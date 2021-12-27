import Compiler

projectPath = ".."
compilePath = ".."

compiler = Compiler.Compiler(projectPath,compilePath)
compiler.readProjectFiles()
compiler.compile()
compiler.create()
