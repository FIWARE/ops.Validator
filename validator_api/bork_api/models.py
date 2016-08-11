# coding=utf-8
from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.db import models

SYSTEMS = (
    ("chef", "chef"),
    ("puppet", "puppet"),
    ("murano", "murano"),
)


class Image(models.Model):
    """
    A docker OS image identified by OS name and version
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False, default='Unknown')
    version = models.CharField(max_length=50, blank=False, default='Unknown')
    dockerfile = models.CharField(max_length=255, blank=False, default='Unknown')
    system = models.CharField(max_length=6, choices=SYSTEMS, default="chef")
    tag = models.CharField(max_length=50, blank=False, default='Unknown')

    def __unicode__(self):
        return "%s:%s" % (self.name, self.version)


class CookBook(models.Model):
    """
    A collection of cookbooks belonging to a user, identified by name and version
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False, default='Unknown')
    version = models.CharField(max_length=50, blank=False, default='Unknown')
    user = models.ForeignKey(User, blank=True, null=True)
    path = models.CharField(max_length=255, blank=False, default='/tmp/cookbooks')
    system = models.CharField(max_length=6, choices=SYSTEMS, default="chef")

    def __unicode__(self):
        return self.name


class Recipe(models.Model):
    """
    A recipe belonging to a given cookbook, identified by name
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, blank=False, default='Unknown')
    cookbook = models.ForeignKey(CookBook, blank=True, null=True)

    def __unicode__(self):
        return self.name


class Deployment(models.Model):
    """
    The deployment of a recipe in a system image
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, blank=True, null=True)
    recipe = models.ForeignKey(Recipe, blank=True, null=True)
    image = models.ForeignKey(Image, blank=True, null=True)
    launch = models.NullBooleanField(blank=True, null=True)
    dependencies = models.NullBooleanField(blank=True, null=True)
    dependencies_log = models.TextField(blank=True, null=True)
    syntax = models.NullBooleanField(blank=True, null=True)
    syntax_log = models.TextField(blank=True, null=True)
    deployment = models.NullBooleanField(blank=True, null=True)
    deployment_log = models.TextField(blank=True, null=True)
    ok = models.NullBooleanField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)