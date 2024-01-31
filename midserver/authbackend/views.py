from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.shortcuts import render
from .models import User


# Create your views here.
@method_decorator(csrf_protect, name='dispatch')
class UserSignup(APIView):
    def post(self, request, format=None):
        data = self.request.data
        email = data["email"]
        password = data["password"]
        print(email, password)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'user already exists'})
        else:
            User.objects.create_user(email, password)
            return Response({'response': 'user registration successful'})
        
@method_decorator(csrf_protect, name='dispatch')
class UserLogin(APIView):
    def post(self, request, format=None):
        data = self.request.data
        email = data["email"]
        password = data["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return Response({'success': 'login success'})
        else:
            return Response({'error': 'invalid login'})

class UserLogout(APIView):
    def get(self, request, format=None):
        logout(self.request)
        return Response({'success': 'logout success'})
    
class GetUserEmail(APIView):
    def get(self, request, format=None):
        user = self.request.user
        return Response({'email': user.get_username()})
    
class GetUserSubscriptionStatus(APIView):
    def get(self, request, format=None):
        user = self.request.user
        return Response({'email': user.get_subscription_status})



@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    def get(self, request, format=None):
        return Response(get_token(request))

    
class CheckAuthenticated(APIView):
    def get(self, request, format=None):
        user = self.request.user
        print(user)
        try:
            if user.is_authenticated:
                return Response({'is_authenticated: true'})
            else:
                return Response({'is_authenticated: false'})
        except:
            return Response({'error': 'authentication check error'})
       
