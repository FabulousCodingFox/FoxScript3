import os,logging,json

_file_ = __file__.replace("\\","/")
_dir_ = _file_.replace(_file_.split("/")[-1],"")
logging.basicConfig(filename=_dir_+"runtime.log", encoding='utf-8', level=logging.DEBUG,filemode="w")

def stop(err):
    logging.error(err)
    quit()

def getFailSafe(iter,index,failreplace):
    try:
        return iter[index]
    except IndexError:
        return failreplace

class ReservedCounter:
    def __init__(self) -> None:
        self.c=0
    def new(self):
        self.c+=1
        return self.c

class McFunction:
    def __init__(self) -> None:
        self.content=""
        self.raw=""
        self.namespace=None
        self.path=""
        self.original_path=""
        self.reservedCounter=None
    
    def compile(self,compiler):
        logging.info(f"Project: Compiling File {self.namespace.name}:{self.path}")

        final = ""

        blockedlines=[]

        for linenumber,line in enumerate(self.raw.split("\n")):
            res=line

            line=line.lstrip()

            #############################################################################################################################################################

            for kw in compiler.keywords:
                for alias in kw.aliases:

                    #index=line.find(alias)

                    if line.lstrip().startswith(alias):
                        index = 0
                    elif "execute" in line and line.split(" run ")[-1].startswith(alias):
                        index = line.find(line.split(" run ")[-1])
                    else:
                        index = -1

                    #res=line

                    if index!=-1:
                        status=kw.comp(line[index:])
                        if status==True:
                            res=line[:index]+kw.result
                        
            
            ##############################################################################################################################################################

            

            if linenumber in blockedlines:
                continue
            
            if "function{" in line.replace(" ",""):
                text=""
                level=0
                slot=self.reservedCounter.new()

                for nlinenumber in range(linenumber+1,len(self.raw.split("\n"))):
                    nline=self.raw.split("\n")[nlinenumber].lstrip()
                    if nline.lstrip().startswith("{") or nline.rstrip().endswith("{"):
                        level=level+1
                    elif nline.lstrip().startswith("}"):
                        level=level-1
                        if(level<=-1):
                            break
                    if level==0:
                        nline=nline.replace("function this",f"function {self.namespace.name}:{self.original_path+'_'+str(slot)}")
                    text=text+nline+"\n"
                
                res = res[:res.find("function")]+f"function {self.namespace.name}:{self.original_path+'_'+str(slot)}"

                blockedlines=blockedlines+list(range(linenumber,nlinenumber+1))

                self.namespace.mcfunctions.append(McFunction())
                self.namespace.mcfunctions[-1].namespace=self.namespace
                self.namespace.mcfunctions[-1].path=self.original_path+"_"+str(slot)
                self.namespace.mcfunctions[-1].original_path=self.original_path
                self.namespace.mcfunctions[-1].raw=text
                self.namespace.mcfunctions[-1].reservedCounter=self.reservedCounter
                self.namespace.mcfunctions[-1].compile(compiler)

            final = final + res + "\n"

        self.content=final

class Namespace:
    def __init__(self,path,name) -> None:
        self.mcfunctions=[]
        self.path=path
        self.name=name
    
    def addFunction(self,func):
        self.mcfunctions.append(func)
    
    def compile(self,compiler):
        logging.info("Compiling namespace "+self.name)
        if os.path.exists(os.path.join(self.path,"functions")) and os.path.isdir(os.path.join(self.path,"functions")):
            for root,dirs,files in os.walk(os.path.join(self.path,"functions")):
                for file in files:

                    p = root.replace(self.path,"").replace("\\","/")
                    if p.startswith("/"):p=p[1:]
                    if not p.endswith("/"):p=p+"/"
                    p=p+file.split(".")[-2]
                    p=p.replace("functions/","")              #####################################MAKE BETTER

                    self.mcfunctions.append(McFunction())
                    self.mcfunctions[-1].namespace=self
                    self.mcfunctions[-1].path=p
                    self.mcfunctions[-1].original_path=p
                    self.mcfunctions[-1].reservedCounter=ReservedCounter()
                    with open(os.path.join(root,file)) as f:self.mcfunctions[-1].raw=f.read()
                    self.mcfunctions[-1].compile(compiler)

class Project:
    def __init__(self,path) -> None:
        self.namespaces=[]
        self.path=path

        self.validateProjectDotJson()
    
    def compile(self,compiler):
        logging.info("Clearing Target Folders")

        for folder in [self.config["TARGET"]["path"]["datapack"],self.config["TARGET"]["path"]["texturepack"]]:
            for root,dirs,files in os.walk(folder,topdown=False):
                for file in files:
                    os.remove(os.path.join(root,file))
                for dir in dirs:
                    os.rmdir(os.path.join(root,dir))
        
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data"))

        with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"pack.mcmeta"),"w") as file:
            file.write("{\"pack\": {\"pack_format\": "+"18"+",\"description\": \""+self.config["INFO"]["description"]+"\"}}")
        
        for folder in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path,folder)) and not folder.startswith("#"):
                logging.info("Found namespace "+folder)
                self.namespaces.append(Namespace(os.path.join(self.path,folder),folder))
                self.namespaces[-1].compile(compiler)

                path = os.path.join(os.path.join(self.config["TARGET"]["path"]["datapack"],"data"),self.namespaces[-1].name)

                os.mkdir(path)

                for mcfunc in self.namespaces[-1].mcfunctions:
                    p=os.path.join(path,mcfunc.path)

                    with open(p,"w") as file:
                        file.write(mcfunc.content)



    def validateProjectDotJson(self):
        if os.path.exists(os.path.join(self.path,"project.json")):
            try:
                with open(os.path.join(self.path,"project.json")) as file:self.config = json.load(file)
                a=self.config["INFO"]
                a=self.config["INFO"]["name"]
                a=self.config["INFO"]["description"]
                a=self.config["INFO"]["authors"]
                a=self.config["INFO"]["id"]
                a=self.config["TARGET"]
                a=self.config["TARGET"]["version"]
                a=self.config["TARGET"]["version"]["mc"]
                a=self.config["TARGET"]["version"]["fs"]
                a=self.config["TARGET"]["path"]
                a=self.config["TARGET"]["path"]["datapack"]
                a=self.config["TARGET"]["path"]["texturepack"]
                a=self.config["SCHEDULES"]
            except KeyError as err:stop("The project.json does not contain the following: "+err)
        else:stop("The path does not contain a project.json")

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
            return None

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

class Compiler:
    def __init__(self) -> None:
        try:
            with open(os.path.join(_dir_,"compiler.json")) as file:self.compiler_config=json.load(file)
        except FileNotFoundError:self.stop("The Compiler doesnt have a compiler.json")
        logging.info("Compiler: Validated all contents of compiler.json")

        self.keywords = []
        for kwKey in self.compiler_config["KEYWORDS"]:
            self.keywords.append(Keyword(self.compiler_config["KEYWORDS"][kwKey]))

if __name__=="__main__":
    projekt = Project("..\\project-example")
    projekt.compile(Compiler())