from CppLexer import CppLexer
from CppAST import *
from rich import print
import sly

class CppParser(sly.Parser):
    debugfile = 'MiniCCParser.txt'

    def __init__(self):
        self.current_class = None

    #Lista de tokens
    tokens = CppLexer.tokens

    #Precedencia de operadores

    precedence = (
        ('right', ELSE), #type: ignore
        ('right', ASSIGN), #type: ignore
        ('right', ADDEQ), #type: ignore
        ('right', MINEQ), #type: ignore
        ('right', TIMESEQ), #type: ignore
        ('right', DIVIDEEQ), #type: ignore
        ('right', MODULEEQ), #type: ignore
        ('left', OR), #type: ignore
        ('left', AND), #type: ignore
        ('left', EQUAL, NOT_EQUAL), #type: ignore
        ('left', LESS, LESS_EQUAL, GREATER, GREATER_EQUAL), #type: ignore
        ('left', PLUS, MINUS), #type: ignore
        ('left', TIMES, DIVIDE, MOD), #type: ignore
        ('right', UNARY, NOT) #type: ignore
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

    @_("IF '(' expr ')' statement %prec ELSE") # type: ignore
    def if_stmt(self, p):
        ''' IF '(' expr ')' stmt %prec ELSE  Sin ELSE
        Tiene menos precedencia que ELSE, si el parser
        se encuentra con un ELSE, se asocia con el IF más cercano'''
        return IfStmt(p.expr, p.stmt)

    @_("IF '(' expr ')' statement ELSE statement") # type: ignore
    def if_stmt(self, p):
        ''' IF '(' expr ')' stmt ELSE stmt  Con ELSE, no se necesita
         una precedencia especial porque ya incluye el ELSE'''
        return IfStmt(p.expr, p.stmt0, p.stmt1)
    
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
    
    # Expresiones de asignación
    @_("expr ASSIGN expr", #type: ignore
       "expr ADDEQ expr",
       "expr MINEQ expr",
       "expr TIMESEQ expr",
       "expr DIVIDEEQ expr",
       "expr MODULEEQ expr") #type: ignore
    def expr(self, p):
        if isinstance(p.expr0, VarExpr):
            return AssignExpr(p[1], p.expr0.ident, p.expr1)
        elif isinstance(p.expr0, Get):
            return Set(p.expr0.obj, p.expr0.ident, p.expr1)
        else:
            raise SyntaxError(f"{p.lineno}: Error de sintaxis. Imposible asignar a la expresión {p.expr0}")
    
    # Expresiones lógicas
    @_("expr OR expr", #type: ignore
       "expr AND expr",
       "expr NOT expr")
    def expr(self, p):
        return LogicalExpr(p[1], p.expr0, p.expr1)
    
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

    # Parametros y argumentos
    @_("TYPE_SPECIFIER IDENTIFIER { COMMA TYPE_SPECIFIER IDENTIFIER }") #type: ignore
    def params(self, p):
        return (p.TYPE_SPECIFIER0, p.IDENTIFIER0) + (p.TYPE_SPECIFIER1, p.IDENTIFIER1)
    
    @_("expr { COMMA expr }") #type: ignore
    def args(self, p):
        return [ p.expr0 ] + p.expr1
    


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

        