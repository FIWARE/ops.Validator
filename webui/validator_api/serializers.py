# coding=utf-8
from __future__ import unicode_literals
from rest_framework import serializers
from validator_api.models import System, Repo, Recipe, CookBook, Deployment, Image


class SystemSerializer(serializers.ModelSerializer):

    class Meta:
        model = System
        fields = ('id',  'name')


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('id', 'name', 'version')

    def refresh(self):
        """
        Update image list from local configuration
        """
        from validator_api.clients.docker_client import DockerClient
        for s in DockerClient().list_systems():
            instance = Image()
            instance.name = s.name
            instance.version = s.version
            instance.save()


class RepoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repo
        fields = ('id', 'type', 'location')


class CookBookSerializer(serializers.ModelSerializer):

    class Meta:
        model = CookBook
        fields = ('id', 'name', 'version', 'repo')

    def refresh(self):
        """
        Update cookbook list from repos
        """
        for r in Repo().objects.all():
            if r.type == "svn":
                from validator_api.clients.svn_client import CookbookRepo
                r = CookbookRepo(url=r.location)
                for c in r.list_cookbooks():
                    cb = CookBook()
                    cb.repo = r
                    cb.name = c.name
                    cb.version = c.version
                    cb.save()
            elif r.type == "git":
                from validator_api.clients.repo_browse_client import RepoBrowser
                r = RepoBrowser(r.location)
                for c in r.browse_repository():
                    cb = CookBook()
                    cb.repo = r
                    cb.name = c.name
                    cb.version = c.version
                    cb.save()
            elif r.type == "tgz":
                from validator_api.clients.storage_client import LocalStorage
                r = LocalStorage(r.location)
                for c in r.list_cookbooks():
                    cb = CookBook()
                    cb.repo = r
                    cb.name = c.name
                    cb.version = c.version
                    cb.save()


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cookbook')


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = ('id', 'recipe', 'image', 'system', 'ok', 'description')

    def deploy(self, data):
        """
        Deploys the given recipe
        """
        instance = Deployment()
        if "chef" == data.system:
            from validator_api.clients.chef_client import ChefClient
            cc = ChefClient()
            cc.run_container(data.image)
            res = cc.cookbook_deployment_test(data.recipe.cookbook, data.recipe.name, data.image)
            instance.ok = res['success']
            instance.description = res['result']
        elif "puppet" == data.system:
            from validator_api.clients.puppet_client import PuppetClient
            pc = PuppetClient()
            pc.run_container(data.image)
            res = pc.cookbook_deployment_test(data.recipe.cookbook, data.recipe.name, data.image)
            instance.ok = res['success']
            instance.description = res['result']
        instance.save()
        return instance
