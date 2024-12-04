'''

****************************************** TREE WALING INTERPRETER PARA MINI C++ ******************************************

* Autor: Juan Pablo Sánchez Zapata
* Fecha: 2024-11-20
* Descripción: Implementación de un intérprete que recorre el árbol sintáctico con el objetivo 
de ejecutar el código fuente de Mini C++.

-  El intérprete recorre el AST y ejecuta las operaciones definidas en el código fuente. 
Esto incluye la ejecución de expresiones, el manejo de control de flujo (condiciones, bucles), 
la manipulación de variables, etc.

- El intérprete evalúa las declaraciones de variables, funciones y otras estructuras del lenguaje, 
gestionando las operaciones de asignación, invocación de funciones, y la creación de nuevos objetos o instancias.

- El intérprete también se encarga de manejar errores de ejecución en tiempo real, como la ejecución de operaciones 
inválidas o el acceso a variables no inicializadas.

******************************************************************************************************************************


'''

from collections import ChainMap
from CppAST import *
from CppChecker import Checker
from rich import print
from stdlib import *

import math

# Veracidad en Mini C++
def _is_truthy(value):
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    else:
        return True
    
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ContinueException(Exception):
    pass

class MiniCExit(BaseException):
    pass

class AttributeError(Exception):
    pass


class Function: 
    def __init__(self, node, env):
        self.node = node
        self.env = env

    @property
    def arity(self) -> int:
        return len(self.node.params)

    def __call__(self, interp, *args):
        if self.node.params is not None:
            if len(args) != len(self.node.params):
                raise CallError(f"Interp Error. Expected {len(self.node.params)} arguments but got {len(args)}")

        # Crear un nuevo entorno para los parámetros
        newenv = self.env.new_child()
        if self.node.params is not None:
            for param, arg in zip(self.node.params, args):
                newenv[param.name] = arg  # Usar el atributo `name` de cada parámetro

        # Cambiar el entorno actual
        oldenv = interp.env
        interp.env = newenv

        try:
            self.node.body.accept(interp)
            result = None
        except ReturnException as e:
            result = e.value
        finally:
            interp.env = oldenv
        return result

    
    def bind(self, instance):
        env = self.env.new_child()
        env['this'] = instance
        return Function(self.node, env)
    
class Class:

    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name
    
    def __call__(self, *args):
        this = Instance(self)
        init = self.find_method('init')
        if init:
            init.bind(this)(*args)
        return this

    def find_method(self, name):
        meth = self.methods.get(name)
        if meth:
            return meth
        else:
            raise AttributeError(f"Method {name} not found in class {self.name}")
        
class Instance: 
    def __init__(self, kclass):
        self.kclass = kclass
        self.fields = {}
    
    def __str__(self):
        return self.klass.name + " instance"
    
    def get(self, name):
        if name in self.data:
            return self.data[name]
        method = self.klass.find_method(name)
        if not method:
            raise AttributeError(f"Method {name} not found in class {self.klass.name}")
        return method.bind(self)
    
    def set(self, name, value):
        self.data[name] = value

ThereIsBreak=False
ThereIsContinue=False

class Interpreter(Visitor):

    def __init__(self, ctxt):
        self.ctxt = ctxt
        self.env = ChainMap()
        self.check_env = ChainMap()
        self.localmap = {}

    def _check_numeric_operands(self, node, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True
        else:
            self.error(node, f"Interp Error. In '{node.op}', operands must be numeric")

    def _check_numeric_operand(self, node, value):
        if isinstance(value, (int, float)):
            return True
        else:
            self.error(node, f"Interp Error. In '{node.op}', operand must be numeric")

    def error(self, position, message):
        self.ctxt.error(position, message)
        raise MiniCExit()
    
    # Punto de entrada alto-nivel
    def interpret(self, node):
        try:
            Checker.check(node, self.ctxt)
            if not self.ctxt.have_errors:
                self.visit(node)
            else: print("\n The interpreter could not start because the Checker returned errors")
        except MiniCExit as e:
            pass
    
    # Declaraciones

    def visit(self, node: CompoundStmt):
        for stmt in node.stmts:
            self.visit(stmt)
            if ThereIsBreak:
                return 0
            if ThereIsContinue:
                return 1
    
    def visit(self, node: Program):
        for k, v in stdlibFunctions.items():
            self.env[k] = v
        
        for d in node.decl:
            self.visit(d)
    
    def visit(self, node: ClassDeclStmt):
        class_members = { }
        for memb in node.class_members:
            class_members[memb.name] = Function(memb, self.env)
            cls = Class(node.name, class_members)
            self.env[node.name] = cls
    
    def visit(self, node: ConstructorDeclStmt):
        func = Function(node, self.env)
        self.env[node.name] = func
    
    def visit(self, node: DestructorDeclStmt):
        func = Function(node, self.env)
        self.env[node.name] = func
    
    def visit(self, node: FuncDeclStmt):
        func = Function(node, self.env)
        self.env[node.name] = func

    def visit(self, node: VarDeclStmt):
        if node.expr:
            expr = self.visit(node.expr)
        else:
            expr = None
        self.env[node.name] = expr
    
    def visit(self, node: PrintfStmt):
        print(self.visit(node.expr))
    
    def visit(self, node: IfStmt):
        test = self.visit(node.cond)
        if _is_truthy(test):
            self.visit(node.then_stmt)
        elif node.else_stmt:
            self.visit(node.else_stmt)
    
    def visit(self, node: WhileStmt):
        global ThereIsContinue
        global ThereIsBreak

        while _is_truthy(self.visit(node.cond)):
            ThereIsContinue = False
            ThereIsBreak = False
            flowControl = self.visit(node.body_stmt)
            if flowControl == 0:
                 break
            elif flowControl == 1:
                continue
            else:
                pass
    
    def visit(self, node: ForStmt):
        global ThereIsContinue
        global ThereIsBreak

        self.visit(node.init)
        while _is_truthy(self.visit(node.cond)):
            ThereIsContinue = False
            ThereIsBreak = False
            flowControl = self.visit(node.body_stmt)
            if flowControl == 0:
                break
            elif flowControl == 1:
                continue
            else:
                pass
            self.visit(node.update)
    
    def visit(self, node: ReturnStmt):
        raise ReturnException(self.visit(node.expr))

    def visit(self, node: ExprStmt):
        self.visit(node.expr)

    def visit(self, node: BreakStmt):
        global ThereIsBreak
        ThereIsBreak = True
    
    def visit(self, node: ContinueStmt):
        global ThereIsContinue
        ThereIsContinue = True
    
    def visit(self, node: SizeStmt):
        return len(self.visit(node.expr))
    
    def visit(self, node: NullStmt):
        pass

    # Expresiones

    def visit(self, node: LiteralExpr):
        return node.value
    
    def visit(self, node: BinaryOpExpr):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            (isinstance(left, str) and isinstance(right, str)) or self._check_numeric_operands(node, left, right)
            return left + right
        elif node.op == '-':
            self._check_numeric_operands(node, left, right)
            return left - right
        elif node.op == '*':
            self._check_numeric_operands(node, left, right)
            return left * right
        elif node.op == '/':
            self._check_numeric_operands(node, left, right)
            return left / right
        elif node.op == '%':
            self._check_numeric_operands(node, left, right)
            return left % right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            self._check_numeric_operands(node, left, right)
            return left < right
        elif node.op == '<=':
            self._check_numeric_operands(node, left, right)
            return left <= right
        elif node.op == '>':
            self._check_numeric_operands(node, left, right)
            return left > right
        elif node.op == '>=':
            self._check_numeric_operands(node, left, right)
            return left >= right
        else:
            raise NotImplementedError(f"Interp Error. Binary operator '{node.op}' not implemented")
        
    def visit(self, node: UnaryOpExpr):
        expr = self.visit(node.expr)
        if node.op == "-":
            self._check_numeric_operand(node, expr)
            return - expr
        elif node.op == "!":
            return not _is_truthy(expr)
        else:
            raise NotImplementedError(f"Interp Error. Unary operator '{node.op}' not implemented")
        
    def visit(self, node: LogicalExpr):
        left = self.visit(node.left)
        if node.op == '||':
            return left if _is_truthy(left) else self.visit(node.right)
        if node.op == '&&':
            return self.visit(node.right) if _is_truthy(left) else left
        raise NotImplementedError(f"Interp Error. Logical operator '{node.op}' not implemented")

    def visit(self, node: VarExpr):
        return self.env[node.name]
    
    def visit(self, node: CallExpr):
        callee = node.func.accept(self)
        if not callable(callee):
            self.error(node.func, f'Interp error {self.ctxt.find_source(node.func)!r} no es invocable')
        
        if node.args is not None:
            args = [arg.accept(self) for arg in node.args]
        else:
            args = []

        try:
            return callee(self, *args)
        except CallError as err:
            self.error(node.func, str(err))
    
    def visit(self, node: AssignExpr):
        expr = 0
        if node.op == "=":
            expr = self.visit(node.expr)
        elif node.op == "+=":
            expr = self.env[node.name] + self.visit(node.expr)
        elif node.op == "-=":
            expr = self.env[node.name] - self.visit(node.expr)
        elif node.op == "*=":
            expr = self.env[node.name] * self.visit(node.expr)
        elif node.op == "/=":
            expr = self.env[node.name] / self.visit(node.expr)
        elif node.op == "%=":
            expr = self.env[node.name] % self.visit(node.expr)
        self.env[node.name] = expr
    
    def visit(self, node: AssignPostFix):
        temp = self.visit(node.expr)
        expr = 0
        if node.op == "++":
            expr = self.visit(node.expr) + 1
        else:
            expr = self.visit(node.expr) - 1
        self.env[node.expr.name] = expr
        return temp
    
    def visit(self, node: AssignPreFix):
        expr = 0
        if node.op == "++":
            expr = self.visit(node.expr) + 1
        else:
            expr = self.visit(node.expr) - 1
        self.env[node.expr.name] = expr
        return expr
    
    def visit(self, node: Set):
        obj = self.visit(node.obj)
        val = self.visit(node.expr)

        if isinstance(obj, Instance):
            obj.set(node.name, val)
            return val
        else:
            self.error(node.obj, f'Interp Error{self.ctxt.find_source(node.obj)!r} is not an instance')

    def visit(self, node: Get):
        obj = self.visit(node.obj)
        if isinstance(obj, Instance):
            try:
                return obj.get(node.name)
            except AttributeError as err:
                self.error(node.obj, str(err))
        else:
            self.error(node.obj, f'Interp Error{self.ctxt.find_source(node.obj)!r}  is not an instance')

    def visit(self, node: ThisExpr):
        return self.env['this']