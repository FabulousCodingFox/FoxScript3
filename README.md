# FoxScript3
FoxScript3 is the third iteraton of the MC Datapack toolkit. The new and improved version features a lot of helpfull shortcuts for .mcfunction files!

# Quickstart

```python
import Compiler

projectPath = "C:/Users/name/Desktop/FoxScriptV3/project-example"
compilePath = "C:/Users/name/Desktop/FoxScriptV3/compiled"

compiler = Compiler.Compiler(projectPath,compilePath)
compiler.main()
```

The project must have the following folder structure:

```
├─project.json
│
├─namespace
│ ├─somefile.fs3
│ ├─anotherfile.fs3
│ └───afolder
│     └─yetanotherfile.foxscript
```

