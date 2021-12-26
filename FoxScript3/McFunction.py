
class McFunction:
    def __init__(self,raw:str,namespace:str,path:str) -> None:
        self.raw=raw
        self.namespace=namespace
        self.path=path
        self.compiled=""
        self.name = path.replace("\\","/").split("/")[-1]
    def compile(self) -> None:
        self.compiled=self.raw