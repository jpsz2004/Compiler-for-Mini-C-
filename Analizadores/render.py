'''

Clase que se encarga de renderizar el AST en formato DOT.

'''


from CppAST import *
from graphviz import Digraph

class DotRender(Visitor):

    node_default = {
        'shape': 'box',
        'style': 'filled',
        'color': 'skyblue1',
    }

    edge_default = {
        'arrowhead': 'none',
    }
    color = 'green'

    def __init__(self):
        self.dot = Digraph('AST')

        self.dot.attr('node', **self.node_default)
        self.dot.attr('edge', **self.edge_default)
        self.program = False
        self.seq = 0
        self.cont = 0
    
    def __repr__(self):
        return self.dot.source

    def __str__(self):
        return self.dot.source
    
    @classmethod
    def render(cls, model):
        dot = cls()
        model.accept(dot)
        return dot.dot
    
    def name(self):
        self.seq += 1
        return f'n{self.seq:02d}'
    

    # NODOS DE DECLARACIONES

    #FuncDeclStmt
    def visit(self, node: FuncDeclStmt):
        name = self.name()
        self.dot.node(name, label=fr"FunctDeclStmt\ntype:{node.type_} \nname:'{node.name}' \nparams:{node.params}", color=self.color)
        self.dot.edge(name, self.visit(node.body))
        return name
    
    #VarDeclStmt
    def visit(self, node: VarDeclStmt):
        name = self.name()
        self.dot.node(name, label=fr"VarDeclStmt\ntype:{node.type_} \nname:{node.name}", color=self.color)

        if node.expr:
            self.dot.edge(name, self.visit(node.expr), label='init')
        
        return name

    #ClassDeclStmt
    def visit(self, node: ClassDeclStmt):
        name = self.name()
        self.dot.node(name, label=fr"ClassDeclStmt\nname:{node.name}", color=self.color)
        for memb in node.class_members:
            self.dot.edge(name, self.visit(memb))
        return name
    
    #ConstructorDeclStmt
    def visit(self, node: ConstructorDeclStmt):
        name = self.name()
        self.dot.node(name, label=fr"ConstructorDeclStmt\nname:{node.name} \nparams: {node.params}", color=self.color)
        self.dot.edge(name, self.visit(node.body))
        return name
    
    #DestructorDeclStmt
    def visit(self, node: DestructorDeclStmt):
        name = self.name()
        self.dot.node(name, label=fr"DestructorDeclStmt\nname:{node.name}", color=self.color)
        self.dot.edge(name, self.visit(node.body))
        return name
    
    # NODOS DE INSTRUCCIONES

    #Program
    def visit(self, node: Program):
        name = self.name()
        self.dot.node(name, label='Program', color=self.color)
        for decl in node.decl:
            self.dot.edge(name, self.visit(decl))
        return name
    
    #PrintfStmt
    def visit(self, node: PrintfStmt):
        name = self.name()
        self.dot.node(name, label='PrintfStmt', color=self.color)
        self.dot.edge(name, self.visit(node.expr))
        return name
    
    #IfStmt
    def visit(self, node: IfStmt):
        name = self.name()
        self.dot.node(name, label='IfStmt', color=self.color)
        self.dot.edge(name, self.visit(node.cond), label='cond')
        if node.then_stmt:
            self.dot.edge(name, self.visit(node.then_stmt), label='then')
        if node.else_stmt:
            self.dot.edge(name, self.visit(node.else_stmt), label='else')
        return name
    
    #WhileStmt
    def visit(self, node : WhileStmt):
        name = self.name()
        self.dot.node(name,
            label='WhileStmt', color=self.color)
        self.dot.edge(name, self.visit(node.cond), label='cond')
        self.dot.edge(name, self.visit(node.body_stmt), label='body')
        return name
    
    #ForStmt
    def visit(self, node : ForStmt):
        name = self.name()
        self.dot.node(name, label='ForStmt', color=self.color)
        self.dot.edge(name, self.visit(node.init), label='init')
        self.dot.edge(name, self.visit(node.cond), label='cond')
        self.dot.edge(name, self.visit(node.update), label='update')
        self.dot.edge(name, self.visit(node.body_stmt), label='body')
        return name
    
    #ReturnStmt
    def visit(self, node: ReturnStmt):
        name = self.name()
        self.dot.node(name, label='ReturnStmt', color=self.color)
        
        if node.expr:
            self.dot.edge(name, self.visit(node.expr))
        return name
    
    #ExprStmt
    def visit(self, node: ExprStmt):
        name = self.name()
        self.dot.node(name, label='ExprStmt', color=self.color)
        self.dot.edge(name, self.visit(node.expr))
        return name
    
    #BreakStmt
    def visit(self, node: BreakStmt):
        name = self.name()
        self.dot.node(name, label=f'Break', color=self.color)
        return name
    
    #ContinueStmt
    def visit(self, node: ContinueStmt):
        name = self.name()
        self.dot.node(name, label=f'Continue', color=self.color)
        return name
    
    #SizeStmt
    def visit(self, node: SizeStmt):
        name = self.name()
        self.dot.node(name, label='SizeStmt', color=self.color)
        self.dot.edge(name, self.visit(node.expr))
        return name
    
    #CompoundStmt
    def visit(self, node: CompoundStmt):
        name = self.name()
        if not self.program:
            self.program = True
        self.dot.node(name, label='CompoundStmt', color=self.color)
        for stmt in node.stmts:
            self.dot.edge(name, self.visit(stmt))
        return name
    
    #NullStmt
    def visit(self, node: NullStmt):
        name = self.name()
        self.dot.node(name, label='NullStmt', color=self.color)
        return name
    
    # NODOS DE EXPRESIONES

    #LiteralExpr
    def visit(self, node: LiteralExpr):
        name = self.name()
        value = node.value

        if node.value is None:
            value = "nil"
        elif node.value is True:
            value = "true"
        elif node.value is False:
            value = "false"
        self.dot.node(name, label=fr"LiteralExpr\nvalue= {value}", color=self.color)
        return name
    
    #CallExpr
    def visit(self, node: CallExpr):
        name = self.name()
        self.dot.node(name, label=f"Call ", color=self.color)
        self.dot.edge(name, self.visit(node.func), color=self.color)
        if node.args is not None:
            for arg in node.args:
                self.dot.edge(name, self.visit(arg), color=self.color)
        return name
    
    #VarExpr
    def visit(self, node: VarExpr):
        name = self.name()
        self.dot.node(name, label=f"Variable {node.name}")
        return name

    #UnaryOpExpr
    def visit(self, node: UnaryOpExpr):
        name = self.name()
        self.dot.node(name, label=f'Unary {node.op}', color=self.color)
        self.dot.edge(name, self.visit(node.expr), color=self.color)
        return name
    
    #BinaryOpExpr
    def visit(self, node: BinaryOpExpr):
        name = self.name()
        self.dot.node(name, label=f"Binary '{node.op}'", color=self.color)
        self.dot.edge(name, self.visit(node.left), color=self.color)
        self.dot.edge(name, self.visit(node.right), color=self.color)
        return name

    #LogicalExpr
    def visit(self, node: LogicalExpr):
        name = self.name()
        self.dot.node(name, label=f"Logical '{node.op}'", color=self.color)
        self.dot.edge(name, self.visit(node.left), color=self.color)
        self.dot.edge(name, self.visit(node.right), color=self.color)
        return name
    
    #AssignExpr
    def visit(self, node: AssignExpr):
        name = self.name()
        label = "Assign" if node.op == '=' else node.op
        self.dot.node(name, label=fr"{label}\nname: '{node.name}'", color=self.color)
        self.dot.edge(name, self.visit(node.expr), color=self.color)
        return name
    
    #AssignPostFix
    def visit(self, node: AssignPostFix):
        name = self.name()
        label = node.op
        self.dot.node(name, label=fr"{label}\n Postfix", color=self.color)
        self.dot.edge(name, self.visit(node.expr), color=self.color)
        return name
    
    #AssignPreFix
    def visit(self, node : AssignPreFix):
        name = self.name()
        label = node.op
        self.dot.node(name, label=fr"{label}\n Prefix")
        self.dot.edge(name, self.visit(node.expr))
        return name
    
    #Get
    def visit(self, node : Get):
        name = self.name()
        self.dot.node(name, label='')

        f'(get {self.visit(node.obj)} {node.name})'
        return name
    
    #Set
    def visit(self, node : Set):
        name = self.name()
        self.dot.node(name, label='')
        f'(set {self.visit(node.obj)} {node.name} {self.visit(node.expr)})'
        return name
    
    #ThisExpr
    def visit(self, node : ThisExpr):
        name = self.name()
        self.dot.node(name, label='this ')
        return name