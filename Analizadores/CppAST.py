'''
Estructura del AST (Básica)

Statement
    |
    +--- NullStmt
    |
    +--- ExprStmt
    |
    +--- IfStmt
    |
    +--- WhileStmt
    |
    +--- ReturnStmt
    |
    +--- BreakStmt
    |
    +--- ContinueStmt
    |
    +--- SizeStmt
    |
    +--- PrintfStmt
    |
    +--- FuncDeclStmt
    |
    +--- VarDeclStmt
    |
    +--- ClassDeclStmt
    
Expression

    |
    +--- ConstExpr (int, float, bool, string)
    |
    +--- NewArrayExpr (Arreglos recién creados)
    |
    +--- CallExpr (Llamadas a funciones)
    |
    +--- VarExpr (Variables en lado derecho)
    |
    +--- ArrayLookupExpr (Acceso a arreglos, contenido celda arreglo)
    |
    +--- FieldAccessExpr (Acceso a campos de clase)
    |
    +--- UnaryOpExpr (Operadores unarios: !, +, -)
    |
    +--- BinaryOpExpr (Operadores binarios: ||, &&, ==, !=, <, <=, >, >=, +, -, *, /, %)
    |
    +--- VarAssignmentExpr (Asignaciones var = expr)
    |
    +--- ArrayAssignmentExpr (Asignaciones var[expr] = expr)
    |
    +--- IntToFloatExpr (Conversión de entero a flotante)
    |
    +--- ArraySizeExpr (Tamaño de un arreglo)

'''

from dataclasses import dataclass, field
from multimethod import multimeta
from typing import List, Union

'''
**************** CLASES ABSTRACTAS ****************

'''

@dataclass
class Visitor(metaclass=multimeta): # Clase abstracta del patrón Visitor
    pass

@dataclass
class ASTNode:
    def accept(self, v:Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Expression(ASTNode):
    pass

'''
**************** CLASES CONCRETAS ****************

'''

@dataclass
class Program(Statement):
    stmts: List[Statement] = field(default_factory=list)

@dataclass
class NullStmt(Statement):
    pass

@dataclass
class ExprStmt(Statement):
    expr: Expression

@dataclass
class IfStmt(Statement):
    cond: Expression
    then_stmt: Statement
    else_stmt: Statement = None #Hace que el else sea opcional, al poder ser none

@dataclass
class WhileStmt(Statement):
    cond: Expression
    body_stmt: Statement

@dataclass
class ReturnStmt(Statement):
    expr: Expression = None

@dataclass
class BreakStmt(Statement):
    pass

@dataclass
class ContinueStmt(Statement):
    pass

@dataclass
class SizeStmt(Statement):
    expr: Expression

@dataclass
class PrintfStmt(Statement):
    fmt: str #Formato de la cadena
    args: List[Expression] = field(default_factory=list) #Argumentos de la cadena

@dataclass
class FuncDeclStmt(Statement):
    type_: str
    identifier: str
    params: List[str] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)

    @property
    def return_type(self):
        return self.type_

@dataclass
class VarDeclStmt(Statement):
    type_: str
    identifier: str
    expr: Expression = None

    @property
    def return_type(self):
        return self.type_

@dataclass
class ClassDeclStmt(Statement):
    identifier: str
    fields: List[VarDeclStmt] = field(default_factory=list)
    methods: List[FuncDeclStmt] = field(default_factory=list)


'''
**************** EXPRESIONES ****************

'''

@dataclass
class ConstExpr(Expression):
    value: Union[int, float, bool, str]

@dataclass
class NewArrayExpr(Expression):
    type_: str
    size: Expression

    @property
    def return_type(self):
        return self.type_

@dataclass
class CallExpr(Expression):
    identifier: str
    args: List[Expression] = field(default_factory=list)

@dataclass
class VarExpr(Expression):
    identifier: str

@dataclass
class ArrayLookupExpr(Expression): #Acceso a arreglos
    array: Expression
    index: Expression

@dataclass
class FieldAccessExpr(Expression): #Acceso a campos de clase
    expr: Expression
    field: str

@dataclass
class UnaryOpExpr(Expression):
    op: str
    expr: Expression

@dataclass
class BinaryOpExpr(Expression):
    op: str
    left: Expression
    right: Expression

@dataclass
class VarAssignmentExpr(Expression):
    identifier: str
    expr: Expression

@dataclass
class ArrayAssignmentExpr(Expression):
    array: Expression
    index: Expression
    expr: Expression

@dataclass
class IntToFloatExpr(Expression):
    expr: Expression

@dataclass
class ArraySizeExpr(Expression):
    array: Expression




