from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password

class UserProfileSerializer(serializers.ModelSerializer):
    profilePic = serializers.ImageField(default='defaultProfilePic.jpg')
    class Meta:
        model = UserProfile
        fields = '__all__'

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', None)
        user_permissions_data = validated_data.pop('user_permissions', None)

        user = UserProfile.objects.create(
            firstName=validated_data["firstName"],
            lastName=validated_data["lastName"],
            username=validated_data["username"],
            profilePic=validated_data["profilePic"],
            bio=validated_data["bio"],
            gender=validated_data["gender"],
            contactNumber=validated_data["contactNumber"],
            email=validated_data["email"],
            password=make_password(validated_data["password"])
        )

        if groups_data:
            user.groups.set(groups_data)
        if user_permissions_data:
            user.user_permissions.set(user_permissions_data)

        user.save()
        return user


    def update(self, instance, validated_data):
        print(instance.email)
        instance.firstName = validated_data['firstName']
        instance.lastName = validated_data['lastName']
        instance.username = validated_data['username']
        instance.profilePic = validated_data['profilePic']
        instance.bio = validated_data['bio']
        instance.gender = validated_data['gender']
        instance.contactNumber = validated_data['contactNumber']
        instance.email=validated_data["email"]

        password = validated_data['password']
        if password:
            instance.password=make_password(password)
        instance.save()
        return instance

class PostsSerializer(serializers.ModelSerializer):
    userId = serializers.SlugRelatedField(queryset=UserProfile.objects.all(),slug_field='userId')
    class Meta:
        model = Posts
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    postId = serializers.SlugRelatedField(queryset=Posts.objects.all(),slug_field='postId')
    userId = serializers.SlugRelatedField(queryset=UserProfile.objects.all(),slug_field='userId')
    class Meta:
        model = Likes
        fields = '__all__'

class ConnectionRequestSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(queryset=UserProfile.objects.all(),slug_field='userId')
    destination = serializers.SlugRelatedField(queryset=UserProfile.objects.all(),slug_field='userId')
    class Meta:
        model = ConnectionRequest
        fields = '__all__'

class ConnectionSerializer(serializers.ModelSerializer):
    user1 = serializers.SlugRelatedField(queryset=UserProfile.objects.all(),slug_field='userId')
    user2 = serializers.SlugRelatedField(queryset=UserProfile.objects.all(),slug_field='userId')
    class Meta:
        model = Connections
        fields = '__all__'