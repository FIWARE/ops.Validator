from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from validator_api.models import System, Repo, CookBook, Recipe, Deployment, Image
from validator_api.serializers import SystemSerializer, RepoSerializer, CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self):
        """
        Update image list from local configuration
        """
        from validator_api.clients.docker_client import DockerClient
        for s in DockerClient().list_systems():
            instance = Image()
            instance.name = s.name
            instance.version = s.version
            instance.save()
        return Response(Image.objects.all())


class SystemViewSet(viewsets.ModelViewSet):
    queryset = System.objects.all()
    serializer_class = SystemSerializer
    permission_classes = (permissions.IsAuthenticated,)


class RepoViewSet(viewsets.ModelViewSet):
    queryset = Repo.objects.all()
    serializer_class = RepoSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CookBookViewSet(viewsets.ModelViewSet):
    queryset = CookBook.objects.all()
    serializer_class = CookBookSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @list_route()
    def refresh(self):
        """
        Update cookbook list from repos
        """
        for r in Repo().objects.all():
            if r.type == "svn":
                from validator_api.clients.svn_client import CookbookRepo
                r = CookbookRepo(url=r.location)
                for c in r.list_cookbooks():
                    cb = CookBook()
                    cb.repo = r
                    cb.name = c.name
                    cb.version = c.version
                    cb.save()
            elif r.type == "git":
                from validator_api.clients.repo_browse_client import RepoBrowser
                r = RepoBrowser(r.location)
                for c in r.browse_repository():
                    cb = CookBook()
                    cb.repo = r
                    cb.name = c.name
                    cb.version = c.version
                    cb.save()
            elif r.type == "tgz" or r.type == "zip":
                from validator_api.clients.storage_client import LocalStorage
                r = LocalStorage(r.location)
                for c in r.list_cookbooks():
                    cb = CookBook()
                    cb.repo = r
                    cb.name = c.name
                    cb.version = c.version
                    cb.save()
        return Response(CookBook.objects.all())


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
            from validator_api.clients.chef_client import ChefClient
            cc = ChefClient()
            cc.run_container(data.image)
            res = cc.cookbook_deployment_test(data.recipe.cookbook, data.recipe.name, data.image)
            instance.ok = res['success']
            instance.description = res['result']
            instance.save()
        elif "puppet" == data.system:
            from validator_api.clients.puppet_client import PuppetClient
            pc = PuppetClient()
            pc.run_container(data.image)
            res = pc.cookbook_deployment_test(data.recipe.cookbook, data.recipe.name, data.image)
            instance.ok = res['success']
            instance.description = res['result']
            instance.save()
        return Response(instance)
