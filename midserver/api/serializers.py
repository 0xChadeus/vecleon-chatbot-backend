from rest_framework import serializers
from .models import CharacterCard, WorldCard, Chat
from django.contrib.postgres.fields import ArrayField


class CharacterSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=10000)
    first_message = serializers.CharField(max_length=10000)
    personality_summary = serializers.CharField(max_length=10000)
    scenario = serializers.CharField(max_length=10000)
    src = serializers.CharField(max_length=500)

    def create(self, validated_data):
        """
        Create and return a new `CharacterCard` instance, given the validated data.
        """
        return CharacterCard.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `CharacterCard` instance, given the validated data.
        """
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.first_message = validated_data.get('first_message', instance.first_message)
        instance.personality_summary = validated_data.get('personality_summary', instance.personality_summary)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.src = validated_data.get('src', instance.src)
        instance.save()
        return instance
    

class WorldSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=10000)
    scenario = serializers.CharField(max_length=10000)
    src = serializers.CharField(max_length=500)

    def create(self, validated_data):
        """
        Create and return a new `WorldCard` instance, given the validated data.
        """
        return WorldCard.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `WorldCard` instance, given the validated data.
        """
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.first_message = validated_data.get('first_message', instance.first_message)
        instance.personality_summary = validated_data.get('personality_summary', instance.personality_summary)
        instance.scenario = validated_data.get('scenario', instance.scenario)
        instance.src = validated_data.get('src', instance.src)
        instance.save()
        return instance


class ChatSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField(max_length=50)
    msg_history = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField()
            )
        )
    character_key = CharacterSerializer(read_only=True)
    user_name = serializers.CharField(max_length=250)
    user_img = serializers.CharField(max_length=500)

    def create(self, validated_data):
        """
        Create and return a new `Chat` instance, given the validated data.
        """
        return Chat.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Chat` instance, given the validated data.
        """
        instance.id = validated_data.get('id', instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.msg_history = validated_data.get('msg_history', instance.msg_history)
        instance.character_key = validated_data.get('character_key', instance.character_key)
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.user_img = validated_data.get('user_img', instance.user_img)
        instance.save()
        return instance
    
