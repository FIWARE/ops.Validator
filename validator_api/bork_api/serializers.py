# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers
from models import Recipe, CookBook, Deployment, Image


class ImageSerializer(serializers.ModelSerializer):
    """ Serializer for a Image Object """

    class Meta:
        model = Image
        fields = ('id', 'name', 'version', 'dockerfile', 'system', 'tag')


class CookBookSerializer(serializers.ModelSerializer):
    """ Serializer for a Cookbook Object """

    class Meta:
        model = CookBook
        fields = ('id', 'name', 'version', 'user', 'system')


class RecipeSerializer(serializers.ModelSerializer):
    """ Serializer for a Recipe Object """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cookbook', 'system', 'version')


class DeploymentSerializer(serializers.ModelSerializer):
    """ Serializer for a Deployment Object """

    class Meta:
        model = Deployment
        fields = ('id', 'image', 'user', 'recipe', 'launch', 'dependencies', 'dependencies_log', 'syntax', 'syntax_log', 'deployment', 'deployment_log', 'ok', 'description')
