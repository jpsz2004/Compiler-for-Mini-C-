from CppAST import *
from stdlib import *

'''
****************************************************************************************
******************************** ANALIZADOR SEMÁNTICO **********************************

Autor: Juan Pablo Sánchez Zapata
Fecha: 03/11/2024

Descripción: El analizador semántico se encarga de verificar que el código
cumpla con las reglas del lenguaje de programación, es decir,
que las variables estén declaradas antes de ser usadas, que
los tipos de datos sean correctos, que las funciones sean
declaradas antes de ser usadas, etc.

Para ello, se recorre el AST generado por el parser y se
verifican las reglas semánticas del lenguaje.

****************************************************************************************

'''

class SymbolTable:
    '''
    TABLA DE SÍMBOLOS

    La tabla de símbolos es un objeto que mantiene un diccionario
    de nombres de símbolos y nodos asociados a esos símbolos.

    Existe una tabla de símbolos separada para cada elemento de código
    que lo requiera, como funciones, clases, bloques, etc.
    '''

    class SymbolError(Exception):
        '''
        EXCEPCIÓN DE ERROR DE SÍMBOLO. Se lanza cuando se intenta
        agregar un símbolo que ya existe en la tabla de símbolos.
        '''
        pass

    def __init__(self, parent=None):
        '''
        Constructor de la tabla de símbolos. Recibe un nodo padre
        que puede ser otro nodo de la tabla de símbolos, o None si
        es la tabla de símbolos principal. Esta es una tabla de símbolos
        vacía con la tabla de símbolos padre.
        '''
        self.symbols = {}
        
        for key, value in stdlibFunctions.items():
            self.symbols[key] = value
        
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.children = []
    
    def addSymbol(self, name, value):
        '''
        Añade un símbolo a la tabla de símbolos. Si el símbolo
        ya existe, lanza una excepción SymbolError.
        '''
        if name in self.symbols:
            raise SymbolTable.SymbolError(f"El símbolo '{name}' ya existe en la tabla de símbolos.")
        self.symbols[name] = value
    
    def getSymbol(self, name):
        '''
        Obtiene el valor asociado a un símbolo en la tabla de símbolos.
        Si el símbolo no existe, busca en la tabla de símbolos padre.
        '''
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.getSymbol(name)
        else:
            return None

InLoop = False

#Analizador semántico
class Checker(Visitor):
    '''
    Visitante para crear y enlazar tabla de símbolos al AST    
    '''

    def add_symbol(self, node, env: SymbolTable):
        '''
        Intenta agregar un símbolo a la tabla de símbolos.
        Captura excepciones y arroja errores
        '''
        try:
            env.addSymbol(node.name, node)
        except SymbolTable.SymbolError:
            self.error(node, f"El símbolo '{node.name}' ya ha sido declarado")

    def error(cls, position, txt):
        cls.ctxt.error(position, txt)
    

    @classmethod
    def check(cls, ast, ctxt):
        '''
        Método estático para iniciar el análisis semántico
        '''

        cls.ctxt = ctxt
        checker = cls(ctxt)
        checker = cls(ctxt)
        
        ast.accept(checker)

        return checker

    #Puerta de entrada a través de ASTNode de CppAST
    def visit(self, node: ASTNode):
        s1 = SymbolTable()
        self.visit(node, s1)
    
    #Visita de nodos de declaración
    def visit(self, node: FuncDeclStmt, env: SymbolTable):
        '''
            1. Agregar el nombre de la función a la tabla de símbolos actual con su tipo.
            2. Crear una nueva tabla de símbolos para el ámbito de la función.
            3. Registrar los parámetros de la función en la nueva tabla de símbolos.
            4. Visitar el cuerpo de la función dentro del nuevo ámbito.
            5. Verificar el tipo de retorno de las declaraciones de retorno en el cuerpo.
        '''
        # 1. Se agrega el nombre y tipo de función a la tabla de símbolos actual
        self.add_symbol(node, env)

        # 2. Se crea una nueva tabla de símbolos para la función
        new_env = SymbolTable(parent=env)

        # 3. Se registran los parámetros de la función en la nueva tabla de símbolos
        for param in node.parms:
            if hasattr(param, 'name') and hasattr(param, 'type_'): #True cuando cada parámetro es una expresión con nombre y tipo
                new_env.addSymbol(param.name, {'type': param.type_})
            else:
                raise ValueError("Error en la declaración de parámetros de la función")
            
        # 4. Se visitan las instrucciones de la función
        for statement in node.body:
            self.visit(statement, new_env)
        
        # 5. Se verifica el tipo de retorno de las declaraciones de retorno en el cuerpo
        for statement in node.body:
            if isinstance(statement, ReturnStmt):
                return_type = self.visit(statement.expr, new_env)
                if return_type != node.type_:
                    self.error(node, f"Error en el tipo de retorno de la función. '{return_type}' no coincide con el tipo de la función '{node.type_}'")
    
    def visit(self, node: VarDeclStmt, env: SymbolTable):
        '''
        1. Agregar el nombre de la variable a la tabla de símbolos actual con su tipo.
        2. Visitar la expresión de inicialización de la variable.
        3. Verificar que la expresión de inicialización sea del mismo tipo que la variable.
        '''

        # 1. Se agrega el nombre y tipo de la variable a la tabla de símbolos actual
        self.add_symbol(node, env)

        # 2,3 Visitar la expresión de inicialización de la variable y verificar tipo
        if node.expr:
            expr_type = self.visit(node.expr, env)
            if expr_type != node.type_:
                self.error(node, f"Error en la inicialización de la variable. '{expr_type}' no coincide con el tipo de la variable '{node.type_}'")
    
    def visit(self, node: ClassDeclStmt, env: SymbolTable):
        '''
        1. Agregar el nombre de la clase a la tabla de símbolos actual.
        2. Crear una nueva tabla de símbolos para el ámbito de la clase.
        3. Visitar y registrar las declaraciones de la clase en la nueva tabla de símbolos.
        '''

        # 1. Se agrega el nombre de la clase a la tabla de símbolos
        self.add_symbol(node, env)
        
        # 2. Se crea una nueva tabla de símbolos para la clase
        class_scope = SymbolTable(parent=env)

        # 3. Se registran las declaraciones de la clase en la nueva tabla de símbolos
        for member in node.class_members:
            if isinstance(member, Declaration):
                # Se visita cada miembro de la clase
                self.visit(member, class_scope)
            else:
                self.error(node, f"El miembro'{member}' en la clase '{node.class_name}' no es una declaración válida")
    
    def visit(self, node: ConstructorDeclStmt, env: SymbolTable):
        '''
        1. Agregar el nombre del constructor a la tabla de símbolos actual.
        2. Crear una nueva tabla de símbolos para el ámbito del constructor.
        3. Registrar los parámetros del constructor en la nueva tabla de símbolos.
        4. Visitar el cuerpo del constructor dentro del nuevo ámbito.
        '''

        # 1. Se agrega el nombre del constructor a la tabla de símbolos
        self.add_symbol(node, env)
        
        # 2. Se crea una nueva tabla de símbolos para el constructor
        constructor_scope = SymbolTable(parent=env)

        # 3. Se registran los parámetros del constructor en la nueva tabla de símbolos
        for param in node.params:
            if isinstance(param, VarDeclStmt):
                constructor_scope.addSymbol(param.name, {'type': param.type_})
            else:
                self.error(node, f"El parámetro '{param}' en el constructor '{node.name}' no es una declaración válida")
        
        # 4. Se visita el cuerpo del constructor
        for statement in node.body:
            self.visit(statement, constructor_scope)
    
    def visit(self, node: DestructorDeclStmt, env: SymbolTable):
        '''
        1. Agregar el nombre del destructor a la tabla de símbolos actual.
        2. Crear una nueva tabla de símbolos para el ámbito del destructor.
        3. Visitar el cuerpo del destructor dentro del nuevo ámbito.
        '''

        # 1. Se agrega el nombre del destructor a la tabla de símbolos
        self.add_symbol(node, env)
        
        # 2. Se crea una nueva tabla de símbolos para el destructor
        destructor_scope = SymbolTable(parent=env)

        # 3. Se visita el cuerpo del destructor
        for statement in node.body:
            self.visit(statement, destructor_scope)
    
    #Visita de nodos de instrucciones
    def visit(self, node: Program, env: SymbolTable):
        '''
        Visitar las declaraciones
        '''

        for declarations in node.decl:
            self.visit(declarations, env)
    
    def visit(self, node: PrintfStmt, env: SymbolTable):
        '''
        Visitar la expresión del printf
        '''

        self.visit(node.expr, env)
    
    def visit(self, node: IfStmt, env: SymbolTable):
        '''
        1. Visitar la condición del if.
        2. Visitar el cuerpo del if.
        3. Visitar el cuerpo del else si está definido.
        '''

        # 1. Se visita la condición de if

        self.visit(node.cond, env)

        # 2. Se visita el cuerpo del if
        self.visit(node.then_stmt, env)

        # 3. Se visita el cuerpo del else
        if node.else_stmt:
            self.visit(node.else_stmt, env)
    
    def visit(self, node: WhileStmt, env: SymbolTable):
        '''
        1. Visitar la condición
        2. Visitar el cuerpo del while
        '''

        global InLoop
        # 1. Se visita la condición del while
        self.visite(node.cond, env)
        InLoop=True

        # 2. Se visita el cuerpo del while
        self.visit(node.body_stmt, env)
        InLoop=False

        
