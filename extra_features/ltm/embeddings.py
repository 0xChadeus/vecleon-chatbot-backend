from sentence_transformers import SentenceTransformer


class Embedder():
    def __init__(self, model_path='example'):
        self.model_path = model_path

    def get_embedding(self, text):
        model = SentenceTransformer(self.model_path)
        embeddings = model.encode(text)
        return embeddings
    


