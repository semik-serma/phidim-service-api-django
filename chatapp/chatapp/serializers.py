from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(**serializer.validated_data)
        return Response({'message': 'User created successfully'})
    return Response(serializer.errors, status=400)