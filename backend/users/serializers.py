from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import CustomUser, Follow


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('first_name', 'last_name', 'username', 'email')
        model = CustomUser


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ['user', 'following']
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['user', 'following']
            )
        ]

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')

        return data
