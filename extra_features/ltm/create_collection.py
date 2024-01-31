import time

import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema, CollectionSchema, DataType,
    Collection,
)


# create collection
def make_collection(collection_name):
    # create fields and collection
    fields = [
        FieldSchema(name="chat_id", dtype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=65535),
        FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=384),
        FieldSchema(name="content", dtype=DataType.VARCHAR, auto_id=False, max_length=65535),
    ]  
    schema = CollectionSchema(
        fields=fields,
        description="text embeddings",
        enable_dynamic_field=True
    )
    collection = Collection(
        name=collection_name,
        schema=schema,
        using='default',
        shards_num=1
    )

    # create index for search
    index_params = {
        "metric_type":"L2",
        "index_type":"IVF_FLAT",
        "params":{"nlist":10}
    }
    collection.create_index(
        field_name="embeddings", 
        index_params=index_params
    )
    utility.index_building_progress(collection_name)

    return collection


