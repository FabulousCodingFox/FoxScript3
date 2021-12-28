import logging

class McFunction:
    def __init__(self,raw:str,namespace:str,path:str,sourcepath:str) -> None:
        self.raw=raw
        self.namespace=namespace
        self.path=path
        self.compiled=""
        self.name = path.replace("\\","/").split("/")[-1]
        self.sourcepath=sourcepath

    def compile(self,keywords,reserved) -> None:
        logging.info(f"Project: Compiling File {self.namespace}:{self.path}")

        addFunctions = []

        final = ""

        blockedlines=[]

        for linenumber,line in enumerate(self.raw.split("\n")):
            res=""

            line=line.lstrip()

            #############################################################################################################################################################

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
            
            ##############################################################################################################################################################

            if linenumber in blockedlines:
                continue


            #line=line.replace("function this",f"function {self.namespace}:{self.path}")
            
            if "function{" in line.replace(" ",""):
                text=""
                level=0
                slot=reserved.new()

                for nlinenumber in range(linenumber+1,len(self.raw.split("\n"))):
                    nline=self.raw.split("\n")[nlinenumber].lstrip()
                    #print(nline,":",level)
                    if nline.lstrip().startswith("{") or nline.rstrip().endswith("{"):
                        level=level+1
                    elif nline.lstrip().startswith("}"):
                        level=level-1
                        if(level<=-1):
                            break
                    if level==0:
                        nline=nline.replace("function this",f"function {self.namespace}:{self.sourcepath+'_'+str(slot)}")
                    text=text+nline+"\n"

                addFunctions.append(McFunction(
                    text,#"\n".join([i.lstrip() for i in self.raw.split("\n")[linenumber+1:nlinenumber]]),
                    self.namespace,
                    self.sourcepath+"_"+str(slot),
                    self.sourcepath
                ))

                res = res[:res.find("function")]+f"function {addFunctions[-1].namespace}:{addFunctions[-1].path}"

                blockedlines=blockedlines+list(range(linenumber,nlinenumber+1))

                addFunctions=addFunctions+addFunctions[-1].compile(keywords,reserved)

            final = final + res + "\n"

        self.compiled=final

        return addFunctions



