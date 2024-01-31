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
from app.extra_features.ltm.client import LTM
from app.extra_features.calendar.google_calendar import Calendar
from app.extra_features.images.image_recognition import get_imagedesc
from app.extra_features.images.image_generation import ImageGenerator
from app.extra_features.voice.voice_recognition import speech_to_text
from app.extra_features.voice.voice_generation import AudioGenerator

from api.models import Chat, CharacterCard

from openai import OpenAI


class ChatConsumer(WebsocketConsumer):

    ltm = LTM(collection_name='chatbot1')
    calendar = Calendar()
    client = OpenAI(
        api_key='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',
        base_url='http://127.0.0.1:5000/v1'
    )
    img_generator = ImageGenerator()
    audio_generator = AudioGenerator()
    
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



        if user.subscription_is_active and (user.subscription_package == "Standard" or user.subscription_package == "Unlimited"):

            ltm_read = self.ltm.get_b_read(user_input)
            ltm_write = self.ltm.get_b_write(user_input)

            calendar_read = self.calendar.get_b_read(user_input)

            generate = self.img_generator.get_b_generate_img(context)
            generate_self = self.img_generator.get_b_generate_self_img(context)

            if ltm_read:
                ltm_result = self.ltm.search(user_input)
                message_split.insert(8, 
                        'This is the result \
                            from your long term memory \
                                which has the most relevance to \
                                the previous message: ' + ltm_result)          

            if ltm_write:
                self.ltm.add_vector(user_input, chat_id)

            if calendar_read:
                events = self.calendar.get_events()
                if events != None:
                    message_split.insert(8, 
                        'These are the next events\
                            recorded in the user\'s calendar: ' + str(events))    
                else:
                    message_split.insert(8, 
                        'These are the next events\
                            recorded in the user\'s calendar: ' + 'No events')    


            if generate[0]:
                image = self.img_generator.generate_image(positive_prompt='anime, landscape, masterpiece, ' + generate[1], 
                                                            negative_prompt='low quality, worst quality, deformed, horror')
            
                if image != 'error':
                    self.send(text_data=json.dumps({"image": image, 
                                            "is_image": True,
                                            "msg_complete": "false"}))

            if generate_self[0]:
                character_img = Chat.objects.get(id=chat_id).character_key.src
                self_image = self.img_generator.generate_self_image(img_url=character_img,
                                                            positive_prompt='1girl, ' + generate_self[1], 
                                                            negative_prompt='low quality, worst quality, deformed, horror',)
                if self_image != 'error':
                    self.send(text_data=json.dumps({"image": self_image, 
                                                    "is_image": True,
                                                    "msg_complete": "false"}))
                    


        message = '\n'.join(message_split)

        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": message},
            ],
            stream=True
        )
        
        curr_mes = ''
        for chunk in completion:
            msg_chunk = chunk.choices[0].delta.content
            print(chunk.choices[0].delta)
            curr_mes += msg_chunk
            self.send(text_data=json.dumps({"message": msg_chunk, 
                                                    "msg_complete": "false"}))
            
        # if user.subscription_package == "Unlimited":
        audio=self.audio_generator.generate(curr_mes)
        self.send(text_data=json.dumps({"audio": audio, "is_audio": True, "msg_complete": "false"}))

        self.send(text_data=json.dumps({"message": "", "msg_complete": "true"}))


    def user_update_on_message(self):
        user = self.scope['user']
        if not user.subscription_is_active:
            user.free_msgs -= 1
        else:
            user.messages_left -= 1
        
        user.save()

