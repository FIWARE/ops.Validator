# coding=utf-8
from django.views.generic import TemplateView
from django.conf.urls import url


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='Index'),
]
