'''

********* ANALIZADOR LÉXICO PARA MINI C++ *********

* Autor: Juan Pablo Sánchez Zapata
* Fecha: 2024-09-02
* Descripción: Implementación de un analizador léxico para tokenizar el lenguaje C++ (Mini C++).
* El analizador léxico se encarga de identificar los tokens que conforman el lenguaje C++.
* Se utiliza la librería sly para la implementación del analizador léxico.
* Se utiliza la librería rich para la impresión de los tokens identificados.
* Se importan las pruebas unitarias de test_cases.py para imprimir los tokens.
-------------------------------------------------------------------------------------------------
* SALVEDADES: Se usa # type: ignore para ocultar los errores de tipo en la librería sly.

********* ANALIZADOR LÉXICO PARA MINI C++ *********

'''

#Librerías
from sly import Lexer
from rich import print
from test_cases import test_cases

#Definición de la clase CppLexer
class CppLexer(Lexer):
    
    # Tokens
    tokens = {
        IDENTIFIER, TYPE_SPECIFIER, ACCESS_SPECIFIER, INT_LITERAL, FLOAT_LITERAL, BOOL_LITERAL, STRING_LITERAL, # type: ignore
        IF, ELSE, WHILE, CLASS, PRINTF, RETURN, NEW, BREAK, CONTINUE, SIZE, # type: ignore
        PLUS, MINUS, TIMES, DIVIDE, MOD, ASSIGN, EQUAL, NOT_EQUAL, LESS, LESS_EQUAL, # type: ignore
        GREATER, GREATER_EQUAL, AND, OR, NOT, SEMICOLON, COMMA, DOT, COLON, LEFT_PAREN, # type: ignore
        RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE, LEFT_BRACKET, RIGHT_BRACKET, # type: ignore
    }

    ''' ********* DEFINICIÓN DE TOKENS ********* '''

    # Palabras reservadas
    ACCESS_SPECIFIER = r'public|private|protected'
    TYPE_SPECIFIER = r'int|float|bool|void|string'
    CLASS = r'class'
    IF = r'if'
    ELSE = r'else'
    WHILE = r'while'
    PRINTF = r'printf'
    RETURN = r'return'
    NEW = r'new'
    BREAK = r'break'
    CONTINUE = r'continue'
    SIZE = r'size'

    # Operadores
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    ASSIGN = r'='
    EQUAL = r'=='
    NOT_EQUAL = r'!='
    LESS = r'<'
    LESS_EQUAL = r'<='
    GREATER = r'>'
    GREATER_EQUAL = r'>='
    AND = r'&&'
    OR = r'\|\|'
    NOT = r'!'

    # Delimitadores
    SEMICOLON = r';'
    COMMA = r','
    DOT = r'\.'
    COLON = r':'
    LEFT_PAREN = r'\('
    RIGHT_PAREN = r'\)'
    LEFT_BRACE = r'\{'
    RIGHT_BRACE = r'\}'
    LEFT_BRACKET = r'\['
    RIGHT_BRACKET = r'\]'

    ''' ********* DEFINICIÓN DE RE ********* '''
    
    # Se define el literal flotante antes que el entero para que el lexer pueda diferenciarlos
    @_(r'\d+\.\d+') # type: ignore
    def FLOAT_LITERAL(self, t):
        t.value = float(t.value)
        return t

    #INT_LITERAL
    @_(r'\d+') # type: ignore
    def INT_LITERAL(self, t):
        t.value = int(t.value)
        return t
    
    #BOOL_LITERAL
    @_(r'true|false') # type: ignore
    def BOOL_LITERAL(self, t):
        t.value = True if t.value == 'true' else False
        return t
    
    #VOID_LITERAL
    @_(r'void') # type: ignore
    def VOID_LITERAL(self, t):
        return t
    
    #STRING_LITERAL
    @_(r'"(\\.|[^"\\])*"') # type: ignore
    def STRING_LITERAL(self, t):
        return t
    

    # Destructor: ~ seguido del nombre de la clase
    @_(r'~[A-Z][a-zA-Z_0-9]*') #type: ignore
    def DESTRUCTOR(self, t):
        return t
    
    # Manejo de la declaración de clase
    def __init__(self):
        self.current_class_name = None

    @_(r'class') # type: ignore
    def CLASS(self, t):
        self.current_class_name = None  # Reiniciar el nombre de la clase
        return t

    #IDENTIFIER con condición especial para identificar el constructor
    @_(r'[a-zA-Z_][a-zA-Z0-9_]*') # type: ignore
    def IDENTIFIER(self, t):
        if self.current_class_name is None:
            self.current_class_name = t.value  # Guardar el nombre de la clase
        elif t.value == self.current_class_name:
            t.type = 'CONSTRUCTOR'  # Identificar el constructor
        return t
    
    ''' ********* IGNORAR ********* '''
    
    # Ignorar espacios en blanco y tabulaciones
    ignore = ' \t\r'

    #Ignorar comentarios
    @_(r'//.*') # type: ignore
    def ignore_comment(self, t):
        self.lineno += 1
    
    #Ignorar comentarios multilinea
    @_(r'/\*(.|\n)*?\*/') # type: ignore
    def ignore_multiline_comment(self, t):
        self.lineno += t.value.count('\n')

    ''' ********* MANEJO DE NUEVAS LÍNEAS Y ERRORES ********* '''

    # Contador de líneas
    @_(r'\n+') # type: ignore
    def ignore_newline(self, t):
        self.lineno += len(t.value)


    # Manejo de errores
    def error(self, t):
        print(f'[red]Caracter ilegal {t.value[0]!r} en la línea {self.lineno}[/red]')
        self.index += 1

#Función para imprimir los tokens de las pruebas unitarias
def print_tokens():
    l = CppLexer()

     # Determinar el ancho máximo para cada columna
    max_type_width = max(len('TYPE'), max(len(tok.type) for case in test_cases for tok in CppLexer().tokenize(case['code'])))
    max_value_width = max(len('VALUE'), max(len(str(tok.value)) for case in test_cases for tok in CppLexer().tokenize(case['code'])))
    
    for case in test_cases:
        print(f"***[bold]{case['description']}[/bold]***\n") #Estilos
        print(f"|{'TYPE'.ljust(max_type_width)}|{'VALUE'.ljust(max_value_width)}|")
        print(f"|{'-' * max_type_width}|{'-' * max_value_width}|")
        for tok in CppLexer().tokenize(case['code']): #Tokenizar
            print(f"|[green]{tok.type.ljust(max_type_width)}[/green]|[blue]{str(tok.value).ljust(max_value_width)}[/blue]|") #Colores
        print(f"|{'-' *  max_type_width }|{'-' * max_value_width}|")#Decoración
        print("\n")


#Ejecutar la función print_tokens
if __name__ == '__main__':
    print_tokens()
