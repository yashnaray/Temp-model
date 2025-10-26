class PromptTemplate:
    def __init__(self, input_variables=None, template=''):
        self.input_variables = input_variables or []
        self.template = template
    def format(self, **kwargs):
        try:
            return self.template.format(**kwargs)
        except Exception:
            # fallback to simple concatenation
            parts = [f"{k}: {v}" for k,v in kwargs.items()]
            return "\n".join(parts)
