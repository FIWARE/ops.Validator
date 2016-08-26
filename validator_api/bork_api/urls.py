# coding=utf-8
from bork_api import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'images', views.ImageViewSet)
router.register(r'cookbooks', views.CookBookViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'deployments', views.DeploymentViewSet)
router.register(r'repos', views.RepoViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
