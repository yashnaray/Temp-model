from langchain_core.documents import Document
class DirectoryLoader:
    def __init__(self, path):
        self.path = path
    def load(self):
        return []
class TextLoader:
    def __init__(self, path, encoding='utf-8'):
        self.path = path
    def load(self):
        try:
            with open(self.path,'r',encoding='utf-8') as f:
                return [Document(f.read(), metadata={'source':self.path})]
        except:
            return []
class CSVLoader(TextLoader):
    pass
class PyPDFLoader:
    def __init__(self, path):
        self.path = path
    def load(self):
        # return empty list to avoid pdf parsing dependency
        return []
