import time

import numpy as np
from pymilvus import (
    connections,
    utility,
    Collection,
)
from . import embeddings
from . import create_collection


api_key = '58f32ad1080e42aa8a7504ad4e3ba9dfb60319651afb5598305c0d01da0eccf29b5b31ae7baecc20113ee1aa9f5f1915c39153ff'
cluster_endpoint = 'https://in03-25eea8454b3d622.api.gcp-us-west1.zillizcloud.com'

class LTM():
    def __init__(self, collection_name="chatbot1"):
        # Replace uri and API key with your own
        self.embedder = embeddings.Embedder(model_path='flax-sentence-embeddings/all_datasets_v4_MiniLM-L6')
        if utility.has_collection(collection_name):
            self.collection = Collection(collection_name)
            self.collection.load()
        else:
            self.collection = create_collection.make_collection(collection_name)

    def connect():
        #alias 	    Alias of the Milvus connection to construct.
        #host 	    IP address of the Milvus server.
        #port 	    Port of the Milvus server.
        connections.connect(
          alias="default", 
          host='localhost', 
          port='19530'
        )

    def disconnect():
        connections.disconnect("default")

    def add_vector(self, text):
        # add embedding vector(s) to database, given some text
        embd = self.embedder.get_embedding(text)
        mr = self.collection.insert(embd)
        return mr

    def search(self, text):
        # vector search embeddings, given some text
        embd = self.embedder.get_embedding(text)
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}, "offset": 5}
        results = self.collection.search(
            data=embd, 
            anns_field="text_embeddings", 
            param=search_params,
            limit=10, 
            expr=None,
            # set the names of the fields you want to retrieve from the search result.
            output_fields=['embeddings'],
            consistency_level="Strong"
        )

        print("search result IDs:\n", results[0].ids)
        print("search result distances:\n", results[0].distances)

        hit = results[0][0]
        hit.entity.get('title')





