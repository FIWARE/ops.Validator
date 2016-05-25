from rest_framework import viewsets
from rest_framework import permissions
from validator_api.models import System, Repo, CookBook, Recipe, Deployment, Image
from validator_api.serializers import SystemSerializer, RepoSerializer, CookBookSerializer, RecipeSerializer, DeploymentSerializer, ImageSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.IsAuthenticated,)


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


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.all()
    serializer_class = DeploymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

