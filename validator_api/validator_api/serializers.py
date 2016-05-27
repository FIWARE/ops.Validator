# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers
from models import Repo, Recipe, CookBook, Deployment, Image


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'name', 'version', 'dockerfile', 'system')


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
