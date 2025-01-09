from rest_framework import serializers
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)
    
    def validate(self, data):
        data['profile_pic'] = data.get('profile_pic', f'https://ui-avatars.com/api/?name={data["username"]}')
        
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
        
    class Meta:
        model = User
        fields = ("id", "username", "password", "email", "profile_pic", "auth_type")

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only = True)
    auth_type = serializers.CharField(read_only = True)
    class Meta:
        model = User
        fields = ("id", "username", "email", "profile_pic", "auth_type")