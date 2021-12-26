import Compiler

projectPath = "C:/Users/..."
compilePath = "C:/Users/..."

compiler = Compiler.Compiler(projectPath,compilePath)
compiler.readProjectFiles()
compiler.compile()
compiler.create()
