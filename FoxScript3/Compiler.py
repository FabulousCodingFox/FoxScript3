import os,logging,json,tkinter,shutil
from tkinter import filedialog
from tkinter.constants import S

# Creating a root Tk window and prevent it from showing
rootW=tkinter.Tk();rootW.withdraw()

#Getting Compiler File- and Dirpath
_file_ = __file__.replace("\\","/")
_dir_ = _file_.replace(_file_.split("/")[-1],"")

#Logging to a file
logging.basicConfig(filename=_dir_+"runtime.log", encoding='utf-8', level=logging.DEBUG,filemode="w")

#Stopping the Compiler in the event of an error
def stop(err):
    logging.error(err)
    quit()

#Getting an Index, but FailSafe
def getFailSafe(iter,index,failreplace):
    try:
        return iter[index]
    except (IndexError, KeyError):
        return failreplace

#A small Utility for a pointer to a counter
class ReservedCounter:
    def __init__(self) -> None:self.c=0
    def new(self):self.c+=1;return self.c

#A dataclass managing McFunctions files and their compiling
class McFunction:
    def __init__(self) -> None:
        self.content=""
        self.raw=""
        self.namespace=None
        self.path=""
        self.original_path=""
        self.reservedCounter=None
    
    def compile(self,compiler):
        logging.info(f"[McFunction] Compiling File {self.namespace.name}:{self.path}")

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

        

        copyrighttext=f"""###########################################################################################################################\n# Compiled using FoxScriptV3(https://github.com/FabulousCodingFox/FoxScript3)                                             #\n# Compiler Version {compiler.compiler_config["VERSION"]}{(103-len(compiler.compiler_config["VERSION"]))*" "}#\n# {self.namespace.project.project_string}{(120-len(self.namespace.project.project_string))*" "}#\n# Function {self.namespace.name}:{self.path} {(109-len(self.namespace.name+self.path))*" "}#\n###########################################################################################################################\n"""

        self.content=copyrighttext + final


#A dataclass managing Namespaces aka Wrappers for FUnctions, Generators, etc.
class Namespace:
    def __init__(self,path,name,project) -> None:
        self.mcfunctions=[]
        self.customblocks=[]
        self.path=path
        self.name=name
        self.project=project
    
    def addFunction(self,func):
        self.mcfunctions.append(func)
    
    def compile(self,compiler):
        logging.info("[Namespace] Compiling namespace "+self.name)
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
        
        if os.path.exists(os.path.join(self.path,"generators","blocks")) and os.path.isdir(os.path.join(self.path,"generators","blocks")):
            slotter=ReservedCounter()
            for folder in os.listdir(os.path.join(self.path,"generators","blocks")):
                if os.path.isdir(os.path.join(self.path,"generators","blocks",folder)) and os.path.exists(os.path.join(self.path,"generators","blocks",folder,"block.json")):
                    logging.info(f"[Namespace] Found custom block {folder}")

                    self.customblocks.append(CustomBlock())
                    self.customblocks[-1].name=folder
                    self.customblocks[-1].path=os.path.join(self.path,"generators","blocks",folder)
                    with open(os.path.join(self.customblocks[-1].path,"block.json")) as file:self.customblocks[-1].config=json.load(file)
                    self.customblocks[-1].model=os.path.join(self.customblocks[-1].path,self.customblocks[-1].config["assets"]["model"])
                    self.customblocks[-1].atlas=[i if os.path.isfile(os.path.join(self.customblocks[-1].path,i)) and i.endswith(".png") else None for i in os.listdir(self.customblocks[-1].path)]
                    self.customblocks[-1].custommodeldata=slotter.new()

#A dataclass controlling the project
class Project:
    def __init__(self,path,compiler) -> None:
        self.namespaces=[]
        self.path=path
        self.compiler=compiler

        self.validateProjectDotJson()

        self.project_string = f"""{self.config["INFO"]["name"]} by {", ".join(self.config["INFO"]["authors"])}:  {self.config["INFO"]["description"]}"""
    
    def compile(self):
        compiler=self.compiler
        logging.info("[Project] Clearing Target Folders")

        for folder in [self.config["TARGET"]["path"]["datapack"],self.config["TARGET"]["path"]["texturepack"]]:
            for root,dirs,files in os.walk(folder,topdown=False):
                for file in files:
                    os.remove(os.path.join(root,file))
                for dir in dirs:
                    os.rmdir(os.path.join(root,dir))

        logging.info("[Project] Generating&Compiling Namespaces")
        
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data"))

        with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"pack.mcmeta"),"w") as file:
            pack_format=getFailSafe(self.compiler.compiler_config["pack_format"],self.config["TARGET"]["version"]["mc"],False)
            if pack_format!=False:file.write("{\"pack\": {\"pack_format\": "+pack_format+",\"description\": \""+self.config["INFO"]["description"]+"\"}}")
            else:
                stop(f"[Project] The targeted MC Version {self.config['TARGET']['version']['mc']} isnt supported! Use one of the supported ones: {str(list(self.compiler.compiler_config['pack_format'].keys()))}")
        
        for folder in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path,folder)) and not folder.startswith("#"):
                logging.info("[Project] Found namespace "+folder)
                self.namespaces.append(Namespace(os.path.join(self.path,folder),folder,self))
                self.namespaces[-1].compile(compiler)

                path = os.path.join(os.path.join(self.config["TARGET"]["path"]["datapack"],"data"),self.namespaces[-1].name)

                os.mkdir(path)
                os.mkdir(os.path.join(path,"functions"))

                for mcfunc in self.namespaces[-1].mcfunctions:
                    p=os.path.join(path,"functions",mcfunc.path)

                    subdirs=mcfunc.path.split("/")
                    subdirs.pop()

                    for instancenum,instance in enumerate(subdirs):
                        if not os.path.exists(os.path.join(path,"functions","/".join(subdirs[:instancenum+1]))): os.mkdir(os.path.join(path,"functions","/".join(subdirs[:instancenum+1])))

                    with open(p+".mcfunction","w") as file:
                        file.write(mcfunc.content)
                
                logging.info("[Project] Moving folders (tags,etc.)")
                
                for folder in os.listdir(os.path.join(self.path,self.namespaces[-1].name)):
                    if os.path.isdir(os.path.join(self.path,self.namespaces[-1].name,folder)) and folder in ["advancements","item_modifiers","loot_tables","predicates","recipes","structures","tags","dimension","dimension_type","worldgen"]:
                        target=os.path.join(path,folder)
                        source=os.path.join(self.path,self.namespaces[-1].name,folder)
                        os.mkdir(target)
                        for (nroot,ndirs,nfiles) in os.walk(source,topdown=True):
                            for ndir in ndirs:
                                pt=str(os.path.join(nroot,ndir).replace("\\","/").replace(source.replace("\\","/"),"")).replace("\\","/")
                                if pt.startswith("/"):pt=pt[1:]
                                os.mkdir(os.path.join(target,pt))
                            for nfile in nfiles:
                                pt=str(os.path.join(nroot,nfile).replace("\\","/").replace(source.replace("\\","/"),"")).replace("\\","/")
                                if pt.startswith("/"):pt=pt[1:]
                                with open(os.path.join(nroot,nfile),"r") as original:
                                    with open(os.path.join(target,pt),"w") as new:
                                        new.write(original.read())
                                
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","minecraft"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","minecraft","tags"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","minecraft","tags","functions"))

        logging.info("Generating TexturePack")
        
        with open(os.path.join(self.config["TARGET"]["path"]["texturepack"],"pack.mcmeta"),"w") as file:
            pack_format=getFailSafe(self.compiler.compiler_config["pack_format"],self.config["TARGET"]["version"]["mc"],False)
            if pack_format!=False:file.write("{\"pack\": {\"pack_format\": "+pack_format+",\"description\": \""+self.config["INFO"]["description"]+"\"}}")

        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","textures"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","textures","customblocks"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","models"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","models","item"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","models","customblocks"))

        path = os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft")

        with open(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","models","item","item_frame.json"),"w") as file:file.write("{\"parent\": \"item/generated\",\"textures\": {\"layer0\": \"item/item_frame\"},\"overrides\": []}")

        
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions"))
        os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions","customblocks"))


        
        for namespace in self.namespaces:
            for customBlock in namespace.customblocks:
                customBlock:CustomBlock
                #Moving textures
                os.mkdir(os.path.join(path,"textures","customblocks",customBlock.name))
                for tex in customBlock.atlas:
                    if tex==None: continue
                    shutil.copy(os.path.join(customBlock.path,tex),os.path.join(path,"textures","customblocks",customBlock.name,tex))
                #Moving and modifiing model
                logging.info(f"[Customblock] {customBlock.name} Generating/modifying the model + textures")
                os.mkdir(os.path.join(path,"models","customblocks",customBlock.name))
                with open(os.path.join(customBlock.path,customBlock.config["assets"]["model"])) as source:
                    with open(os.path.join(path,"models","customblocks",customBlock.name,customBlock.config["assets"]["model"]),"w") as target:
                        js = json.load(source)
                        for tex in js["textures"]:js["textures"][tex]="customblocks/"+customBlock.name+"/"+js["textures"][tex].split("/")[-1]
                        if not "display" in js:js["display"]={}
                        js["display"]["head"]={"rotation": [0, 0, 0],"translation": [0, -30.43, 0],"scale": [1.601, 1.601, 1.601]}
                        json.dump(js,target)
                #Adding Itself to the ItemFrame CustomModelData
                logging.info(f"[Customblock] {customBlock.name} can now be found under the CustomModelData of {customBlock.custommodeldata}")
                with open(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","models","item","item_frame.json"),"r") as file:js=json.load(file)

                js["overrides"].append({"predicate": {"custom_model_data": customBlock.custommodeldata},"model": f"customblocks/{customBlock.name}/{''.join(customBlock.config['assets']['model'].split('.')[:-1])}"})

                with open(os.path.join(self.config["TARGET"]["path"]["texturepack"],"assets","minecraft","models","item","item_frame.json"),"w") as file:json.dump(js,file)
                #Generating Functions

                os.mkdir(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions","customblocks",customBlock.name))

                with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions","customblocks",customBlock.name,"destroy.mcfunction"),"w") as file:
                    txt=""
                    if customBlock.config["dropItem"]: txt=txt+"""execute if entity @p[gamemode=survival] run summon item ~ ~0.5 ~ {Item:{id:"minecraft:item_frame",Count:1b,tag:{EntityTag:{Tags:["customblocks","customblocks."""+customBlock.name+""""],Invisible:1b},CustomModelData:"""+str(customBlock.custommodeldata)+""",display:{Name:"{\\"text\\":\\\""""+customBlock.config["DisplayName"]+"""\\",\\"italic\\":\\"false\\"}"}}},Motion:[0.0d,0.2d,0.0d],PickupDelay:10}\n"""
                    txt=txt+"""execute if entity @p[gamemode=survival] run kill @e[type=item,distance=..1,limit=1,sort=nearest,nbt={Item:{id:\""""+customBlock.config["base"]+"""\"}}]\nkill @s"""
                    file.write(txt+"\n"+customBlock.config["functions"]["break"])

                with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions","customblocks",customBlock.name,"give.mcfunction"),"w") as file:
                    txt="""give @p minecraft:item_frame{EntityTag:{Tags:["customblocks","customblocks."""+customBlock.name+""""],Invisible:1b},CustomModelData:"""+str(customBlock.custommodeldata)+""",display:{Name:"{\\"text\\":\\\""""+customBlock.config["DisplayName"]+"""\\",\\"italic\\":\\"false\\"}"}}"""
                    file.write(txt)

                with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions","customblocks",customBlock.name,"place.mcfunction"),"w") as file:
                    txt="""execute at @s align xyz run summon armor_stand ~0.5 ~ ~0.5 {Marker:1b,Invisible:1b,Pose:{Head:[0f,180f,0f]},Tags:["customblocks","customblocks."""+customBlock.name+""""],ArmorItems:[{},{},{},{id:"minecraft:item_frame",Count:1b,tag:{CustomModelData:"""+str(customBlock.custommodeldata)+"""}}]}\nexecute at @s run setblock ~ ~ ~ """+customBlock.config["base"]+"""\nexecute at @s align xyz run playsound """+customBlock.config["sound"]["place"]+""" block @a[distance=..16]\nkill @s"""
                    file.write(txt+"\n"+customBlock.config["functions"]["place"])
                
                with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","foxscript","functions","customblocks","tick.mcfunction"),"a") as file:
                    txt="""execute as @e[type=minecraft:item_frame,tag=customblocks."""+customBlock.name+"""] run function foxscript:customblocks/"""+customBlock.name+"""/place\nexecute as @e[type=minecraft:armor_stand,tag=customblocks."""+customBlock.name+"""] at @s unless block ~ ~ ~ """+customBlock.config["base"]+""" run function foxscript:customblocks/"""+customBlock.name+"""/destroy\n"""
                    file.write(txt)


                    found=False
                    for s in self.config["SCHEDULES"]:
                        if s["path"]=="foxscript:customblocks/tick":found=True
                    if found==False:
                        self.config["SCHEDULES"].append({"timing":"tick","path":"foxscript:customblocks/tick"})




        

        




        logging.info("[Project] Creating tick.json and load.json")
        with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","minecraft","tags","functions","tick.json"),"w") as tickFile:
            with open(os.path.join(self.config["TARGET"]["path"]["datapack"],"data","minecraft","tags","functions","load.json"),"w") as loadFile:
                tick={"values":[],"replace":False}
                load={"values":[],"replace":False}

                for schedule in self.config["SCHEDULES"]:
                    if schedule["timing"]=="tick":tick["values"].append(schedule["path"])
                    elif schedule["timing"]=="load":load["values"].append(schedule["path"])
                
                json.dump(load,loadFile)
                json.dump(tick,tickFile)

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
            except KeyError as err:stop("[Project] The project.json does not contain the following: "+err)
        else:stop("[Project] The path does not contain a project.json")

        self.checkCompatibility(self.config["TARGET"]["version"]["fs"],self.compiler.compiler_config["VERSION"])
        
        path="/".join(_dir_.split("/")[:-2])
        self.config["TARGET"]["path"]["datapack"]=self.config["TARGET"]["path"]["datapack"].replace("(BASEDIR)",path)
        self.config["TARGET"]["path"]["texturepack"]=self.config["TARGET"]["path"]["texturepack"].replace("(BASEDIR)",path)

        if not os.path.exists(self.config["TARGET"]["path"]["datapack"]):stop("[Project] The path for the Target Datapack doesnt exist")
        if not os.path.exists(self.config["TARGET"]["path"]["texturepack"]):stop("[Project] The path for the Target Texturepack doesnt exist")

    def checkCompatibility(self,projVersion:str,compVersion:str):
        master=projVersion.split(".")[0]
        version=projVersion.split(".")[1]
        iteration=projVersion.split(".")[2].split("-")[0]
        isAlpha=False if getFailSafe(projVersion.split(".")[2].split("-"),1,False)==False else True

        comp_master=compVersion.split(".")[0]
        comp_version=compVersion.split(".")[1]
        comp_iteration=compVersion.split(".")[2].split("-")[0]
        comp_isAlpha=False if getFailSafe(compVersion.split(".")[2].split("-"),1,False)==False else True

        if comp_isAlpha:logging.warning("[Version] The Compiler is an Alpha build and may not support all features or may break")
        if isAlpha:logging.warning("[Version] The Project is for an Alpha build and may not be read correctly")

        if master!=comp_master:stop(f"[Version] The Compiler is for Foxscript{comp_master} and the project is for FoxScript{master}. That Error is literally impossible")

        if version!=comp_version:stop(f"[Version] Either the Compiler(Version {comp_master}.{comp_version}) or the Project(Version {master}.{version}) is outdated and doesnt support the featured features.")

        if iteration!=comp_iteration:logging.warning(f"[Version] The iterations dont match! Compiler is on Iteration {comp_iteration} and the Project is made for Iteration {iteration}")

#A dataclass covering Keywords for the compiler() of a McFunction
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

#A dataclass covvering CustomBlocks
class CustomBlock:
    def __init__(self) -> None:
        self.name=""
        self.path=""
        self.config={}

        self.model=""
        self.atlas=[]

        self.custommodeldata=0
        
    def compile(self):
        pass

    def validateBlockDotJson(self):
        try:
            a=self.config["id"]
            a=self.config["base"]
            a=self.config["sound"]
            a=self.config["sound"]["break"]
            a=self.config["sound"]["place"]
            a=self.config["assets"]
            a=self.config["assets"]["model"]
            a=self.config["ElevatedArmorStand"]
            a=self.config["functions"]
            a=self.config["functions"]["place"]
            a=self.config["functions"]["break"]
            a=self.config["dropItem"]
            a=self.config["DisplayName"]
        except KeyError as err:stop("[CustomBlock] The block.json does not contain the following: "+err)

#A dataclass saving the COmpiler preferences
class Compiler:
    def __init__(self) -> None:
        try:
            with open(os.path.join(_dir_,"compiler.json")) as file:self.compiler_config=json.load(file)
        except FileNotFoundError:self.stop("[Compiler] Couldnt find compiler.json in the source directory. Is it up-to-date?")
        logging.info("[Compiler] Validated all contents of compiler.json")

        self.keywords = []
        for kwKey in self.compiler_config["KEYWORDS"]:
            self.keywords.append(Keyword(self.compiler_config["KEYWORDS"][kwKey]))
        logging.info("[Compiler] Generated custom Keywords "+str([i.id for i in self.keywords]))

print("""
==========================================================================================================================
FoxScript 3 - Credits

Programming:
FabulousFox

Optional Dependencies:
Local-WASD by Miestrode to detect wasd Button Presses: https://github.com/Miestrode/local-wasd (modified version)
==========================================================================================================================
""")

if __name__=="__main__":
    with open(os.path.join(_dir_,"session.json"),"r") as file:data=json.load(file)
    toOpen = filedialog.askdirectory(mustexist=True,title="Choose the Folder containing project.json",initialdir=data["OpenDirectory"])
    data["OpenDirectory"]=toOpen
    with open(os.path.join(_dir_,"session.json"),"w") as file:json.dump(data,file)
    projekt = Project(toOpen,Compiler())
    projekt.compile()
    logging.shutdown()
