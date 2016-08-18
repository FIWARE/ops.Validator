# coding=utf-8

from oslo_config import cfg
from oslo_log import log as logging
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from manager import images_cleanup, recipes_cleanup, recipes_add, cookbooks_cleanup, cookbooks_add
from clients.git_client import RepoManager
from clients.docker_client import DockerManager
from clients.storage_client import LocalStorage
from clients.chef_client import ChefClient
from clients.puppet_client import PuppetClient
from clients.murano_client import MuranoClient
from models import CookBook, Recipe, Deployment, Image
from serializers import CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self, request=None):
        """ Update image list from local configuration """
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
    def generate(self, request=None):
        """ Generate images from local configuration """
        for s in Image.objects.all():
            DockerManager().prepare_image(s.tag)
        return self.list(None)


class CookBookViewSet(viewsets.ModelViewSet):
    queryset = CookBook.objects.all()
    serializer_class = CookBookSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, **kwargs):
        """
        Creates a cookbook db object from a remote url
        :param request: dict with request values
        :param kwargs: additional arguments
        :return: json response with operation status
        """
        # Check data validity
        if 'upload_url' in request.data.keys():
            url = request.data['upload_url']
            user = request.user.get_username()
            LOG.info("Creating Cookbook from %s" % url)
        else:
            return Response({'detail': 'Insufficient payload'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Download contents to temporary local storage
        name, path = LocalStorage().download(url)
        if not name:
            return Response('Error downloading %s. Quota exceeded?' % url,
                            status=status.HTTP_400_BAD_REQUEST)

        # Parse downloaded contents
        system = LocalStorage().find_system(path)
        if not system:
            return Response({'detail': 'No valid cookbook detected for %s' % url},
                            status=status.HTTP_400_BAD_REQUEST)

        # Add valid cookbook to user repo
        m = RepoManager(user)
        version = m.add_cookbook(path)

        # Generate valid cookbook
        LOG.info("Generating Cookbook {} for user {}".format(name, request.user.id))
        cb = CookBook(user=request.user, name=name, path=path, version=version, system=system)
        cb.save()
        cbs = CookBookSerializer(cb)
        resp = Response(cbs.data, status=status.HTTP_201_CREATED)

        return resp

    @list_route()
    def refresh(self, request=None):
        """
        Update cookbook list from local repo
        :param request: request data
        :return: list of db cookbooks
        """
        # Remove current cookbooks
        cookbooks_cleanup()
        # Remove current recipes
        recipes_cleanup()
        # Add local cookbooks
        cookbooks_add()
        return self.list(None)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self, request):
        """
        Update recipe list from local cookbooks
        :param request: request data
        :return: list of db recipes
        """
        # Remove current cookbooks
        cookbooks_cleanup()
        # Remove current recipes
        recipes_cleanup()
        # Add local cookbooks
        cookbooks_add()
        # Add local recipes
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
        d.user = request.user.id
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
            res = cc.run_install(d.recipe.cookbook.name, d.image.tag)
            d.dependencies, d.dependencies_log = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            pc = PuppetClient()
            res = pc.run_install(d.recipe.cookbook.name, d.image.tag)
            d.dependencies, d.dependencies_log = (res['success'], res['result'])
        elif "murano" == d.recipe.system:
            mc = MuranoClient()
            res = mc.run_install(d.recipe.cookbook.name, d.image.tag)
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
            res = cc.run_test(d.recipe.cookbook.name, d.image.tag)
            d.syntax, d.syntax_log = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            pc = PuppetClient()
            res = pc.run_test(d.recipe.cookbook.name, d.image.tag)
            d.syntax, d.syntax_log = (res['success'], res['result'])
        elif "murano" == d.recipe.system:
            mc = MuranoClient()
            res = mc.run_test(d.recipe.cookbook.name, d.image.tag)
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
            res = cc.run_deploy(d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.deployment, d.deployment_log = (res['success'], res['result'])
        elif "puppet" == d.recipe.system:
            pc = PuppetClient()
            res = pc.run_deploy(d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.deployment, d.deployment_log = (res['success'], res['result'])
        elif "murano" == d.recipe.system:
            mc = MuranoClient()
            res = mc.run_deploy(d.recipe.cookbook.name, d.recipe.name, d.image.tag)
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
        elif "murano" == d.recipe.system:
            res = MuranoClient().blueprint_deployment_test(d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.ok, d.description = (res['success'], res['result'])
        d.save()
        return Response(s.data)


