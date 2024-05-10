# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

import json
import requests
import time

import json
from .extra_features.ltm.client import LTM

from api.models import Chat

import anthropic
import replicate
from transformers import LlamaTokenizerFast

import stripe
stripe.api_key = "sk_test_51O0YIeLcAPiyHOsMCUTkBhuJF5iaza6JRQcGoUxGnQmDznH3TmxKd2pQUHxPyGdzKRSwSef2lzWgMU1BvvBviY8u00fTjWc0Ju"



class ChatConsumer(WebsocketConsumer):

    ltm = LTM(collection_name='chatbot1')
    s = requests.Session()
    client = anthropic.Anthropic(api_key='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')
    message_finished = True
    tokenizer = LlamaTokenizerFast.from_pretrained("hf-internal-testing/llama-tokenizer")
    
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
        elif not user.subscription_is_active:
            print('user is not subscribed')
            return


        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        while not self.message_finished:
            print('message not finished')
            time.sleep(1)

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
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
        prefill = message_split[10]
        nsfw = message_split[11]
        system_prompt = message_split[0]

        chat = Chat.objects.get(id=chat_id)


        if user.subscription_is_active and user.stripe_subscription_id != '':
            self.message_finished=False

            message_split[6] = '<nsfw>' + '\n' + nsfw + '\n' + '</nsfw>'
            message_split[8] = ''
            message_split[9] = ''
            message_split[10] = ''
            message_split[11] = ''
            message_split[12] =  "<context>" + '\n' + context + '\n' + "</context>"   
            message = '\n'.join(message_split)

            input_tokens = self.tokenizer.encode(message + user_input + '\n' + prefill)
            n_input_tokens = len(input_tokens)
            if n_input_tokens > 7800:
                context = context[-(7800-n_input_tokens):len(context)]
            message_split[12] = "<context>" + '\n' + context + '\n' + "</context>"
            message = '\n'.join(message_split)

            curr_mes = ''
            input = {'prompt': message + user_input + '\n' + prefill, 'temperature': 2.5, 'top_p': 0.7, 'top_k': 20, 'max_new_tokens': 1000, 'repetition_penalty':0.85}

            for event in replicate.stream("meta/meta-llama-3-70b-instruct", input= input):
                    self.send(text_data=json.dumps({"message": str(event), "msg_complete": "false"}))
                    curr_mes += str(event)
            output_tokens = self.tokenizer.encode(curr_mes)
            n_output_tokens = len(output_tokens)
            user.current_usage += n_input_tokens + n_output_tokens
            user.input_tokens += n_input_tokens
            user.output_tokens += n_output_tokens
            user.save()
            stripe.billing.MeterEvent.create(
                event_name='vecleon_chat_tokens',
                payload={"value": n_input_tokens + n_output_tokens, "stripe_customer_id": user.stripe_customer_id}
            )
            #stripe.billing.MeterEvent.create(
            #    event_name='vecleon_standard_input_tokens',
            #    payload={"value": n_input_tokens, "stripe_customer_id": user.stripe_customer_id}
            #)
            #stripe.billing.MeterEvent.create(
            #    event_name='vecleon_standard_output_tokens',
            #    payload={"value": n_output_tokens, "stripe_customer_id": user.stripe_customer_id}
            #)
            self.message_finished=True
        else:
            self.send(text_data=json.dumps({"message": 'account has no active subscription', "msg_complete": "true"}))

        self.send(text_data=json.dumps({"message": "", "msg_complete": "true"}))


