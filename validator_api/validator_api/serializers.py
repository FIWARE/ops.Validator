# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers
from validator_api.models import System, Repo, Recipe, CookBook, Deployment, Image


class SystemSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = System
        fields = ('id',  'name')


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'name', 'version')


class RepoSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Repo
        fields = ('id', 'type', 'location')


class CookBookSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CookBook
        fields = ('id', 'name', 'version', 'repo')


class RecipeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cookbook')


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Deployment
        fields = ('id', 'recipe', 'image', 'system', 'ok', 'description')
