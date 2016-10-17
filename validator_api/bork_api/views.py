# coding=utf-8
from django.core import serializers
from oslo_config import cfg
from oslo_log import log as logging
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response

from bork_api import filters
from manager import images_cleanup, recipes_cleanup, recipes_add, cookbooks_cleanup, cookbooks_add
from clients.git_client import RepoManager
from clients.docker_client import DockerManager
from clients.storage_client import LocalStorage
from clients.chef_client import ChefClient
from clients.puppet_client import PuppetClient
from clients.murano_client import MuranoClient
from models import CookBook, Recipe, Deployment, Image, Repo
from serializers import CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer, RepoSerializer

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
    filter_backends = (filters.IsOwnerFilterBackend,)
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
            user = request.user.username
            LOG.info("Creating Cookbook from %s" % url)
        else:
            return Response({'detail': 'Insufficient payload'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Download contents to temporary local storage
        # TODO: better github quota management
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
        cb_path, version = m.add_cookbook(path)

        # Generate valid cookbook
        cb = CookBook.objects.get(name=name, user=user)
        if cb:
            LOG.info("Updating Cookbook {} for user {}".format(name, request.user.id))
        else:
            LOG.info("Generating Cookbook {} for user {}".format(name, request.user.id))
            cb = CookBook(user=user, name=name, path=cb_path, version=version, system=system)
            cb.save()
        for r in LocalStorage().list_recipes(cb.path):
            ro = Recipe()
            ro.name = r
            ro.cookbook = cb
            ro.version = RepoManager(user).browse_file(r)
            ro.system = system
            ro.user = user
            ro.save()
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
    filter_backends = (filters.IsOwnerFilterBackend,)
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

    @detail_route(methods=['put', 'get'])
    def github(self, request, pk=None):
        """
        Upload the given cookbook to a remote github repository
        :param request: request data
        :param pk: id of selected cookbook
        :return: operation status
        """
        cb = CookBook.objects.get(pk=pk)
        user = request.user.username
        LOG.info("Uploading cookbook %s to Github" % cb.name)
        RepoManager(user).upload_coobook(cb.path)


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
        recipe = request.data['recipe'] if 'recipe' in request.data.keys() else 'default.rb'
        system = request.data['system'].lower()
        d.cookbook = CookBook.objects.get(name=cookbook)
        d.recipe = Recipe.objects.get(name=recipe, cookbook=d.cookbook)
        d.user = str(request.user)
        # Detect image
        if ":" in image:
            image_name, image_version = image.split(":")
            try:
                i = Image.objects.get(name=image_name.lower(), version=image_version.lower(), system=system)
                image_tag = i.tag
            except Image.DoesNotExist:
                pass
            except Image.MultipleObjectsReturned:
                return Response({'detail': 'Multiple images found for [%s]' % image}, status=status.HTTP_400_BAD_REQUEST)
        try:
            i = Image.objects.get(tag=image_tag)
        except Image.DoesNotExist:
            return Response({'detail': 'Image not found: [%s]' % image}, status=status.HTTP_400_BAD_REQUEST)
        d.image = i

        d.save()
        return Response(s.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['put', 'get'])
    def launch(self, request, pk=None):
        """Ensures launch image is ready for use"""
        d = Deployment.objects.get(pk=pk)
        d.launch, d.launch_log = DockerManager().run_container(d.user, d.recipe.cookbook.name, d.image.tag)
        d.save()
        s = DeploymentSerializer(d)
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def dependencies(self, request, pk=None):
        """Install package and dependencies"""
        d = Deployment.objects.get(pk=pk)
        if "chef" == d.recipe.system:
            res = ChefClient().run_install(d.user, d.recipe.cookbook.name, d.image.tag)
            d.dependencies, d.dependencies_log = (res['success'], res['response'])
        elif "puppet" == d.recipe.system:
            res = PuppetClient().run_install(d.user, d.recipe.cookbook.name, d.image.tag)
            d.dependencies, d.dependencies_log = (res['success'], res['response'])
        elif "murano" == d.recipe.system:
            res = MuranoClient().run_install(d.user, d.recipe.cookbook.name, d.image.tag)
            d.dependencies, d.dependencies_log = (res['success'], res['response'])
        d.save()
        s = DeploymentSerializer(d)
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def syntax(self, request, pk=None):
        """ Syntax checks package """
        d = Deployment.objects.get(pk=pk)
        if "chef" == d.recipe.system:
            res = ChefClient().run_test(d.user, d.recipe.cookbook.name, d.image.tag)
            d.syntax, d.syntax_log = (res['success'], res['response'])
        elif "puppet" == d.recipe.system:
            res = PuppetClient().run_test(d.user, d.recipe.cookbook.name, d.image.tag)
            d.syntax, d.syntax_log = (res['success'], res['response'])
        elif "murano" == d.recipe.system:
            res = MuranoClient().run_test(d.user, d.recipe.cookbook.name, d.image.tag)
            d.syntax, d.syntax_log = (res['success'], res['response'])
        d.save()
        s = DeploymentSerializer(d)
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def deploy(self, request, pk=None):
        """ Deploys package"""
        d = Deployment.objects.get(pk=pk)
        if "chef" == d.recipe.system:
            res = ChefClient().run_deploy(d.user, d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.deployment, d.deployment_log = (res['success'], res['response'])
        elif "puppet" == d.recipe.system:
            res = PuppetClient().run_deploy(d.user, d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.deployment, d.deployment_log = (res['success'], res['response'])
        elif "murano" == d.recipe.system:
            res = MuranoClient().run_deploy(d.user, d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.deployment, d.deployment_log = (res['success'], res['response'])
        d.save()
        s = DeploymentSerializer(d)
        return Response(s.data)

    @detail_route(methods=['put', 'get'])
    def full_deploy(self, request, pk=None):
        d = Deployment.objects.get(pk=pk)
        s = DeploymentSerializer(d)
        if "chef" == d.recipe.system:
            res = ChefClient().cookbook_deployment_test(d.user, d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.ok, d.description = (res['success'], res['response'])
        elif "puppet" == d.recipe.system:
            res = PuppetClient().cookbook_deployment_test(d.user, d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.ok, d.description = (res['success'], res['response'])
        elif "murano" == d.recipe.system:
            res = MuranoClient().blueprint_deployment_test(d.user, d.recipe.cookbook.name, d.recipe.name, d.image.tag)
            d.ok, d.description = (res['success'], res['response'])
        d.save()
        return Response(s.data)


class RepoViewSet(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    filter_backends = (filters.IsOwnerFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """ Generates db repo object """
        user = request.data['user']
        path = request.data['path']
        version = request.data['version']

        res = RepoManager(user).create()
        if not version:
            version = res

        r = Repo(user=user, path=path, version=version)
        r.save()

        rs = RepoSerializer(r)
        return Response(rs.data)

    def delete(self, request, pk=None):
        """Delete db repo object"""
        r = Repo.objects.get(pk=pk)
        user = request.data['user']
        RepoManager(user).delete()
        r.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['put', 'get'])
    def branches(self, request, pk=None):
        """
        Returns current repo branches
        :param request: request data
        :param pk: repo id
        :return: Current repo branches
        """
        user = request.data['user']
        b = RepoManager(user).check_branches()
        bs = serializers.serialize('json', b)
        return Response(bs)

    @detail_route(methods=['put', 'get'])
    def tags(self, request, pk=None):
        """
        Returns current repo tags
        :param request: request data
        :param pk: repo id
        :return: Current repo tags
        """
        user = request.data['user']
        b = RepoManager(user).check_tags()
        bs = serializers.serialize('json', b)
        return Response(bs)

    @detail_route(methods=['put', 'get'])
    def browse(self, request, pk=None):
        """
        Returns current repo contents
        :param request: request data
        :param pk: repo id
        :return: Current repo contents
        """
        user = request.data['user']
        b = RepoManager(user).browse_repository()
        bs = serializers.serialize('json', b)
        return Response(bs)

    @detail_route(methods=['put', 'get'])
    def file(self, request, pk=None):
        """
        Returns current repo file
        :param request: request data
        :param pk: repo id
        :return: Current repo file
        """
        user = request.data['user']
        file = request.data['file']
        b = RepoManager(user).browse_file(file)
        bs = serializers.serialize('json', b)
        return Response(bs)

    @detail_route(methods=['put', 'get'])
    def stats(self, request, pk=None):
        """
        Returns current repo stats
        :param request: request data
        :param pk: repo id
        :return: Current repo stats
        """
        user = request.data['user']
        b = RepoManager(user).statistics()
        bs = serializers.serialize('json', b)
        return Response(bs)

# API Documentation
# from rest_framework.decorators import api_view, renderer_classes
# from rest_framework import response, schemas
# from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
#
#
# @api_view()
# @renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
# def schema_view(request):
#     generator = schemas.SchemaGenerator(title='Bookings API')
#     return response.Response(generator.get_schema(request=request))

