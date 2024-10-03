from CppAST import *
from CppParser import CppParser  
from CppLexer import CppLexer  
from rich import print

class ASTVisualizerDOT(Visitor):
    def __init__(self):
        self.dot_lines = ["digraph G {"]
        self.node_count = 0

    def new_node(self, label):
        node_name = f"node{self.node_count}"
        self.dot_lines.append(f'{node_name} [label="{label}"];')
        self.node_count += 1
        return node_name

    def add_edge(self, parent, child):
        self.dot_lines.append(f'{parent} -> {child};')

    def visit(self, node, parent=None):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node, parent)

    def generic_visit(self, node, parent):
        node_name = self.new_node(node.__class__.__name__)
        if parent:
            self.add_edge(parent, node_name)

        for field_name, field_value in node.__dict__.items():
            if isinstance(field_value, list):
                for item in field_value:
                    if isinstance(item, ASTNode):
                        self.visit(item, node_name)
            elif isinstance(field_value, ASTNode):
                self.visit(field_value, node_name)
            else:
                # Los campos básicos como identificadores o valores se pueden agregar como nodos
                leaf_node = self.new_node(f'{field_name} = {field_value}')
                self.add_edge(node_name, leaf_node)

        return node_name

    def get_dot(self):
        self.dot_lines.append("}")
        return "\n".join(self.dot_lines)

def generate_ast_from_file(file_path):
    with open(file_path, "r") as f:
        code = f.read()  # Se lee el código desde el archivo
        
    lexer = CppLexer()  # Instanciar el lexer
    parser = CppParser()  # Instanciar el parser
    
    # Tokenizar el código fuente antes de pasarlo al parser
    tokens = lexer.tokenize(code)
    
    # Parsear los tokens para generar el AST
    ast = parser.parse(tokens)  # Ahora pasamos los tokens al parser
    
    return ast


if __name__ == '__main__':
    # Leer el archivo de prueba
    file_path = 'Pruebas/test.mcc'  # Ruta del archivo test.mcc
    ast = generate_ast_from_file(file_path)

    # Visualizar el AST en formato DOT
    visualizer = ASTVisualizerDOT()
    visualizer.visit(ast)

    # Guardar el archivo DOT
    with open('ast_output.dot', 'w') as dot_file:
        dot_file.write(visualizer.get_dot())

    print(f"[green]El archivo DOT ha sido generado como 'ast_output.dot'. [/green]")
