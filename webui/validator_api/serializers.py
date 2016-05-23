# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers
from validator_api.models import System, Repo, Recipe, CookBook, Deployment


class SystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = System
        fields = ('id', 'name', 'version')


class RepoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repo
        fields = ('id', 'type', 'location')


class CookBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = CookBook
        fields = ('id', 'name', 'version', 'repo')


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cookbook')


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = ('id', 'recipe', 'system', 'ok', 'description')