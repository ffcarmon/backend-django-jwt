from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['POST'])
def login(request):
    # Retrieve the user by their username or return a 404 error if not found
    user_instance = get_object_or_404(User, username=request.data.get('username'))
    
    # Check if the provided password is valid
    if not user_instance.check_password(request.data.get('password')):
        return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Retrieve or create a token for the authenticated user
    user_token, token_created = Token.objects.get_or_create(user=user_instance)
    
    # Serialize the user instance to return user details
    user_serializer = UserSerializer(instance=user_instance)

    # Return the token and user details
    return Response({
        'token': user_token.key,
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    # Deserialize the incoming data using UserSerializer
    user_serializer = UserSerializer(data=request.data)
    
    if user_serializer.is_valid():
        # Save the new user instance
        new_user = user_serializer.save()

        # Set the user's password securely
        new_user.set_password(user_serializer.validated_data['password'])
        new_user.save()

        # Generate a token for the newly created user
        user_token = Token.objects.create(user=new_user)

        # Respond with the token and user details
        return Response({
            'token': user_token.key,
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)

    # Return validation errors if the data is invalid
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    # Return a message confirming the logged-in user
    username = request.user.username
    return Response(f"You are logged in as {username}", 
                     status=status.HTTP_200_OK)