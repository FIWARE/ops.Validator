import os
import logging
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from models import Repo, CookBook, Recipe, Deployment, Image
from serializers import RepoSerializer, CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer
from validator_api import settings


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
        from clients.docker_client import DockerClient
        for s in DockerClient().list_systems():
            instance = Image()
            instance.name = s['name']
            instance.version = s['version']
            instance.save()
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
        # Cleanup phase
        logging.info("Cleanup old Cookbooks in %s" % settings.LOCAL_STORAGE)
        cookbooks = set()
        CookBook.objects.all().delete()
        if os.path.exists(settings.LOCAL_STORAGE):
            import shutil
            shutil.rmtree(settings.LOCAL_STORAGE)
            os.mkdir(settings.LOCAL_STORAGE)
        for r in Repo.objects.all():
            if r.type == "svn":
                logging.info("Downloading Cookbooks from %s" % r.location)
                from clients.svn_client import SVNRepo
                repo = SVNRepo(url=r.location, user=r.user, pwd=r.password)
                repo.download_cookbooks()
                generate_cookbooks(cookbooks, r)
            elif r.type == "git":
                from clients.repo_browse_client import GITRepo
                logging.info("Downloading Cookbooks from %s" % r.location)
                repo = GITRepo(r.location)
                repo.checkout()
                generate_cookbooks(cookbooks, r)
        return self.list(None)


def generate_cookbooks(cookbooks, r):
    from clients.storage_client import LocalStorage
    l = LocalStorage(settings.LOCAL_STORAGE)
    for c in l.list_cookbooks():
        if c not in cookbooks:
            logging.info("Adding cookbook %s" % c)
            cb = CookBook()
            cb.repo = r
            cb.name = c
            cb.save()
            cookbooks.add(c)
            for r in l.list_recipes(c):
                ro = Recipe()
                ro.name = r
                ro.cookbook = cb
                ro.save()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @detail_route(methods=['post'])
    def deploy(self, data):
        """
        Deploys the given recipe
        """
        instance = Deployment()
        if "chef" == data.system:
            from clients.chef_client import ChefClient
            cc = ChefClient()
            cc.run_container(data.image)
            res = cc.cookbook_deployment_test(data.recipe.cookbook, data.recipe.name, data.image)
            instance.ok = res['success']
            instance.description = res['result']
            instance.save()
        elif "puppet" == data.system:
            from clients.puppet_client import PuppetClient
            pc = PuppetClient()
            pc.run_container(data.image)
            res = pc.cookbook_deployment_test(data.recipe.cookbook, data.recipe.name, data.image)
            instance.ok = res['success']
            instance.description = res['result']
            instance.save()
        return Response(instance)
