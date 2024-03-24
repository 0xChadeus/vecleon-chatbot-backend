# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync

from channels.auth import login
from channels.db import database_sync_to_async
import json
import requests
import sseclient  # pip install sseclient-py
import asyncio

import json
from .extra_features.ltm.client import LTM

from api.models import Chat, CharacterCard

import anthropic


class ChatConsumer(WebsocketConsumer):

    ltm = LTM(collection_name='chatbot1')
    s = requests.Session()
    client = anthropic.Anthropic(api_key='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')
    
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        user = self.scope['user']

        if not user.is_authenticated:
            print(user)
            print('user not authenticated')
            return
        elif user.free_msgs <= 0 and not user.subscription_is_active:
            print('user has exhausted their free messages and is not subscribed')
            return
        elif user.subscription_is_active and user.messages_left <= 0:
            print('user has exhausted their message quota for the month')
            return


        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        self.user_update_on_message()
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message_split = event["message"]

        user = self.scope['user']
        user_input = message_split[7]
        chat_id = message_split[-1]
        context = message_split[6] + '\n' + message_split[7]
        prefill = message_split[11]
        nsfw = message_split[12]
        system_prompt = message_split[0]

        chat = Chat.objects.get(id=chat_id)

        message_split[6] = "<context>" + '\n' + context + '\n' + "</context>"
        message_split[7] = ''
        # if chat.nsfw:
        #    message_split[12] = '<nsfw>' + '\n' + nsfw + '\n' + '</nsfw>'   
        # else:
        #    message_split[12] = ''
        message = '\n'.join(message_split)

        curr_mes = ''
        with self.client.messages.stream(
            max_tokens=1024,
            messages=[{"role": "user", "content": message + user_input}, {"role": "assistant", "content": prefill}, ],
            model="claude-3-opus-20240229",
        ) as stream:
            for text in stream.text_stream:
                curr_mes += text
                self.send(text_data=json.dumps({"message": text, "msg_complete": "false"}))



        self.send(text_data=json.dumps({"messsage": "", "msg_complete": "true"}))


    def user_update_on_message(self):
        user = self.scope['user']
        if not user.subscription_is_active:
            user.free_msgs -= 1
        else:
            user.messages_left -= 1
        
        user.save()


    
