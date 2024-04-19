from django.shortcuts import render
import json
import os
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CharacterCard, WorldCard, Chat
from authbackend.models import User
from rest_framework.decorators import api_view
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import CharacterSerializer, WorldSerializer, ChatSerializer
import stripe
import uuid
stripe.api_key = "sk_test_51O0YIeLcAPiyHOsMCUTkBhuJF5iaza6JRQcGoUxGnQmDznH3TmxKd2pQUHxPyGdzKRSwSef2lzWgMU1BvvBviY8u00fTjWc0Ju"


class CreateChat(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data
        name = data["name"]
        character_id = data["character_id"]
        character = CharacterCard.objects.get(id=character_id)  
        Chat.objects.create(name=name, msg_history=[], 
                                   user_key=user, 
                                   character_key=character)
        return Response({"response": "chat created"})
 
class UpdateChat(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data
        mes_id = str(uuid.uuid4())
        chat_id = data["chat_id"]
        message = data["msg"]
        images = data["images"]
        audio = data["audio"]
        role = data["role"]
        chat = Chat.objects.get(id=chat_id)
        chat.msg_history.append([role, message, images, audio, mes_id])
        chat.save()
        return Response({"response": "chat updated"})
    
class UpdateChatNSFW(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data
        chat_id = data["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        chat.nsfw = data["nsfw"]
        chat.save()
        return Response({"response": "chat nsfw status updated"})

    
class DeleteChat(APIView):
    def delete(self, request, format=None):
        user = self.request.user
        data = self.request.data
        chat_id = data["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        chat.delete()
        return Response({"response": "chat deleted"})
    
class GetChats(APIView):
    def get(self, request, format=None):
        user = self.request.user
        chats = user.chat_set.all()
        chats_serial = ChatSerializer(chats, many=True)
        return Response(chats_serial.data)
    
class GetChat(APIView):
    def put(self, request, format=None):
        user = self.request.user
        chat_id = self.request.data["chat_id"]
        chat = Chat.objects.get(id=chat_id)
        chat_serial = ChatSerializer(chat)
        return Response(chat_serial.data)








class CreateCharacter(APIView):
    def post(self, request, format=None):
        user = self.request.user
        if user.stripe_customer_id == '' or user.stripe_subscription_id == '' or user.subscription_is_active == False:
            return Response({"response": "user does not have an active subscription or stripe customer ID"})
        elif user.charactercard_set.all().count() >= 20 and user.subscription_package == "Standard":
            return Response({"response": "user is subscribed to the standard package and tried to create more than 20 active characters. User must delete a character first before proceeding."})

        data = self.request.data
        name = data["name"]
        description = data["description"]
        personality_summary = data["personality_summary"]
        scenario = data["scenario"]
        src = data["src"]
        CharacterCard.objects.create(name=name, description=description, 
                                    personality_summary=personality_summary,
                                     scenario=scenario, src=src, user_key=user)
        return Response({"response": "character created"})

class UpdateCharacter(APIView):
    def patch(self, request, format=None):
        user = self.request.user
        if user.stripe_customer_id == '' or user.stripe_subscription_id == '' or user.subscription_is_active == False:
            return Response({"response": "user does not have an active subscription or stripe customer ID"})
        data = self.request.data
        character_id = data['id']
        name = data["name"]
        description = data["description"]
        personality_summary = data["personality_summary"]
        scenario = data["scenario"]
        src = data['src']
        character = CharacterCard.objects.filter(id=character_id)  
        character.update(name=name, description=description, 
                        personality_summary=personality_summary,
                        src=src, scenario=scenario)
        return Response({"response": "character updated"})
    
class DeleteCharacter(APIView):
    def delete(self, request, format=None):
        user = self.request.user
        data = self.request.data
        character_id = data['id']
        character = CharacterCard.objects.filter(id=character_id)  
        character.delete()
        return Response({"response": "character deleted"})
    
class GetCharacters(APIView):
    def get(self, request, format=None):
        user = self.request.user
        characters = user.charactercard_set.all()
        char_serial = CharacterSerializer(characters, many=True)
        return Response(char_serial.data)

class GetCharacter(APIView):
    def put(self, request, format=None):
        user = self.request.user
        print("Data: ", self.request)
        character_id = self.request.data["id"]  
        character = CharacterCard.objects.get(id=character_id)
        char_serial = CharacterSerializer(character)
        return Response(char_serial.data)





class CreateWorld(APIView):
    def post(self, request, format=None):
        user = self.request.user
        data = self.request.data
        name = data["name"]
        description = data["description"]
        scenario = data["scenario"]
        src = data["src"]
        WorldCard.objects.create(name=name, description=description, 
                                     scenario=scenario, src=src, user_key=user)
        return Response({"response": "world created"})
    
class UpdateWorld(APIView):
    def patch(self, request, format=None):
        user = self.request.user
        data = self.request.data
        name = data["name"]
        description = data["description"]
        scenario = data["scenario"]
        world_id = data['id']
        src = data['src']
        world = WorldCard.objects.filter(id=world_id)
        world.update(name=name, description=description, 
                                src=src, scenario=scenario)
        return Response({"response": "world updated"})
    
class DeleteWorld(APIView):
    def delete(self, request, format=None):
        user = self.request.user
        data = self.request.data
        world_id = data['id']
        world = WorldCard.objects.filter(id=world_id)
        world.delete()
        return Response({"response": "world deleted"})

class GetWorlds(APIView):
    def get(self, request, format=None):
        user = self.request.user
        worlds = user.worldcard_set.all()
        world_serial = WorldSerializer(worlds, many=True)
        return Response(world_serial.data)
    


    

class GetCheckout(APIView):
    def put(self, request, format=None):
        user = self.request.user
        prices = {'unlimited': 'price_1O4zwXLcAPiyHOsMsguhc2P4', 'standard': 'price_1P0KUrLcAPiyHOsM5cAoRMYy',}
        metered_prices = {'standard': 'price_1P0KXELcAPiyHOsMwQ5rOok8', 'unlimited': 'price_1P10CcLcAPiyHOsMq5zQY31Q',}
        
        data = self.request.data
        product = data['product']
        stripe_response=stripe.checkout.Session.create(
            line_items=[
                {
                "price": prices[product],
                "quantity": 1,
                },
                {
                "price": metered_prices[product],
                }
            ],
            mode="subscription",
            success_url="https://vecleon.com/edit/characters/",
            cancel_url="https://vecleon.com/subscriptions/",
            customer_email=user.get_username(),
        )
        return Response(stripe_response)
    
class GetSubscription(APIView):
    def get(self, request, format=None):
        user = self.request.user
        cancelled = user.subscription_is_cancelled
        if user.stripe_subscription_id == '':
            return Response({'response' : 'not_subscribed'})
        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)
        return Response({"subscription": subscription, "cancelled":cancelled})
    
class GetSubscriptionIsActive(APIView):
    def get(self, request, format=None):
        user = self.request.user
        if user.subscription_is_active:
            return Response({'response' : 'active'})
        else:
            return Response({'response' : 'inactive'})
    
    

class CancelSubscription(APIView):
    # legacy, webhook listener 
    # for "customer.subscription.updated" does the same thing
    def put(self, request, format=None):
        user = self.request.user
        if user.stripe_subscription_id != '':
            try:
                stripe.Subscription.modify(user.stripe_subscription_id,
                                           cancel_at_period_end=True,)
                user.subscription_is_cancelled = True
                user.save()
            except:
                print(f'cannot cancel subscription {user.stripe_subscription_id}, possibly already cancelled')
        else:
            return Response({'user has no active subscription'})
        return Response({f'subscription {user.stripe_subscription_id} cancelled'})


class GetCustomerPortal(APIView):
    def put(self, request, format=None):
        user = self.request.user
        if user.stripe_customer_id != '':
            portal = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url="http://127.0.0.1:3000/account/",
                )
            return Response(portal)
        else:
            return Response({"no Stripe customer ID for this account found"})

    

class StripeWebhooks(APIView):
    endpoint_secret = 'whsec_88556757c031d0826ba778a9da2dc7b42297d0b103899b420b60267f2bd85b85'
    @csrf_exempt
    def post(self, request, format=None):
        event = None
        payload = self.request.data
        # print(payload)

        try:
            event = stripe.Event.construct_from(
            payload, stripe.api_key
            )
        except ValueError as e:
            # Invalid payload
            return Response(status=400)            
        print('meme')
            
        if event['type'] == 'checkout.session.completed':
            checkout = event['data']['object']
            print('Subscription for customer {} created'.format(checkout['customer']))
            print(checkout)
            user = User.objects.get(email=checkout['customer_email'])
            if user.stripe_subscription_id != '':
                try:
                    stripe.Subscription.cancel(user.stripe_subscription_id)
                except:
                    print(f'cannot cancel subscription {user.stripe_subscription_id}, possibly already cancelled')
                    user.stripe_subscription_id = ''
                    user.stripe_customer_id = ''
                    user.save()
            user.stripe_subscription_id = checkout['subscription']
            user.stripe_customer_id = checkout['customer']
            user.subscription_is_active = True
            invoice = stripe.Invoice.retrieve(checkout['invoice'])
            line_item = invoice['lines']['data'][0]
            user.subscription_package = line_item
            user.save()
                
                            
        elif event['type'] == 'invoice.paid':
            invoice = event['data']['object']
            subscription = invoice['subscription']
            customer = invoice['customer']
            user = User.objects.get(stripe_customer_id=customer)
            user.subscription_is_active = True
            line_item = invoice['lines']['data'][0]
            if 'Standard' in line_item["description"]:
                user.subscription_package = "Standard"
            elif 'Unlimited' in line_item["description"]:
                user.subscription_package = "Unlimited"
            else:
                user.subscription_package = "Undefined"
            user.current_usage = 0
            metered_id = stripe.Subscription(user.stripe_subscription_id).items.data[1].id
            stripe.SubscriptionItem.create_usage_record(metered_id, quantity=0 ,action='set',)
            user.save()


        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            user = User.objects.get(stripe_customer_id=subscription['customer'])
            if subscription['cancel_at_period_end']:
                user.subscription_is_cancelled = True
                user.save()
            else:
                user.subscription_is_cancelled = False
                user.save()

        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            subscription = invoice['subscription']
            customer = invoice['customer']
            user = User.objects.get(stripe_customer_id=customer)
            user.messages_left=0
            user.subscription_is_active=False
            user.save()

        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            user = User.objects.get(stripe_customer_id=subscription['customer'])
            user.subscription_is_active=False
            user.messages_left=0
            user.stripe_customer_id=''
            user.stripe_subscription_id=''
            user.save()

        else:
            # Unexpected event type
            print('Unhandled event type {}'.format(event['type']))

        return Response({'success':True})


