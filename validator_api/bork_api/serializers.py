# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers
from models import Repo, Recipe, CookBook, Deployment, Image


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'name', 'version', 'dockerfile', 'system', 'tag')


class RepoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repo
        fields = ('id', 'type', 'location')


class CookBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = CookBook
        fields = ('id', 'name', 'version', 'repo', 'system')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cookbook', 'system', 'version')


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = ('id', 'recipe', 'image', 'ok', 'description')
