from rest_framework import serializers
from .models import Node
from .utilities import findParent
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
class NodeSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField('parentMethod')
    userName = serializers.SerializerMethodField('userMethod')
    def userMethod(self, obj):
        return obj.user.username
    def parentMethod(self,obj):
        return findParent(obj.number)

    class Meta:
        model = Node
        fields = ['number', 'userName', 'child1', 'child1Value', 'child2', 'child2Value','childrenMissing','parent']
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('userMethod')
    def userMethod(self, obj):
        return obj.username
    class Meta:
        model = get_user_model()
        fields = ['name']