# coding=utf-8
from validator_api import views
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
admin.autodiscover()

router = DefaultRouter()
router.register(r'images', views.ImageViewSet)
router.register(r'repos', views.RepoViewSet)
router.register(r'cookbooks', views.CookBookViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'deployments', views.DeploymentViewSet)

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^', include('openstack_auth.urls')),
    url(r'^', include(router.urls)),
]
