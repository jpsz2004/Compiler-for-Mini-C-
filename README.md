# Compiler-for-Mini-C-
This project wants to make a compiler for the programming language C++, but not all the concepts about it, but some basic and fundamental subjetcs of the language.

# Folder

About the 'Analizadores' folder, it can tell that it's contains the different classes we need to build the compiler. Previously, Lexer was builded. The lexer, lets tokenize an input (test case) writen in C++ code. That works perfect.


>[!NOTE]
   >
   >Parser only needs be modified to recognize correctly the class constructos, the for loop without initialization, the arrays declaration and one line comments.

The checker is so important for this compiler. With it, we can check:

1. Build the Symbols table (you can use ChainMap).
2. Validate that any Identifier must be declared beforehand.
3. Add a cast instruction.
4. Validate that any expression must have type compatibility.
5. Validate that there is a main function (gateway).
6. Implement the iread, fread (scanf) function
7. Implement the FOR instruction.
8. Validate that the BREAK and CONTINUE instructions are used within WHILE/FOR instructions.

# AST Visualization
For the AST visualization, the class will create an file with instruction with DOT format. You can use: [https://dreampuf.github.io/GraphvizOnline/#digraph%20G%20%7B%0D%0Anode0%20%5Blabel%3D"Program"%5D%3B%0D%0Anode1%20%5Blabel%3D"VarDeclStmt"%5D%3B%0D%0Anode0%20->%20node1%3B%0D%0Anode2%20%5Blabel%3D"type_%20%3D%20int"%5D%3B%0D%0Anode1%20->%20node2%3B%0D%0Anode3%20%5Blabel%3D"identifier%20%3D%20main"%5D%3B%0D%0Anode1%20->%20node3%3B%0D%0Anode4%20%5Blabel%3D"expr%20%3D%202"%5D%3B%0D%0Anode1%20->%20node4%3B%0D%0A%7D] This tool works good, and it'll show you the Tree with his nodes.

# To test and look the AST
You can use 
```
python CppASTVisualizer.py 
```
