import logging,json,os,McFunction,Keyword

_file_ = __file__.replace("\\","/")
_dir_ = _file_.replace(_file_.split("/")[-1],"")

logging.basicConfig(filename=_dir_+"runtime.log", encoding='utf-8', level=logging.DEBUG,filemode="w")

class Compiler:
    def stop(self,cause="A compiling Error occured"):
        logging.warn("Compiler stoppped: "+cause)
        quit()
    
    def validateProjectDotJson(self):
        try:
            a = self.project_config["NAME"]
            a = self.project_config["MC-VERSION"]
            a = self.project_config["FS3-VERSION"]
            a = self.project_config["AUTHOR"]
            a = self.project_config["Description"]
            a = self.project_config["schedules"]
        except KeyError as ex:
            self.stop("project.json is missing essential Attributes. is it up to date?")

    def __init__(self,project_path,compile_path) -> None:
        self.project_path=project_path
        self.compile_path=compile_path
        self.fs_version = "3.0.6"

        try:
            with open(_dir_+"compiler.json") as file:self.compiler_config=json.load(file)
        except FileNotFoundError:self.stop("The Compiler doesnt have a compiler.json")
        logging.info("Compiler: Validated all contents of compiler.json")

        try:
            with open(os.path.join(self.project_path,"project.json")) as file:self.project_config=json.load(file)
        except FileNotFoundError:self.stop("The Project doesnt have a config.json")
        self.validateProjectDotJson()
        logging.info("Project: Validated all contents of project.json")
        
        self.project_string = f"\"{self.project_config['NAME']}\" by \"{self.project_config['AUTHOR']}\" for Minecraft Version {self.project_config['MC-VERSION']}: {self.project_config['Description']}"
        logging.info(self.project_string)

        if self.fs_version!=self.project_config["FS3-VERSION"]:logging.warn(f"Project: Versions dont match! The Programm is written for FoxScript3 Version {self.project_config['FS3-VERSION']} and the Compiler is on Version {self.fs_version}")

        self.keywords = []
        for kwKey in self.compiler_config["KEYWORDS"]:
            self.keywords.append(Keyword.Keyword(self.compiler_config["KEYWORDS"][kwKey]))

    def readProjectFiles(self) -> list:
        allFiles = []

        for (root,dirs,files) in os.walk(self.project_path,topdown=False):

            for file in files:
                
                if file.endswith(".fs3") or file.endswith(".mcfunction") or file.endswith(".foxscript"):

                    with open(os.path.join(root,file),"r") as f:

                        p = root.replace(self.project_path,"").replace("\\","/")
                        if p.startswith("/"):p=p[1:]
                        if p.endswith("/"):p=p[:len(p)-1]
                        n = p.split("/")[0]

                        p = root.replace(self.project_path,"").replace("\\","/")
                        if p.startswith("/"):p=p[1:]
                        if not p.endswith("/"):p=p+"/"
                        p=p+file.split(".")[-2]
                        p=p.replace(n+"/","")

                        allFiles.append(McFunction.McFunction(f.read(),n,p)) 

                        logging.info(f"Project: Reading File {n}:{p}")

        self.allFiles = allFiles

        return allFiles

    def compile(self) -> None:
        for f in self.allFiles:
            addFunctions = f.compile(self.keywords)
            self.allFiles=self.allFiles+addFunctions
            
    def create(self) -> None:

        for (root,dirs,files) in os.walk(self.compile_path,topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))

        for file in self.allFiles:

            fp = self.compile_path
            if fp[len(fp)-1] != "/": fp+="/"

            path = file.path.split()
            path.insert(0,"data")
            path.insert(1,file.namespace)
            path.insert(2,"functions")
            path.pop()

            for f in path:
                fp = fp + f + "/"
                if not os.path.isdir(fp): os.mkdir(fp)
            
            p = fp + file.name + ".mcfunction"
            with open(p,"w") as ignore:
                ignore.write(file.compiled)

        logging.info("Project: Created Function-Files")

        
        fp = self.compile_path
        if fp[len(fp)-1] != "/": fp+="/"

        with open(fp+"pack.mcmeta","w") as ignore:
            ignore.write("{\"pack\": {\"pack_format\": "+self.compiler_config["pack_format"][self.project_config["MC-VERSION"]]+",\"description\": \""+self.project_config["Description"]+"\"}}")

        os.mkdir(fp+"data/minecraft/")
        os.mkdir(fp+"data/minecraft/tags/")
        os.mkdir(fp+"data/minecraft/tags/functions/")

        with open(fp+"data/minecraft/tags/functions/tick.json","w") as tick:
            with open(fp+"data/minecraft/tags/functions/load.json","w") as load:
                tickcontent={"values":[],"replace":False}
                loadcontent={"values":[],"replace":False}
                for schedule in self.project_config["schedules"]:
                    if schedule["timing"]=="load":
                        loadcontent["values"].append(schedule["path"])
                    elif schedule["timing"]=="tick":
                        tickcontent["values"].append(schedule["path"])
                json.dump(loadcontent, load)
                json.dump(tickcontent, tick)
        logging.info("Project: Created Files")




    def main(self):
        self.readProjectFiles()
        self.compile()
        self.create()

