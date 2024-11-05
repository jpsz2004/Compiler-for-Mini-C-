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
    def accept(self, v:Visitor):
        return v.visit(self)

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class Declaration(Statement):
    pass

'''
**************** CLASES CONCRETAS ****************

'''


@dataclass
class FuncDeclStmt(Declaration):
    type_: str
    name: str
    params: List[Expression] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)

    @property
    def return_type(self):
        return self.type_

@dataclass
class VarDeclStmt(Declaration):
    type_: str
    name: str
    expr: Expression

    @property
    def return_type(self):
        return self.type_

@dataclass
class ClassDeclStmt(Declaration):
    name: str  # El nombre de la clase
    class_members: List[Declaration] = field(default_factory=list) # Las declaraciones de la clase


@dataclass
class ConstructorDeclStmt(ASTNode):
    name: str  # Nombre de la clase, para identificar el constructor
    params: List['VarDeclStmt']  # Lista de parámetros del constructor
    body: 'CompoundStmt'  # Cuerpo del constructor

@dataclass
class DestructorDeclStmt(ASTNode):
    name: str  # Nombre de la clase para identificar el destructor
    body: 'CompoundStmt'  # Cuerpo del destructor




''' 
Statements

'''

@dataclass
class Program(Statement):
    decl: List[Statement] = field(default_factory=list)

@dataclass
class PrintfStmt(Statement):
    expr: Expression

@dataclass
class IfStmt(Statement):
    cond: Expression
    then_stmt: List[Statement] = field(default_factory=list)
    else_stmt: List[Statement] = field(default_factory=list)

@dataclass
class WhileStmt(Statement):
    cond: Expression
    body_stmt: List[Statement] = field(default_factory=list)

@dataclass
class ForStmt(Statement):
    init: Expression
    cond: Expression
    update: Expression
    body_stmt: List[Statement] = field(default_factory=list)

@dataclass
class ReturnStmt(Statement):
    expr: Expression

@dataclass
class ExprStmt(Statement):
    expr: Expression

@dataclass
class BreakStmt(Statement):
    name: str

@dataclass
class ContinueStmt(Statement):
    name: str

@dataclass
class SizeStmt(Statement):
    expr: Expression

@dataclass
class CompoundStmt(Statement):
    stmts: List[Statement] = field(default_factory=list)

@dataclass
class NullStmt(Statement):
    pass

'''
**************** EXPRESIONES ****************

'''
@dataclass
class LiteralExpr(Expression):
    value: any



# @dataclass
# class ConstExpr(Expression):
#     value: Union[int, float, bool, str]

# @dataclass
# class NewArrayExpr(Expression):
#     type_: str
#     size: Expression

#     @property
#     def return_type(self):
#         return self.type_

@dataclass
class CallExpr(Expression):
    func: Expression
    args: List[Expression] = field(default_factory=list)

@dataclass
class VarExpr(Expression):
    name: str

# @dataclass
# class ArrayLookupExpr(Expression): #Acceso a arreglos
#     array: Expression
#     index: Expression

# @dataclass
# class FieldAccessExpr(Expression): #Acceso a campos de clase
#     expr: Expression
#     field: str

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
class LogicalExpr(Expression):
    op: str
    left: Expression
    right: Expression

# @dataclass
# class VarAssignmentExpr(Expression):
#     name: str
#     expr: Expression

# @dataclass
# class ArrayAssignmentExpr(Expression):
#     array: Expression
#     index: Expression
#     expr: Expression

# @dataclass
# class IntToFloatExpr(Expression):
#     expr: Expression

# @dataclass
# class ArraySizeExpr(Expression):
#     array: Expression

@dataclass
class AssignExpr(Expression):
    op: str
    name: str
    expr: Expression

@dataclass
class Set(Expression):
    obj: str
    name: str
    expr: Expression

@dataclass
class Get(Expression):
    obj: str
    name: str

@dataclass
class ThisExpr(Expression):
    pass





