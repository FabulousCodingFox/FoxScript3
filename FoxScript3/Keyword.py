
def getFailSafe(iter,index,failreplace):
    try:
        return iter[index]
    except IndexError:
        return failreplace




class Keyword:
    def __init__(self,config:dict) -> None:
        self.id = config["id"]
        self.aliases = config["aliases"]
        self.openEnding = config["openEnding"]
        self.syntax = config["syntax"]
        self.compile = config["compile"]
    
    def comp(self,string:str):
        alias = string.split(" ")[0]
        args = string.split(" ")[1:]

        syntax = {}

        if alias.lower() in self.aliases:
            if len(args) <= sum([1 if dic["essential"]==True else 0 for dic in dict(self.syntax).values()]):
                for arg in self.syntax:
                    num = int(arg)-1
                    possibilities = self.syntax[arg]["possibilities"]
                    if (len(args)-1 >= num and possibilities==None) or (len(args)-1 >= num and args[num] in possibilities):
                        syntax[arg]=args[num]
                    else:
                        return "Bad Arguments"
            else:
                return f"{alias} is missing important arguments"
        else:
            return None #Tells this sint the right Keyword

        
        for case in self.compile:
            valid = True
            for stmt in case.split(";"):
                if "==" in stmt:
                    if not syntax[stmt.split("==")[0]] == stmt.split("==")[1]:valid=False
                elif "!=" in stmt:
                    if not syntax[stmt.split("!=")[0]] != stmt.split("!=")[1]:valid=False
            if valid:
                self.result=self.compile[case]
                for text1,text2 in (
                    ("%[overflow]"," ".join(args[1:])),
                    ("%[1]",getFailSafe(args,0,"")),
                    ("%[2]",getFailSafe(args,1,"")),
                    ("%[3]",getFailSafe(args,2,"")),
                    ("%[4]",getFailSafe(args,3,"")),
                    ("%[5]",getFailSafe(args,4,""))
                ):self.result=self.result.replace(text1,text2)

                return True