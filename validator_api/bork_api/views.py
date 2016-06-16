import os
import logging
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from models import Repo, CookBook, Recipe, Deployment, Image
from serializers import RepoSerializer, CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer
from bork_api import settings
from bork_api.clients.storage_client import LocalStorage
from clients.chef_client import ChefClient
from clients.puppet_client import PuppetClient


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self, request):
        """
        Update image list from local configuration
        """
        Image.objects.all().delete()
        from clients.docker_client import DockerManager
        for s in DockerManager().list_systems():
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
    def refresh(self, request):
        """
        Update cookbook list from repos
        """
        cookbooks_cleanup()
        cookbooks = set()
        for r in Repo.objects.all():
            if r.type == "svn":
                logging.info("Downloading Cookbooks from %s" % r.location)
                from clients.svn_client import SVNRepo
                repo = SVNRepo(url=r.location, user=r.user, pwd=r.password)
                repo.download_cookbooks()
                cookbooks_add(cookbooks, r, version=repo.version)
            elif r.type == "git":
                from clients.repo_browse_client import GITRepo
                logging.info("Downloading Cookbooks from %s" % r.location)
                repo = GITRepo(r.location)
                repo.checkout()
                cookbooks_add(cookbooks, r, version=repo.version)
        return self.list(None)


def cookbooks_cleanup():
    """
    Cleanup previously downloaded cookbooks
    :return:
    """
    logging.info("Cleanup old Cookbooks in %s" % settings.LOCAL_STORAGE)
    CookBook.objects.all().delete()
    if os.path.exists(settings.LOCAL_STORAGE):
        import shutil
        shutil.rmtree(settings.LOCAL_STORAGE)
        os.mkdir(settings.LOCAL_STORAGE)


def cookbooks_add(cookbooks, r, version='Unknown'):
    """
    Add local cookbooks to db
    :param cookbooks: current cookbooks
    :param r: current repository
    :return:
    """
    l = LocalStorage(settings.LOCAL_STORAGE)
    for c in l.list_cookbooks():
        if c['name'] not in cookbooks:
            logging.info("Adding cookbook %s" % c['name'])
            cb = CookBook()
            cb.repo = r
            cb.name = c['name']
            cb.system = c['system']
            cb.version = version
            cb.path = os.path.join(settings.LOCAL_STORAGE, c['name'])
            cb.save()
            cookbooks.add(c['name'])


def recipes_cleanup():
    """
    Cleanup previous recipes
    :return:
    """
    Recipe.objects.all().delete()


def recipes_add():
    """
     Add detected recipes based on local cookbooks
    """
    l = LocalStorage(settings.LOCAL_STORAGE)
    for cb in CookBook.objects.all():
        for r in l.list_recipes(cb.path):
            ro = Recipe()
            ro.name = r
            ro.cookbook = cb
            ro.version = cb.version
            ro.system = cb.system
            ro.save()


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
        """
        Deploys the given recipe
        """
        import traceback
        instance = Deployment()
        try:
            image = request.data['image'].lower()
            image_tag = image
            cookbook = request.data['cookbook']
            recipe = request.data['recipe'] or 'default.rb'
            system = request.data['system'].lower()

            instance.cookbook = CookBook.objects.get(name=cookbook)
            instance.recipe = Recipe.objects.get(name=recipe, cookbook=instance.cookbook)
            # Prepare image
            from clients.docker_client import DockerManager
            if ":" in image:
                image_name, image_version = image.split(":")
                try:
                    image = Image.objects.get(name=image_name.lower(), version=image_version.lower(), system=system)
                    image_tag = image.tag
                except Image.DoesNotExist:
                    try:
                        DockerManager().prepare_image(image_tag)
                    except Image.DoesNotExist:
                        return Response({'detail': 'Image not found %s' % image}, status=status.HTTP_404_NOT_FOUND)
                except Image.MultipleObjectsReturned:
                    return Response('Multiple images found %s' % image, status=status.HTTP_404_NOT_FOUND)
            instance.save()
        except Exception:
            traceback.print_exc()
        # # Deploy image
        # if "chef" == system:
        #     res = ChefClient(url=settings.DOCKER_URL).cookbook_deployment_test(cookbook, recipe, image_tag)
        #     instance.ok, instance.description = (res['success'], res['result'])
        #     instance.save()
        # elif "puppet" == system:
        #     res = PuppetClient(url=settings.DOCKER_URL).cookbook_deployment_test(cookbook, recipe, image_tag)
        #     instance.ok, instance.description = (res['success'], res['result'])
        #     instance.save()
        return Response(instance, status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'])
    def dependencies(self, request, pk=None):
        print(pk)
        d = Deployment.objects.get(pk=pk)
        if "chef" == d.system.name:
            cc = ChefClient(url=settings.DOCKER_URL)
            res = cc.run_install(d.cookbook.name)
            d.dependencies, d.dependencies_log = (res['success'], res['result'])
        elif "puppet" == d.system.name:
            pc = PuppetClient(url=settings.DOCKER_URL)
            res = pc.run_install(d.cookbook.name)
            d.dependencies, d.dependencies_log = (res['success'], res['result'])
        d.save()
        return Response(d)

    @detail_route(methods=['get'])
    def syntax(self, request, pk=None):
        d = Deployment.objects.get(pk=pk)
        if "chef" == d.system.name:
            cc = ChefClient(url=settings.DOCKER_URL)
            res = cc.run_test(d.cookbook.name)
            d.syntax, d.syntax_log = (res['success'], res['result'])
        elif "puppet" == d.system.name:
            pc = PuppetClient(url=settings.DOCKER_URL)
            res = pc.run_test(d.cookbook.name)
            d.syntax, d.syntax_log = (res['success'], res['result'])
        d.save()
        return Response(d)

    @detail_route(methods=['get'])
    def deploy(self, request, pk=None):
        d = Deployment.objects.get(pk=pk)
        if "chef" == d.system.name:
            cc = ChefClient(url=settings.DOCKER_URL)
            res = cc.run_deploy(d.cookbook.name)
            d.deployment, d.deployment_log = (res['success'], res['result'])
        elif "puppet" == d.system.name:
            pc = PuppetClient(url=settings.DOCKER_URL)
            res = pc.run_deploy(d.cookbook.name)
            d.deployment, d.deployment_log = (res['success'], res['result'])
        d.save()
        return Response(d)
