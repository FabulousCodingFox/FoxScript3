import logging

class McFunction:
    def __init__(self,raw:str,namespace:str,path:str) -> None:
        self.raw=raw
        self.namespace=namespace
        self.path=path
        self.compiled=""
        self.name = path.replace("\\","/").split("/")[-1]
    def compile(self,keywords) -> None:
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
            
            if "function{" in line.replace(" ",""):
                text=""
                level=0

                for nlinenumber in range(linenumber+1,len(self.raw.split("\n"))):
                    if line.lstrip().startswith("{"):
                        level+=1
                    elif line.lstrip().startswith("}"):
                        level-=1
                        if(level<=-1):
                            break
                #addFunctions.append(McFunction("\n".join(self.raw.split("\n")[linenumber:nlinenumber])))
                #self.raw.split("\n")[linenumber+1:nlinenumber]
                #[i.lstrip() for i in self.raw.split("\n")[linenumber+1:nlinenumber]]
                #print("\n".join([i.lstrip() for i in self.raw.split("\n")[linenumber+1:nlinenumber]]))



                addFunctions.append(McFunction(
                    "\n".join([i.lstrip() for i in self.raw.split("\n")[linenumber+1:nlinenumber]]),
                    self.namespace,
                    self.path+"_"
                ))

                res = res[:res.find("function")]+f"function {addFunctions[-1].namespace}:{addFunctions[-1].path}"

                blockedlines=blockedlines+list(range(linenumber,nlinenumber+1))

               
                addFunctions=addFunctions+addFunctions[-1].compile(keywords)


                
            final = final + res + "\n"

        self.compiled=final

        return addFunctions



