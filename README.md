# Compiler-for-Mini-C-
This project wants to make a compiler for the programming language C++, but not all the concepts about it, but some basic and fundamental subjetcs of the language.

# Folder

About the 'Analizadores' folder, it can tell that it's contains the different classes we need to build the compiler. Previously, Lexer was builded. The lexer, lets tokenize an input (test case) writen in C++ code. That works perfect.

For parser, and the AST creation, it have problems. With the parser, the grammar rules was defined, however, to create the AST is complicated because, when the programm try to recognize the different expressions or statements, only recognize an expression like this: 'TYPE_SPECIFIER IDENTIFIER SEMICOLON'. Then an expression like: 'int x;' is recognized but other distintc, for example, an assignment like: 'int x = 2;' print sintax errors.  In the future, that will be fixed with the next commit. For this part, we already have all the needed classes and the class to create the AST works. But, the problem maybe is in the parser with the grammar rules.

# AST Visualization
For the AST visualization, the class will create an file with instruction with DOT format. You can use: [https://dreampuf.github.io/GraphvizOnline/#digraph%20G%20%7B%0D%0Anode0%20%5Blabel%3D"Program"%5D%3B%0D%0Anode1%20%5Blabel%3D"VarDeclStmt"%5D%3B%0D%0Anode0%20->%20node1%3B%0D%0Anode2%20%5Blabel%3D"type_%20%3D%20int"%5D%3B%0D%0Anode1%20->%20node2%3B%0D%0Anode3%20%5Blabel%3D"identifier%20%3D%20main"%5D%3B%0D%0Anode1%20->%20node3%3B%0D%0Anode4%20%5Blabel%3D"expr%20%3D%202"%5D%3B%0D%0Anode1%20->%20node4%3B%0D%0A%7D] This tool works good, and it'll show you the Tree with his nodes.
