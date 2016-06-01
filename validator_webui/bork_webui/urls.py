# coding=utf-8
import os

from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.conf.urls import url
from bork_webui import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', render_to_string('index.html')),
]
urlpatterns = static('/', document_root=os.path.join(settings.BASE_DIR, 'static'))
