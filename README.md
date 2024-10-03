# Compiler-for-Mini-C-
This project wants to make a compiler for the programming language C++, but not all the concepts about it, but some basic and fundamental subjetcs of the language.

# Folder

About the 'Analizadores' folder, it can tell that it's contains the different classes we need to build the compiler. Previously, Lexer was builded. The lexer, lets tokenize an input (test case) writen in C++ code. That works perfect.

For parser, and the AST creation, it have problems. With the parser, the grammar rules was defined, however, to create the AST is complicated because, when the programm try to recognize the different expressions or statements, only recognize an expression like this: 'TYPE_SPECIFIER IDENTIFIER SEMICOLON'. Then an expression like: 'int x;' is recognized but other distintc, for example, an assignment like: 'int x = 2;' print sintax errors.  In the future, that will be fixed with the next commit. For this part, we already have all the needed classes and the class to create the AST works. But, the problem maybe is in the parser with the grammar rules.
