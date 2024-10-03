'''

****************************************** ANALIZADOR SINTÁCTICO PARA MINI C++ ******************************************

* Autor: Juan Pablo Sánchez Zapata
* Fecha: 2024-10-03
* Descripción: Implementación de un analizador sintáctico para soportar los tokens para el lenguaje C++ (Mini C++).
* El analizador sintáctico se encarga de crear reglas para los tokens que conforman el lenguaje C++.
* Se utiliza la librería sly para la implementación del analizador sintáctico.
* Se utiliza la librería rich para la impresión de los tokens identificados.
* Se importa la lista de tokens del archivo CppLexer.py para trabajar con estos.

----> Se soluciona el problema del shift/reduce en la gramática de Mini-C++ por diferentes motivos


* Nota importante: Para solucionar el problema de shift/reduce se modifica la precedencia de los tokens. 
Para manejar la sentencia IF, ELSE, el conflicto de shift/reduce ocurre porque el parser no sabe si 
debe reducir un if sin else o desplazar el else cuando lo encuentra en la entrada. 
Con la solución planteada, al darle mayor precedencia al else, el parser siempre elegirá desplazar 
el else y asociarlo con el if más cercano, eliminando el conflicto de shift/reduce.

-------------------------------------------------------------------------------------------------------------------------
* SALVEDADES: Se usa # type: ignore para ocultar los errores de tipo en la librería sly.

'''

#Librerías
from rich import print
from CppLexer import CppLexer
from test_cases import test_cases
from CppAST import *

import sly

#Definición de la clase CppParser

class CppParser(sly.Parser):
    debugfile = 'MiniCCParser.txt'

    tokens = CppLexer.tokens

    # Definir cada regla de la gramática

    precedence = (
        ('right', ELSE), #type: ignore
        ('right', ASSIGN), #type: ignore
        ('left', OR), #type: ignore
        ('left', AND), #type: ignore
        ('left', EQUAL, NOT_EQUAL), #type: ignore
        ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL), #type: ignore
        ('left', PLUS, MINUS), #type: ignore
        ('left', TIMES, DIVIDE, MOD), #type: ignore
        ('right', UNARY, NOT) #type: ignore
    )
    
    @_("decl_list")     #type: ignore
    def program(self, p):
        '''program ::= decl+'''
        return Program(p.decl_list)
    
    @_("decl_list decl")  #type: ignore
    def decl_list(self, p):
        '''decl_list ::= decl+'''
        return p.decl_list + [p.decl]
    
    @_("decl")  #type: ignore
    def decl_list(self, p):
        '''decl_list ::= decl'''
        return [p.decl]

    @_("var_decl", "func_decl", "class_decl")    #type: ignore
    def decl(self, p):
        '''decl ::= var_decl
                 | func_decl
                 | class_decl'''
        return p[0]
    
    @_("TYPE_SPECIFIER")  #type: ignore
    def type_spec(self, p):
        '''type_spec ::= TYPE_SPECIFIER'''
        return p[0]
        
    @_("type_spec IDENTIFIER SEMICOLON")   #type: ignore
    def var_decl(self, p):
        '''var_decl ::= TYPE_SPECIFIER IDENTIFIER SEMICOLON'''
        return VarDeclStmt(p.type_spec, p.IDENTIFIER)

    @_("type_spec IDENTIFIER LEFT_BRACKET RIGHT_BRACKET SEMICOLON")   #type: ignore
    def var_decl(self, p):
        '''var_decl ::= TYPE_SPECIFIER IDENTIFIER LEFT_BRACKET RIGHT_BRACKET SEMICOLON'''
        return VarDeclStmt(p.type_spec, p.IDENTIFIER)

    @_("type_spec IDENTIFIER LEFT_PAREN params RIGHT_PAREN compound_stmt")   #type: ignore
    def func_decl(self, p):
        '''func_decl ::= type_spec IDENTIFIER LEFT_PAREN params RIGHT_PAREN compound_stmt'''
        return FuncDeclStmt(p.type_spec, p.IDENTIFIER, p.params, p.compound_stmt)
    
    @_("param_list", "empty")   #type: ignore
    def params(self, p):
        '''params ::= param_list
                   | VOID'''
        return p.param_list if p.param_list else []
    
    @_("param { COMMA param }")  #type: ignore
    def param_list(self, p):
        '''param_list ::= param (COMMA param)*'''
        return p.param_list + [p.param]
    
    @_("TYPE_SPECIFIER IDENTIFIER")  #type: ignore
    def param(self, p):
        '''param ::= TYPE_SPECIFIER IDENTIFIER'''
        return VarDeclStmt(p.TYPE_SPECIFIER, p.IDENTIFIER)
    
    @_("TYPE_SPECIFIER IDENTIFIER LEFT_BRACKET RIGHT_BRACKET")   #type: ignore
    def param(self, p):
        '''param ::= TYPE_SPECIFIER IDENTIFIER LEFT_BRACKET RIGHT_BRACKET'''
        return ArrayAssignmentExpr(p[0], p[1])

    @_("LEFT_BRACE local_decls stmt_list RIGHT_BRACE")   #type: ignore
    def compound_stmt(self, p):
        '''compound_stmt ::= LEFT_BRACE local_decls stmt_list RIGHT_BRACE'''
        return p.stmt_list
    
    @_("local_decl","empty")  #type: ignore
    def local_decls(self, p):
        '''local_decls ::= local_decl*
                         | '''
        return p.local_decl if p.local_decl else []
    
    @_("TYPE_SPECIFIER IDENTIFIER SEMICOLON")   #type: ignore
    def local_decl(self, p):
        '''local_decl ::= TYPE_SPECIFIER IDENTIFIER SEMICOLON'''
        return VarDeclStmt(p.TYPE_SPECIFIER, p.IDENTIFIER)
    

    @_("TYPE_SPECIFIER IDENTIFIER LEFT_BRACKET RIGHT_BRACKET SEMICOLON")  #type: ignore
    def local_decl(self, p):
        '''local_decl ::= TYPE_SPECIFIER IDENTIFIER LEFT_BRACKET RIGHT_BRACKET SEMICOLON'''
        return VarDeclStmt(p.TYPE_SPECIFIER, p.IDENTIFIER)
    
    @_("{ stmt }")   #type: ignore
    def stmt_list(self, p):
        '''stmt_list ::= stmt*'''
        return p.stmt_list

    @_("expr_stmt", "compound_stmt", "if_stmt", "while_stmt", "return_stmt", #type: ignore
       "break_stmt", "continue_stmt", "size_stmt") 
    def stmt(self, p):
        '''stmt ::= expr_stmt
                 | compound_stmt
                 | if_stmt
                 | while_stmt
                 | return_stmt
                 | break_stmt
                 | printf_stmt
                 | continue_stmt
                 | size_stmt'''
        return p[0]
    
    @_("expr SEMICOLON")   #type: ignore
    def expr_stmt(self, p):
        '''expr_stmt ::= expr SEMICOLON'''
        return p.expr
    
    @_("SEMICOLON")   #type: ignore
    def expr_stmt(self, p):
        '''expr_stmt ::= SEMICOLON'''
        return None
    
    # Regla para manejar la ambigüedad de la gramática "Else colgante"

    @_("IF '(' expr ')' stmt %prec ELSE") # type: ignore
    def if_stmt(self, p):
        ''' IF '(' expr ')' stmt %prec ELSE  Sin ELSE
        Tiene menos precedencia que ELSE, si el parser
        se encuentra con un ELSE, se asocia con el IF más cercano'''
        return IfStmt(p.expr, p.stmt)

    @_("IF '(' expr ')' stmt ELSE stmt") # type: ignore
    def if_stmt(self, p):
        ''' IF '(' expr ')' stmt ELSE stmt  Con ELSE, no se necesita
         una precedencia especial porque ya incluye el ELSE'''
        return IfStmt(p.expr, p.stmt0, p.stmt1)
    
    @_("WHILE LEFT_PAREN expr RIGHT_PAREN stmt")   #type: ignore
    def while_stmt(self, p):
        '''while_stmt ::= WHILE LEFT_PAREN expr RIGHT_PAREN stmt'''
        return WhileStmt(p.expr, p.stmt)

    @_("RETURN SEMICOLON")   #type: ignore
    def return_stmt(self, p):
        '''return_stmt ::= RETURN SEMICOLON'''
        return ReturnStmt()
    
    @_("RETURN expr SEMICOLON")   #type: ignore
    def return_stmt(self, p):
        '''return_stmt ::= RETURN expr SEMICOLON'''
        return ReturnStmt(p.expr)
    
    @_("BREAK SEMICOLON")   #type: ignore
    def break_stmt(self, p):
        '''break_stmt ::= BREAK SEMICOLON'''
        return BreakStmt()
    
    @_("PRINTF LEFT_PAREN STRING_LITERAL { COMMA expr } RIGHT_PAREN SEMICOLON")   #type: ignore
    def printf_stmt(self, p):
        '''printf_stmt ::= PRINTF LEFT_PAREN STRING_LITERAL (COMMA expr)* RIGHT_PAREN SEMICOLON'''
        return PrintfStmt(p.STRING_LITERAL, p.expr)

    @_("printf_stmt")   #type: ignore
    def printf_call(self, p):
        '''printf_call ::= PRINTF LEFT_PAREN STRING_LITERAL (COMMA expr)* RIGHT_PAREN'''
        return p.printf_stmt
    
    @_("CONTINUE SEMICOLON")   #type: ignore
    def continue_stmt(self, p):
        '''continue_stmt ::= CONTINUE SEMICOLON'''
        return ContinueStmt()
    
    @_("SIZE LEFT_PAREN expr RIGHT_PAREN SEMICOLON")   #type: ignore
    def size_stmt(self, p):
        '''size_stmt ::= SIZE LEFT_PAREN expr RIGHT_PAREN SEMICOLON'''
        return SizeStmt(p.expr)
    
    @_("IDENTIFIER ASSIGN expr")   #type: ignore
    def expr(self, p):
        '''expr ::= IDENTIFIER ASSIGN expr'''
        return VarAssignmentExpr(p.IDENTIFIER, p.expr)
    
    @_("IDENTIFIER LEFT_BRACKET expr RIGHT_BRACKET ASSIGN expr")   #type: ignore
    def expr(self, p):
        '''expr ::= IDENTIFIER LEFT_BRACKET expr RIGHT_BRACKET ASSIGN expr'''
        return ArrayAssignmentExpr(p.IDENTIFIER, p.expr0, p.expr1)

    @_("expr OR expr",  #type: ignore
       "expr AND expr", 
       "expr EQUAL expr", 
       "expr NOT_EQUAL expr",
       "expr LESS expr",
       "expr LESS_EQUAL expr",
       "expr GREATER expr",
       "expr GREATER_EQUAL expr",
       "expr PLUS expr",
       "expr MINUS expr",
       "expr TIMES expr",
       "expr DIVIDE expr",
       "expr MOD expr")
    def expr(self, p):
        '''expr ::= expr OR expr
                 | expr AND expr
                 | expr EQUAL expr
                 | expr NOT expr
                 | expr LESS expr
                 | expr LESS_EQUAL expr
                 | expr GREATER expr
                 | expr GREATER_EQUAL expr
                 | expr PLUS expr
                 | expr MINUS expr
                 | expr TIMES expr
                 | expr DIVIDE expr
                 | expr MOD expr'''
        return BinaryOpExpr(p[1], p.expr0, p.expr1)
    
    @_("NOT expr", "MINUS expr %prec UNARY", "PLUS expr %prec UNARY")   #type: ignore
    def expr(self, p):
        '''expr ::= NOT expr
                 | MINUS expr
                 | PLUS expr '''
        return UnaryOpExpr(p[0], p.expr)

    @_("LEFT_PAREN expr RIGHT_PAREN")   #type: ignore
    def expr(self, p):
        '''expr ::= LEFT_PAREN expr RIGHT_PAREN'''
        return p.expr
    
    @_("IDENTIFIER")  #type: ignore
    def expr(self, p):
        '''expr ::= IDENTIFIER'''
        return VarExpr(p.IDENTIFIER)
    
    @_("IDENTIFIER LEFT_BRACKET expr RIGHT_BRACKET")   #type: ignore
    def expr(self, p):
        '''expr ::= IDENTIFIER LEFT_BRACKET expr RIGHT_BRACKET'''
        return ArrayLookupExpr(p.IDENTIFIER, p.expr)
    
    @_("IDENTIFIER LEFT_PAREN args RIGHT_PAREN")   #type: ignore
    def expr(self, p):
        '''expr ::= IDENTIFIER LEFT_PAREN args RIGHT_PAREN'''
        return CallExpr(p.IDENTIFIER, p.args)
    
    @_("IDENTIFIER DOT SIZE")   #type: ignore
    def expr(self, p):
        '''expr ::= IDENTIFIER DOT SIZE'''
        return ArraySizeExpr(p.IDENTIFIER)

    @_("BOOL_LITERAL", "INT_LITERAL", "FLOAT_LITERAL", "STRING_LITERAL")   #type: ignore
    def expr(self, p):
        '''expr ::= BOOL_LITERAL
                 | INT_LITERAL
                 | FLOAT_LITERAL
                 | STRING_LITERAL'''
        return ConstExpr(p[0])
    
    @_("NEW TYPE_SPECIFIER LEFT_BRACKET expr RIGHT_BRACKET")   #type: ignore
    def expr(self, p):
        '''expr ::= NEW TYPE_SPECIFIER LEFT_BRACKET expr RIGHT_BRACKET'''
        return NewArrayExpr(p.TYPE_SPECIFIER, p.expr)
    
    @_("printf_call")   #type: ignore
    def expr(self, p):
        '''expr ::= printf_call'''
        return p.printf_call
    
    @_("arg_list", "empty")  #type: ignore
    def args(self, p):
        '''args ::= arg_list
                 | '''
        return p.arg_list if p.arg_list else []
    
    @_("expr [ COMMA expr ]")   #type: ignore
    def arg_list(self, p):
        '''arg_list ::= expr (COMMA expr)*'''
        return p.arg_list + [p.expr]
    
    @_("CLASS IDENTIFIER class_content")   #type: ignore
    def class_decl(self, p):
        '''class_decl ::= CLASS IDENTIFIER class_content'''
        return ClassDeclStmt(p.IDENTIFIER, p.class_content)
    
    @_("CLASS IDENTIFIER COLON inheritance_list class_content")  #type: ignore
    def class_decl(self, p):
        '''class_decl ::= CLASS IDENTIFIER COLON inheritance_list class_content'''
        return ClassDeclStmt(p.IDENTIFIER, p.class_content, p.inheritance_list)
    
    @_("LEFT_BRACE [ members_decl ] RIGHT_BRACE SEMICOLON")   #type: ignore
    def class_content(self, p):
        '''class_content ::= LEFT_BRACE members_decl RIGHT_BRACE SEMICOLON'''
        return p.members_decl if p.members_decl else []


    @_("inheritance [ COMMA inheritance ]")   #type: ignore
    def inheritance_list(self, p):
        '''inheritance_list ::= inheritance (COMMA inheritance)*'''
        return p.inheritance_list + [p.inheritance]

    @_("access_specifier IDENTIFIER")   #type: ignore
    def inheritance(self, p):
        '''inheritance ::= ACCESS_SPECIFIER IDENTIFIER'''
        return p.access_specifier, p.IDENTIFIER
    
    @_("IDENTIFIER")   #type: ignore
    def inheritance(self, p):
        '''inheritance ::= IDENTIFIER'''
        return None, p.IDENTIFIER
    
    @_("ACCESS_SPECIFIER")   #type: ignore
    def access_specifier(self, p):
        '''access_specifier ::= PRIVATE
                            | PUBLIC
                            | PROTECTED'''
        return p[0]


    @_("access_specifier COLON members_list")   #type: ignore
    def members_decl(self, p):
        '''members_decl ::= ACCESS_SPECIFIER COLON members_list'''
        return p.access_specifier, p.members_list


    @_("destructor_decl", "constructor_decl", "func_decl", "var_decl")   #type: ignore
    def members_list(self, p):
        '''members_list ::= destructor_decl
                         | constructor_decl
                         | func_decl
                         | var_decl'''
        return p[0]
    
    @_("IDENTIFIER LEFT_PAREN params RIGHT_PAREN compound_stmt")   #type: ignore
    def constructor_decl(self, p):
        '''constructor_decl ::= IDENTIFIER LEFT_PAREN params RIGHT_PAREN compound_stmt'''
        return FuncDeclStmt("void", p.IDENTIFIER, p.params, p.compound_stmt)
    
    @_("'~' IDENTIFIER LEFT_PAREN RIGHT_PAREN compound_stmt")   #type: ignore
    def destructor_decl(self, p):
        '''destructor_decl ::= '~' IDENTIFIER LEFT_PAREN RIGHT_PAREN compound_stmt'''
        return FuncDeclStmt("void", p.IDENTIFIER, [], p.compound_stmt)


    @_("")  #type: ignore
    def empty(self, p):
        '''empty ::= '''
        return NullStmt()

    def error(self, p):
        if p:
            print(f"Línea {p.lineno}: Error de sintaxis en el token '{p.value}' ({p.type})")
            self.errok()
        else:
            print("Error de sintaxis en EOF")
    
def parse(source):
    lexer = CppLexer()
    parser = CppParser()
    parser.parse(lexer.tokenize(source))

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print(f"[blue]Usage CppLexer.py textfile[/blue]")
        exit(1)

    parse(open(sys.argv[1], encoding='utf-8').read())
#Fin del archivo CppParser.py

        
    