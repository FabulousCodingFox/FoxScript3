# FoxScript3
FoxScript3 is the third iteraton of the MC Datapack toolkit. The new and improved version features a lot of helpfull shortcuts for .mcfunction files!

## Create your OWN COMMANDS
Using the simple JSON structure, you can create your own command in just seconds(See the wiki for more infos)!

## Better Loops and If Statements
Using the simple In-File Function declarations you can easily write lopps in the same file without having 10.000+ extra files!

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
│ ├─#tags
│ │  └─blocks
│ │    └─myblocks.json
│ ├─somefile.fs3
│ ├─anotherfile.mcfunction
│ └───afolder
│     └─yetanotherfile.foxscript
```

All files that can be read by Foxscript end with ".fs3", ".mcfunction" or ".foxscript"
