# conterp.py
'''
Tree-walking interpreter
'''
from collections import ChainMap
from rich        import print

from mcast       import *
from mchecker    import Checker
from mcbuiltins  import builtins, consts, CallError
from mctypes     import CObject, Number, String, Bool, Nil, Array


# Veracidad en MiniC
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
    newenv = self.env.new_child()
    for name, arg in zip(self.node.params, args):
      newenv[name] = arg

    oldenv = interp.env
    interp.env = newenv
    try:
      self.node.stmts.accept(interp)
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

  def __init__(self, name, sclass, methods):
    self.name = name
    self.sclass  = sclass
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
    if meth is None and self.sclass:
      return self.sclass.find_method(name)
    return meth


class Instance:

  def __init__(self, klass):
    self.klass = klass
    self.data = { }

  def __str__(self):
    return self.klass.name + " instance"

  def get(self, name):
    if name in self.data:
      return self.data[name]
    method = self.klass.find_method(name)
    if not method:
      raise AttributeError(f'Propiedad indefinida {name}')
    return method.bind(self)

  def set(self, name, value):
    self.data[name] = value


class Interpreter(Visitor):

  def __init__(self, ctxt):
    self.ctxt      = ctxt
    self.env       = ChainMap()
    self.check_env = ChainMap()
    self.localmap  = { }

  def _check_numeric_operands(self, node, left, right):
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
      return True
    else:
      self.error(node, f"En '{node.op}' los operandos deben ser numeros")

  def _check_numeric_operand(self, node, value):
    if isinstance(value, (int, float)):
      return True
    else:
      self.error(node, f"En '{node.op}' el operando debe ser un numero")

  def error(self, position, message):
    self.ctxt.error(position, message)
    raise MiniCExit()

  # Punto de entrada alto-nivel
  def interpret(self, node):

    for name, cval in consts.items():
      self.check_env[name] = cval
      self.env[name] = cval

    for name, func in builtins.items():
      self.check_env[name] = func
      self.env[name] = func

    try:
      Checker.check(node, self.check_env, self)
      if not self.ctxt.have_errors:
        node.accept(self)
    except MiniCExit as e:
      pass

  # Declarations

  def visit(self, node: ClassDeclStmt):
    if node.sclass:
      sclass = node.sclass.accept(self)
      env = self.env.new_child()
      env['super'] = sclass
    else:
      sclass = None
      env = self.env
    methods = { }
    for meth in node.methods:
      methods[meth.name] = Function(meth, env)
    cls = Class(node.name, sclass, methods)
    self.env[node.name] = cls

  def visit(self, node: FuncDeclStmt):
    func = Function(node, self.env)
    self.env[node.name] = func

  def visit(self, node: VarDeclStmt):
    if node.expr:
      expr = node.expr.accept(self)
    else:
      expr = None
    self.env[node.name] = expr

  # Statements

  def visit(self, node: CompoundStmt):
    self.env = self.env.new_child()
    for stmt in node.stmts:
      stmt.accept(self)
    self.env = self.env.parents

  def visit(self, node: Print):
    expr = node.expr.accept(self)
    if isinstance(expr, str):
      expr = expr.replace('\\n', '\n')
      expr = expr.replace('\\t', '\t')
    print(expr, end='')

  def visit(self, node: WhileStmt):
    while _is_truthy(node.expr.accept(self)):
      try:
        node.stmt.accept(self)
      except BreakException:
        return
      except ContinueException:
        raise NotImplementedError

  def visit(self, node: IfStmt):
    expr = node.expr.accept(self)
    if _is_truthy(expr):
      node.then_stmt.accept(self)
    elif node.else_stmt:
      node.else_stmt.accept(self)

  def visit(self, node: Break):
    raise BreakException()

  def visit(self, node: Continue):
    raise ContinueException()

  def visit(self, node: ReturnStmt):
    # Ojo: node.expr es opcional
    value = 0 if not node.expr else node.expr.accept(self)
    raise ReturnException(value)

  def visit(self, node: ExprStmt):
    node.expr.accept(self)

  # Expressions

  def visit(self, node: ConstStmt):
    return node.value

  def visit(self, node: BinaryOpExpr):
    left  = node.left.accept(self)
    right = node.right.accept(self)

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
      if isinstance(left, int) and isinstance(right, int):
        return left // right

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

    elif node.op == '>':
      self._check_numeric_operands(node, left, right)
      return left > right

    elif node.op == '<=':
      self._check_numeric_operands(node, left, right)
      return left <= right

    elif node.op == '>=':
      self._check_numeric_operands(node, left, right)
      return left >= right

    else:
      raise NotImplementedError(f"Mal operador {node.op}")

  def visit(self, node: LogicalOpExpr):
    left = node.left.accept(self)
    if node.op == '||':
      return left if _is_truthy(left) else node.right.accept(self)
    if node.op == '&&':
      return node.right.accept(self) if _is_truthy(left) else left
    raise NotImplementedError(f"Mal operador {node.op}")

  def visit(self, node: UnaryOpExpr):
    expr = node.expr.accept(self)
    if node.op == "-":
      self._check_numeric_operand(node, expr)
      return - expr
    elif node.op == "!":
      return not _is_truthy(expr)
    else:
      raise NotImplementedError(f"Mal operador {node.op}")

  def visit(self, node: Grouping):
    return node.expr.accept(self)

  def visit(self, node: VarAssignmentExpr):
    expr = node.expr.accept(self)
    if node.op == '=':
      self.env.maps[self.localmap[id(node)]][node.name] = expr
    elif node.op == '+=':
      self.env.maps[self.localmap[id(node)]][node.name] += expr
    elif node.op == '-=':
      self.env.maps[self.localmap[id(node)]][node.name] -= expr
    elif node.op == '*=':
      self.env.maps[self.localmap[id(node)]][node.name] *= expr
    elif node.op == '/=':
      self.env.maps[self.localmap[id(node)]][node.name] /= expr
    elif node.op == '%=':
      self.env.maps[self.localmap[id(node)]][node.name] %= expr

  def visit(self, node: PreInc):
    self.env.maps[self.localmap[id(node)]][node.name] += 1
    return self.env.maps[self.localmap[id(node)]][node.name]

  def visit(self, node: PreDec):
    self.env.maps[self.localmap[id(node)]][node.name] -= 1
    return self.env.maps[self.localmap[id(node)]][node.name]

  def visit(self, node: PostInc):
    ret = self.env.maps[self.localmap[id(node)]][node.name]
    self.env.maps[self.localmap[id(node)]][node.name] += 1
    return ret

  def visit(self, node: PostDec):
    ret = self.env.maps[self.localmap[id(node)]][node.name]
    self.env.maps[self.localmap[id(node)]][node.name] -= 1
    return ret

  def visit(self, node: CallExpr):
    callee = node.func.accept(self)
    if not callable(callee):
      self.error(node.func, f'{self.ctxt.find_source(node.func)!r} no es invocable')

    args = [ arg.accept(self) for arg in node.args ]

    if callee.arity != -1 and len(args) != callee.arity:
      self.error(node.func, f"Experado {callee.arity} argumentos")

    try:
      return callee(self, *args)
    except CallError as err:
      self.error(node.func, str(err))

  def visit(self, node: VarExpr):
    return self.env.maps[self.localmap[id(node)]][node.name]

  def visit(self, node: Set):
    obj = node.obj.accept(self)
    val = node.value.accept(self)
    if isinstance(obj, Instance):
      obj.set(node.name, val)
      return val
    else:
      self.error(node.obj, f'{self.ctxt.find_source(node.obj)!r} no es una instancia')

  def visit(self, node: Get):
    obj = node.obj.accept(self)
    if isinstance(obj, Instance):
      try:
        return obj.get(node.name)
      except AttributeError as err:
        self.error(node.obj, str(err))
    else:
      self.error(node.obj, f'{self.ctxt.find_source(node.obj)!r} no es una instancia')

  def visit(self, node: This):
    return self.env.maps[self.localmap[id(node)]]['this']

  def visit(self, node: Super):
    distance = self.localmap[id(node)]
    sclass = self.env.maps[distance]['super']
    this = self.env.maps[distance-1]['this']
    method = sclass.find_method(node.name)
    if not method:
      self.error(node.object, f'Propiedad indefinida {node.name!r}')
    return method.bind(this)
