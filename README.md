# FoxScript3
FoxScript3 is the third iteraton of the MC Datapack toolkit. The new and improved version features a lot of helpfull shortcuts for .mcfunction files!

## Create your OWN COMMANDS
Using the simple JSON structure, you can create your own command in just seconds(See the wiki for more infos)!

## Better Loops and If Statements
Using the simple In-File Function declarations you can easily write lopps in the same file without having 10.000+ extra files!

## Generate Custom BLOCKS and ITEMS with textures using a simple Json File (Beta Feature)

# Quickstart

If you have Python installed on your Machine, you can simply execute the Compiler.py and it will open a Filechooser so you can select your project folder

The project must have the following folder structure:

```
├─project.json (More info on the wiki tab)
│
├─namespace
│ └─functions
│    ├─somefile.fs3
│    ├─anotherfile.mcfunction
│    └───afolder
│        └─yetanotherfile.foxscript
```

All files that can be read by Foxscript end with ".fs3", ".mcfunction" or ".foxscript"
