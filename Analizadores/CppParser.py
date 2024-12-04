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

from CppLexer import CppLexer
from CppAST import *
from rich import print
import sly

class CppParser(sly.Parser):
    debugfile = 'MiniCCParser.txt'

    def __init__(self, ctxt):
        self.current_class = None
        self.ctxt=ctxt

    #Lista de tokens
    tokens = CppLexer.tokens

    #Precedencia de operadores

    precedence = (
        ('left', PLUSPLUS), #type: ignore
        ('left', MINUSMINUS), #type: ignore
        ('right', ELSE), #type: ignore
        ('right', ADDEQ), #type: ignore
        ('right', MINEQ), #type: ignore
        ('right', TIMESEQ), #type: ignore
        ('right', DIVIDEEQ), #type: ignore
        ('right', MODULEEQ), #type: ignore
        ('right', ASSIGN), #type: ignore
        ('left', OR), #type: ignore
        ('left', AND), #type: ignore
        ('left', EQUAL, NOT_EQUAL), #type: ignore
        ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL), #type: ignore
        ('left', PLUS, MINUS), #type: ignore
        ('left', TIMES, DIVIDE, MOD), #type: ignore
        ('right', UNARY, NOT), #type: ignore
    )

    #Reglas de la gramática

    # Un programa es una o más declaraciones
    @_(" { declaration }") #type: ignore
    def program(self, p):
        return Program(p.declaration)
    
    # Una declaración puede ser una declaración de clase, función, variable o sentencia
    @_("class_decl", "func_decl", "var_decl", "statement") #type: ignore
    def declaration(self, p):
        return p[0]
    
    # Declaración de clases
    @_("CLASS IDENTIFIER LEFT_BRACE { class_members } RIGHT_BRACE") #type: ignore
    def class_decl(self, p):
        self.current_class = p.IDENTIFIER
        print(f"[DEBUG] current_class set to: {self.current_class}")
        return ClassDeclStmt(p.IDENTIFIER, p.class_members)

    
    #Cuerpo de la clase
    @_("var_decl", "func_decl", "constructor_decl", "destructor_decl") #type: ignore
    def class_members(self, p):
        return p[0]
    
    # Declaración de constructores
    @_("IDENTIFIER LEFT_PAREN [ params ] RIGHT_PAREN compound_stmt") #type: ignore
    def constructor_decl(self, p):
        if self.current_class is None:
            raise SyntaxError(f"Error {p.lineno}: No se puede declarar un constructor fuera de una clase")
        elif p.IDENTIFIER != self.current_class:
            raise SyntaxError(f"Error {p.lineno}: '{p.IDENTIFIER}' no coincide con el nombre de la clase '{self.current_class}'")
        return ConstructorDeclStmt(p.IDENTIFIER, p.params, p.compound_stmt)
  
    # Declaración de destructores
    @_("DESTRUCTOR LEFT_PAREN RIGHT_PAREN compound_stmt") #type: ignore
    def destructor_decl(self, p):
        return DestructorDeclStmt(p.DESTRUCTOR[1:], p.compound_stmt)  # p.DESTRUCTOR[1:] omite el '~'

    
    # Declaración de funciones
    @_("TYPE_SPECIFIER IDENTIFIER LEFT_PAREN [ params ] RIGHT_PAREN compound_stmt") #type: ignore
    def func_decl(self, p):
        return FuncDeclStmt(p.TYPE_SPECIFIER, p.IDENTIFIER, p.params, p.compound_stmt)
    
    # Declaración de variables
    @_("TYPE_SPECIFIER IDENTIFIER [ ASSIGN expr ] SEMICOLON") #type: ignore
    def var_decl(self, p):
        return VarDeclStmt(p.TYPE_SPECIFIER, p.IDENTIFIER, p.expr)
    
    # Instrucciones
    @_("expr_stmt", #type: ignore
       "for_stmt",
       "while_stmt",
       "if_stmt",
       "return_stmt",
       "break_stmt",
       "continue_stmt",
       "size_stmt",
       "printf_stmt",
       "compound_stmt") #type: ignore
    def statement(self, p):
        return p[0]
    
    # Expresiones
    @_("expr SEMICOLON") #type: ignore
    def expr_stmt(self, p):
        return ExprStmt(p.expr)

    # Instruccion for
    @_("FOR LEFT_PAREN for_initialize [ expr ] SEMICOLON [ expr ] RIGHT_PAREN statement") #type: ignore
    def for_stmt(self, p):
        return ForStmt(p.for_initialize, p.expr0, p.expr1, p.statement)

    # Ciclo for sin inicialización
    @_("FOR LEFT_PAREN SEMICOLON [ expr ] SEMICOLON [ expr ] RIGHT_PAREN statement") #type: ignore
    def for_stmt(self, p):
        return ForStmt(None, p.expr0, p.expr1, p.statement)
    

    # Inicialización de una variable en un ciclo for 
    @_("var_decl", "expr_stmt") #type: ignore
    def for_initialize(self, p):
        return p[0]
    
    # Sentencias de control
    @_("CONTINUE SEMICOLON") #type: ignore
    def continue_stmt(self, p):
        return ContinueStmt(p[0])
    
    @_("BREAK SEMICOLON") #type: ignore
    def break_stmt(self, p):
        return BreakStmt(p[0])
    
    # Regla para manejar la ambigüedad del "Else colgante"

    @_("IF LEFT_PAREN expr RIGHT_PAREN statement %prec ELSE")  # type: ignore
    def if_stmt(self, p):
        ''' IF '(' expr ')' statement %prec ELSE 
            Sin ELSE: Tiene menos precedencia que ELSE.
            Si el parser encuentra un ELSE, se asocia con el IF más cercano.
        '''
        return IfStmt(p.expr, p.statement)

    @_("IF LEFT_PAREN expr RIGHT_PAREN statement ELSE statement")  # type: ignore
    def if_stmt(self, p):
        ''' IF '(' expr ')' statement ELSE statement  
            Con ELSE: No necesita precedencia especial porque incluye el ELSE.
        '''
        return IfStmt(p.expr, p.statement0, p.statement1)

    
    # Sentencia printf
    @_("PRINTF LEFT_PAREN expr RIGHT_PAREN SEMICOLON") #type: ignore
    def printf_stmt(self, p):
        return PrintfStmt(p.expr)
    
    # Sentencia return
    @_("RETURN [ expr ] SEMICOLON") #type: ignore
    def return_stmt(self, p):
        return ReturnStmt(p.expr)
    
    # Sentencia while
    @_("WHILE LEFT_PAREN expr RIGHT_PAREN statement")   #type: ignore
    def while_stmt(self, p):
        return WhileStmt(p.expr, p.statement)
    
    # Instrucciones compuestas
    @_("LEFT_BRACE { declaration } RIGHT_BRACE") #type: ignore
    def compound_stmt(self, p):
        return CompoundStmt(p.declaration)
    
    
    # Sentencia size
    @_("SIZE LEFT_PAREN expr RIGHT_PAREN SEMICOLON") #type: ignore
    def size_stmt(self, p):
        return SizeStmt(p.expr)
    
    
    # Expresiones relacionales
    @_("expr PLUS expr", #type: ignore
       "expr MINUS expr",
       "expr TIMES expr",
       "expr DIVIDE expr",
       "expr MOD expr",
       "expr EQUAL expr",
       "expr NOT_EQUAL expr",
       "expr LESS expr",
       "expr LESS_EQUAL expr",
       "expr GREATER expr",
       "expr GREATER_EQUAL expr")
    def expr(self, p):
        return BinaryOpExpr(p[1], p.expr0, p.expr1)
    
    # Expresiones lógicas
    @_("expr OR expr", #type: ignore
       "expr AND expr",
       "expr NOT expr")
    def expr(self, p):
        return LogicalExpr(p[1], p.expr0, p.expr1)
    
    # Expresiones de asignación
    @_("expr ASSIGN expr", #type: ignore
       "expr ADDEQ expr",
       "expr MINEQ expr",
       "expr TIMESEQ expr",
       "expr DIVIDEEQ expr",
       "expr MODULEEQ expr") #type: ignore
    def expr(self, p):
        if isinstance(p.expr0, VarExpr):
            return AssignExpr(p[1], p.expr0.name, p.expr1)
        elif isinstance(p.expr0, Get):
            return Set(p.expr0.obj, p.expr0.name, p.expr1)
        else:
            raise SyntaxError(f"{p.lineno}: Error de sintaxis. Imposible asignar a la expresión {p.expr0}")
    
    # Expresiones unarias
    @_("factor") #type: ignore
    def expr(self, p):
        return p.factor
    
    # Factores
    @_("BOOL_LITERAL", #type: ignore
       "INT_LITERAL",
       "FLOAT_LITERAL",
       "STRING_LITERAL")
    def factor(self, p):
        return LiteralExpr(p[0])
    
    # Factor NIL
    @_("NIL") #type: ignore
    def factor(self, p):
        return LiteralExpr(None)
    
    # Factor NULL
    @_("NULL") #type: ignore
    def factor(self, p):
        return NullStmt()
    
    # Factor THIS
    @_("THIS") #type: ignore
    def factor(self, p):
        return ThisExpr()
    
    # Factor de acceso a miembros
    @_("IDENTIFIER") #type: ignore
    def factor(self, p):
        return VarExpr(p.IDENTIFIER)
    
    # Factor de acceso a miembros
    @_("factor LEFT_PAREN [ args ] RIGHT_PAREN") #type: ignore
    def factor(self, p):
        return CallExpr(p.factor, p.args)
    
    # Manejo del menos unario
    @_("MINUS factor %prec UNARY", #type: ignore
       "NOT factor %prec UNARY") #type: ignore
    def factor(self, p):
        return UnaryOpExpr(p[0], p.factor)
    
    # Añadido operador ++ y -- en notación prefija y postfija
    @_("factor PLUSPLUS", #type: ignore
       "factor MINUSMINUS")
    def factor(self, p):
        return AssignPostFix(p[1], p.factor)
    
    @_("PLUSPLUS factor", #type: ignore
       "MINUSMINUS factor")
    def factor(self, p):
        return AssignPreFix(p[0], p.factor)
    
    # **********************************************************

    # Parametros y argumentos
    # @_("TYPE_SPECIFIER IDENTIFIER { COMMA TYPE_SPECIFIER IDENTIFIER }") #type: ignore
    # def params(self, p):
    #     return (p.TYPE_SPECIFIER0, p.IDENTIFIER0) + (p.TYPE_SPECIFIER1, p.IDENTIFIER1)

    # @_("TYPE_SPECIFIER IDENTIFIER { COMMA TYPE_SPECIFIER IDENTIFIER }")  # type: ignore
    # def params(self, p):
    #     params = [Parameter(p.TYPE_SPECIFIER0, p.IDENTIFIER0)]
    #     for i in range(1, len(p.TYPE_SPECIFIER1)):
    #         params.append(Parameter(p.TYPE_SPECIFIER1[i - 1], p.IDENTIFIER1[i - 1]))
    #     return params

    @_("TYPE_SPECIFIER IDENTIFIER { COMMA TYPE_SPECIFIER IDENTIFIER }")  # type: ignore
    def params(self, p):
        params = [Parameter(p.TYPE_SPECIFIER0, p.IDENTIFIER0)]
        for i in range(0, len(p.TYPE_SPECIFIER1)):
            params.append(Parameter(p.TYPE_SPECIFIER1[i], p.IDENTIFIER1[i]))
        return params


    
    @_("expr { COMMA expr }") #type: ignore
    def args(self, p):
        return [ p.expr0 ] + p.expr1
    


def error(self, p):
        if p:
            print(f"Línea {p.lineno}: Error de sintaxis en el token '{p.value}' ({p.type})")
            self.errok()
        else:
            print("Error de sintaxis en EOF")
    
# def parse(source):
#     lexer = CppLexer()
#     parser = CppParser()
#     parser.parse(lexer.tokenize(source))

# if __name__ == '__main__':
#     import sys

#     if len(sys.argv) != 2:
#         print(f"[blue]Usage CppLexer.py textfile[/blue]")
#         exit(1)

#     parse(open(sys.argv[1], encoding='utf-8').read())
#Fin del archivo CppParser.py

        