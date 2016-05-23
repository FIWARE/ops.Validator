# coding=utf-8
from validator_api import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'systems', views.SystemViewSet)
router.register(r'repos', views.RepoViewSet)
router.register(r'cookbooks', views.CookBookViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'deployments', views.DeploymentViewSet)

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^', include(router.urls)),
]
