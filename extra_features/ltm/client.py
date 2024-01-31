import time

import numpy as np
from pymilvus import (
    connections,
    utility,
    Collection,
)
from pymilvus import MilvusClient
from . import embeddings
from . import create_collection
from openai import OpenAI


API_KEY = '58f32ad1080e42aa8a7504ad4e3ba9dfb60319651afb5598305c0d01da0eccf29b5b31ae7baecc20113ee1aa9f5f1915c39153ff'
URI = 'https://in03-25eea8454b3d622.api.gcp-us-west1.zillizcloud.com'
USER='db_25eea8454b3d622'  # Username specified when you created this cluster
PASSWORD='Ha7*B>ds$qJ.;C?)'  # Password set for that account
FILE = '/content/books.csv'  # Download it from <https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks> and save it in the folder that holds your script.
COLLECTION_NAME = 'chatbot'  # Collection name
DIMENSION = 768  # Embeddings size

class LTM():

    openai_client = OpenAI(
        api_key='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',
        base_url='http://127.0.0.1:5000/v1'
    )

    def __init__(self, collection_name=COLLECTION_NAME):
        # Replace uri and API key with your own
        # self.client = MilvusClient(
        #     uri=URI, # Cluster endpoint obtained from the console
        #     token=API_KEY # API key or a colon-separated cluster username and password
        # )
        self.connect()
        self.embedder = embeddings.Embedder(model_path='flax-sentence-embeddings/all_datasets_v4_MiniLM-L6')
        if utility.has_collection(collection_name):
            print('1289j192en189n')
            self.collection = Collection(collection_name)
            self.collection.load()
        else:
            self.collection = create_collection.make_collection(collection_name)
            self.collection.load()

    def connect(self,):
        connections.connect(
            alias="default", 
            uri=URI, 
            user=USER, 
            password=PASSWORD, 
            secure=True,
        )

    def disconnect(self,):
        connections.disconnect("default")

    def get_b_read(self, user_input):
        # get whether or not to read from the vector db
        f = open('read_prompt.txt')
        prompt = f.read()
        f.close()

        completion = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt + user_input},
            ],
        )
        print(completion.choices[0].message.content)

        if 'yes' in completion.choices[0].message.content.lower():
            return True
        else:
            return False

    def get_b_write(self, user_input):
        # get whether or not to write to the vector db
        f = open('write_prompt.txt')
        prompt = f.read()
        f.close()

        completion = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": prompt + user_input},
            ],
        )

        print(completion.choices[0].message.content)
        if 'yes' in completion.choices[0].message.content.lower():
            return True
        else:
            return False

    def add_vector(self, text, chat_id):
        # add embedding vector(s) to database, given some text
        embd = self.embedder.get_embedding(text)
    
        data = [
            {
                "chat_id": chat_id,
                "content": text,
                "embeddings": embd
            }
        ]

        res = self.collection.insert(data)
        return res

    def search(self, text):
        # vector search embeddings, given some text
        embd = [self.embedder.get_embedding(text)]
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}, "offset": 5}
        results = self.collection.search(
            data=embd, 
            anns_field="embeddings", 
            param=search_params,
            limit=5, 
            expr=None,
            # set the names of the fields you want to retrieve from the search result.
            output_fields=['embeddings', 'content'],
            consistency_level="Strong"
        )

        print("search result IDs:\n", results[0].ids)
        print("search result distances:\n", results[0].distances)

        for hits in results:
            for hit in hits:
                print(f"hit: {hit}, embeddings: {hit.entity.get('embeddings')}")
        
        # print(results[0][0])
        if len(results[0]) > 0:
            hit = results[0][0]
            return hit.entity.get('content')
        else:
            return ''
            





