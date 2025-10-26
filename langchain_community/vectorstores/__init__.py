import os, json
class FAISS:
    def __init__(self, embeddings):
        self.docs = []
        self.embeddings = embeddings
    def add_documents(self, documents):
        self.docs.extend(documents)
    def save_local(self, path):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path,'store.json'),'w') as fh:
            fh.write(str(len(self.docs)))
    @classmethod
    def load_local(cls, path, embeddings):
        inst = cls(embeddings)
        return inst
