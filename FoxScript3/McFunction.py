
class McFunction:
    def __init__(self,raw:str,namespace:str,path:str) -> None:
        self.raw=raw
        self.namespace=namespace
        self.path=path
        self.compiled=""
        self.name = path.replace("\\","/").split("/")[-1]
    def compile(self,keywords) -> None:
        final = ""

        for line in self.raw.split("\n"):
            res=""

            for kw in keywords:
                for alias in kw.aliases:

                    index=line.find(alias)

                    if line.lstrip().startswith(alias):
                        index = 0
                    elif "execute" in line and line.split(" run ")[-1].startswith(alias):
                        index = line.find(line.split(" run ")[-1])
                    else:
                        index = -1

                    res=line

                    if index!=-1:
                        status=kw.comp(line[index:])
                        if status==True:
                            res=line[:index]+kw.result

            final = final + res + "\n"

        self.compiled=final