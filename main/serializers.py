from rest_framework import serializers

from .models import TestModel


class EnsemblCdsSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.CharField(max_length=50)
    )


class EnsemblVepSerializer(serializers.Serializer):
    hgvs_notations = serializers.ListField(
        child=serializers.CharField(max_length=100)
    )


class TestModelSerializer(serializers.ModelSerializer):
    class Meta():
        model = TestModel
        fields = ('id', 'name', 'description')
