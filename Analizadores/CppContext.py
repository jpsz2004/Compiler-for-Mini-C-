'''

Clase de alto nivel que contiene todo sobre el análisis
y la ejecución de un programa mini cpp

'''

from CppLexer import CppLexer
from CppParser import CppParser
from CppInterpreter import Interpreter
from rich import print

import CppAST

class Context:

    def __init__(self):
        self.lexer = CppLexer(self)
        self.parser = CppParser(self)
        self.interp = Interpreter(self)
        self.source = ''
        self.ast = None
        self.have_errors = False

    #Se pone en marcha el parser
    def parse(self, source):
        self.have_errors = False
        self.source = source
        self.ast = self.parser.parse(self.lexer.tokenize(source))

    #Se ejecuta el programa con el intérprete
    def run(self):
        if not self.have_errors:
            return self.interp.interpret(self.ast)

    def find_source(self, node):
        indices = self.parser.index_position(node)
        if indices:
            return self.source[indices[0]:indices[1]]
        else:
            return f'{type(node).__name__} (source not available)'
        
    def error(self, position, message):
        if isinstance(position, CppAST.ASTNode):
            lineno = self.parser.line_position(position)
            (start, end) = (part_start, part_end) = self.parser.index_position(position)

            while start >= 0 and self.source[start] != '\n':
                start -= 1
            
            start += 1

            while end < len(self.source) and self.source[end] != '\n':
                end += 1
            
            print()
            print(self.source[start:end])
            print(" "*(part_start - start), end='')
            print("^"*(part_end - part_start))
            print(f'{lineno}: {message}')

        else:
            print(message)
        
        self.have_errors = True
