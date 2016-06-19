# coding=utf-8

import os
from oslo_config import cfg
from oslo_log import log as logging
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from models import Repo, CookBook, Recipe, Deployment, Image
from serializers import RepoSerializer, CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer
from clients.storage_client import LocalStorage
from clients.chef_client import ChefClient
from clients.puppet_client import PuppetClient
from clients.docker_client import DockerManager

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self, request=None):
        """
        Update image list from local configuration
        """
        LOG.info("Refreshing image db")
        images_cleanup()
        for s in DockerManager().list_images():
            instance = Image()
            instance.name = s['name']
            instance.version = s['version']
            instance.dockerfile = s['dockerfile']
            instance.system = s['system']
            instance.tag = s['tag']
            instance.save()
        return self.list(None)

    @list_route()
    def generate(self, request):
        """
        Update image list from local configuration
        """
        from clients.docker_client import DockerManager
        for s in Image.objects.all():
            DockerManager().generate_image(s.dockerfile)
        return self.list(None)


class RepoViewSet(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CookBookViewSet(viewsets.ModelViewSet):
    queryset = CookBook.objects.all()
    serializer_class = CookBookSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self, request=None):
        """
        Update cookbook list from repos
        """
        cookbooks_cleanup()
        recipes_cleanup()
        cookbooks = set()
        for r in Repo.objects.all():
            if r.type == "svn":
                LOG.info("Downloading Cookbooks from %s" % r.location)
                from clients.svn_client import SVNRepo
                repo = SVNRepo(url=r.location, user=r.user, pwd=r.password)
                repo.download_cookbooks()
                cookbooks_add(cookbooks, r, version=repo.version)
            elif r.type == "git":
                from clients.repo_browse_client import GITRepo
                LOG.info("Downloading Cookbooks from %s" % r.location)
                repo = GITRepo(r.location)
                repo.checkout()
                cookbooks_add(cookbooks, r, version=repo.version)
        return self.list(None)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self, request):
        """
        Update recipe list from local cookbooks
        """
        recipes_cleanup()
        recipes_add()
        return self.list(None)


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """ Generates db deployment object """
        d = Deployment()
        s = DeploymentSerializer(d)
        image = request.data['image'].lower()
        image_tag = image
        cookbook = request.data['cookbook']
        recipe = request.data['recipe'] or 'default.rb'
        system = request.data['system'].lower()
        d.cookbook = CookBook.objects.get(name=cookbook)
        d.recipe = Recipe.objects.get(name=recipe, cookbook=d.cookbook)
        # Detect image
        if ":" in image:
            image_name, image_version = image.split(":")
            try:
                i = Image.objects.get(name=image_name.lower(), version=image_version.lower(), system=system)
                image_tag = i.tag
            except Image.DoesNotExist:
                pass
            except Image.MultipleObjectsReturned:
                return Response({'detail': 'Multiple images found %s' % image}, status=status.HTTP_400_BAD_REQUEST)
        try:
            i = Image.objects.get(tag=image_tag)
        except Image.DoesNotExist:
            return Response({'detail': 'Image not found %s' % image}, status=status.HTTP_400_BAD_REQUEST)
        d.image = i

        d.save()
        return Response(s.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['put', 'get'])
    def launch(self, request, pk=None):
        """Ensures launch image is ready for use"""
        d = Deployment.objects.get(pk=pk)
        s = DeploymentSerializer(d)
        d.launch = DockerManager().prepare_image(d.image.tag)
        d.save()
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def dependencies(self, request, pk=None):
        """Install package and dependencies"""
        d = Deployment.objects.get(pk=pk)
        s = DeploymentSerializer(d)
        if "chef" == d.recipe.system:
            cc = ChefClient()
            res = cc.run_install(d.recipe.cookbook.name)
            d.dependencies, d.dependencies_log = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            pc = PuppetClient()
            res = pc.run_install(d.recipe.cookbook.name)
            d.dependencies, d.dependencies_log = (res['success'], res['result'])
        d.save()
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def syntax(self, request, pk=None):
        """ Syntax checks package """
        d = Deployment.objects.get(pk=pk)
        s = DeploymentSerializer(d)
        if "chef" == d.recipe.system:
            cc = ChefClient()
            res = cc.run_test(d.recipe.cookbook.name)
            d.syntax, d.syntax_log = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            pc = PuppetClient()
            res = pc.run_test(d.recipe.cookbook.name)
            d.syntax, d.syntax_log = (res['success'], res['result'])
        d.save()
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def deploy(self, request, pk=None):
        """ Deploys package"""
        d = Deployment.objects.get(pk=pk)
        s = DeploymentSerializer(d)
        if "chef" == d.recipe.system:
            cc = ChefClient()
            res = cc.run_deploy(d.recipe.name)
            d.deployment, d.deployment_log = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            pc = PuppetClient()
            res = pc.run_deploy(d.recipe.name)
            d.deployment, d.deployment_log = (res['success'], res['result'])
        d.save()
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def full_deploy(self, request, pk=None):
        d = Deployment.objects.get(pk=pk)
        s = DeploymentSerializer(d)
        if "chef" == d.recipe.system:
            res = ChefClient().cookbook_deployment_test(d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.ok, d.description = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            res = PuppetClient().cookbook_deployment_test(d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.ok, d.description = (res['success'], res['result'])
        d.save()
        return Response(s.data)


def cookbooks_cleanup():
    """ Cleanup previously downloaded cookbooks """
    LOG.info("Cleanup old Cookbooks")
    CookBook.objects.all().delete()
    LocalStorage().reset()


def images_cleanup():
    """ Cleanup image db"""
    LOG.debug("Cleanup old Images")
    Image.objects.all().delete()


def recipes_cleanup():
    """ Cleanup previous recipes """
    LOG.info("Cleanup old Recipes")
    Recipe.objects.all().delete()


def deployments_cleanup():
    """ Cleanup previous deployments """
    LOG.info("Cleanup old Deployments")
    Deployment.objects.all().delete()


def cookbooks_add(cookbooks, repo, version='Unknown'):
    """
    Add local cookbooks to db
    :param cookbooks: current cookbooks
    :param repo: current repository
    :return:
    """
    l = LocalStorage()
    for c in l.list_cookbooks():
        if c['name'] not in cookbooks:
            LOG.info("Adding cookbook %s" % c['name'])
            cb = CookBook()
            cb.repo = repo
            cb.name = c['name']
            cb.system = c['system']
            cb.version = version
            cb.path = os.path.join(l.path, c['name'])
            cb.save()
            cookbooks.add(c['name'])


def recipes_add():
    """ Add detected recipes based on local cookbooks """
    l = LocalStorage()
    for cb in CookBook.objects.all():
        for r in l.list_recipes(cb.path):
            ro = Recipe()
            ro.name = r
            ro.cookbook = cb
            ro.version = cb.version
            ro.system = cb.system
            ro.save()
