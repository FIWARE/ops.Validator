import os
import logging
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from models import Repo, CookBook, Recipe, Deployment, Image
from serializers import RepoSerializer, CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer
from validator_api import settings
from validator_api.clients.storage_client import LocalStorage


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    #permission_classes = (permissions.IsAuthenticated,)

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
    #permission_classes = (permissions.IsAuthenticated,)


class CookBookViewSet(viewsets.ModelViewSet):
    queryset = CookBook.objects.all()
    serializer_class = CookBookSerializer
    #permission_classes = (permissions.IsAuthenticated,)

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
                cookbooks_add(cookbooks, r)
            elif r.type == "git":
                from clients.repo_browse_client import GITRepo
                logging.info("Downloading Cookbooks from %s" % r.location)
                repo = GITRepo(r.location)
                repo.checkout()
                cookbooks_add(cookbooks, r)
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


def cookbooks_add(cookbooks, r):
    """
    Add local cookbooks to db
    :param cookbooks: current cookbooks
    :param r: current repository
    :return:
    """
    l = LocalStorage(settings.LOCAL_STORAGE)
    for c in l.list_cookbooks():
        if c not in cookbooks:
            logging.info("Adding cookbook %s" % c)
            cb = CookBook()
            cb.repo = r
            cb.name = c
            cb.path = os.path.join(settings.LOCAL_STORAGE, c)
            cb.save()
            cookbooks.add(c)


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
            ro.save()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    #permission_classes = (permissions.IsAuthenticated,)

    def refresh(self, request):
        """
        Update recipe list from local cookbooks
        """
        recipes_cleanup()
        recipes_add()


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
    #permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        Deploys the given recipe
        """
        instance = Deployment()
        image_name, image_version = request.data['image'].split(":")
        try:
            image = Image.objects.get(name=image_name.lower(), version=image_version.lower(), system=request.data['system'].lower())
            image_path = image.dockerfile
        except Image.DoesNotExist:
            return Response({'detail': 'Image not found %s' % request.data['image']}, status=status.HTTP_404_NOT_FOUND)
        except Image.MultipleObjectsReturned:
            return Response('Multiple images found %s' % request.data['image'], status=status.HTTP_404_NOT_FOUND)
        if "chef" == request.data['system'].lower():
            from clients.chef_client import ChefClient
            res = ChefClient(url=settings.DOCKER_URL).cookbook_deployment_test(request.data.cookbook, None, image_path)
            instance.ok, instance.description = (res['success'], res['result'])
            instance.save()
        elif "puppet" == request.data.system.lower():
            from clients.puppet_client import PuppetClient
            res = PuppetClient(url=settings.DOCKER_URL).cookbook_deployment_test(request.data.cookbook, None, image_path)
            instance.ok, instance.description = (res['success'], res['result'])
            instance.save()
        return Response(instance, status=status.HTTP_201_CREATED)
