from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.core.mail import send_mail
from api.models import CharacterCard 
from .models import User
from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json

class TestEmail(APIView):
    def post(self, request, format=None):
        data = self.request.data
        email = self.request.user
        html_message = render_to_string('test_email.html', {'context': 'values'})
        plain_message = strip_tags(html_message)
        send_mail(
                'Vecleon Test',
                'test test test',
                'noreply@vecleon.com',
                [email],
                html_message=html_message, 
                fail_silently=False,
                )
        return Response({'response': 'email sent'})

@method_decorator(csrf_protect, name='dispatch')
class UserSignup(APIView):
    def create_defaults(self, user):
        templates_folder = 'templates/'
        default_chars = ["john", "chloe", "alexander"]
        for char in default_chars:
            with open(templates_folder + char + '.json') as f:
                d = json.load(f)
                name = d["data"]["name"]
                description = d["data"]["description"]
                personality_summary = d["data"]["personality"]
                scenario = d['data']['scenario']
                src = d['data']['src']
                CharacterCard.objects.create(name=name, description=description, personality_summary=personality_summary, scenario=scenario, src=src, user_key=user)


    def post(self, request, format=None):
        data = self.request.data
        email = data["email"]
        password = data["password"]
        if User.objects.filter(email=email).exists():
            return Response({'error': 'user already exists'})
        else:
            user = User.objects.create_user(email, password)
            self.create_defaults(user)
            html_message = render_to_string('welcome_email.html', {'context': 'values'})
            plain_message = strip_tags(html_message)
            send_mail(
                    'Welcome to Vecleon',
                    'Welcome to Vecleon! Your account has been created. Please login to continue. \n\n Yours sincerely, The Vecleon Team',
                    'noreply@vecleon.com',
                    [email],
                    html_message=html_message,
                    fail_silently=False
                    )
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

class ChangeUserPassword(APIView):
    def post(self, request, format=None):
        data = self.request.data
        user = self.request.user
        current_password = data["current_password"]
        if not user.check_password(current_password):
            return Response({'error': 'invalid current password'})
        new_password = data["new_password"]
        if current_password == new_password:
            return Response({'error': 'new password must be different from current password'})
        confirm_new_password = data["confirm_new_password"]
        if new_password != confirm_new_password:
            return Response({'error': 'new passwords do not match'})
        user.set_password(new_password)
        user.save()
        return Response({'success': 'Password changed successfully'})
    
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
        try:
            if user.is_authenticated:
                return Response({'is_authenticated: true'})
            else:
                return Response({'is_authenticated: false'})
        except:
            return Response({'error': 'authentication check error'})
       
