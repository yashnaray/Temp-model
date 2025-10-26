class OpenAIEmbeddings:
    def embed(self, texts):
        return [[float(len(t))] for t in texts]
    def embed_texts(self, texts):
        return self.embed(texts)
