import Compiler

projectPath = "C:/Users/fabif/Desktop/FoxScriptV3/project-example"
compilePath = "C:/Users/fabif/Desktop/FoxScriptV3/compiled"

compiler = Compiler.Compiler(projectPath,compilePath)
compiler.readProjectFiles()
compiler.compile()
compiler.create()