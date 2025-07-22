from rest_framework import serializers
from .models import Property, CustomUser, SearchHistory
from django.contrib.auth.hashers import make_password

class PropertySerializer(serializers.Serializer):
    id = serializers.CharField()
    description = serializers.CharField()
    location = serializers.CharField()
    bhk = serializers.IntegerField()
    price = serializers.IntegerField()

    def create(self, validated_data):
        from .models import Property
        return Property.objects.create(**validated_data)

class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = '__all__'

class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    filters = serializers.DictField(required=False)

class RecommendSerializer(serializers.Serializer):
    salary = serializers.IntegerField()
    married_status = serializers.CharField()
    bhk = serializers.IntegerField()
    location = serializers.CharField()


class PropertyInterestCreateSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    property_id = serializers.IntegerField()
    watch_time = serializers.IntegerField()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(RegisterSerializer, self).create(validated_data)
