'''

Archivo principal, donde se ejecuta todo lo que se requiera
del compilador mini cpp

'''

from CppContext import Context
from rich import print
from render import DotRender
from tabulate import tabulate


def menu():
    print("\t\t\t\n ********* BIENVENIDO AL COMPILADOR MINI C++ ********* \n")
    print("usage: Cpp.py [-h] [-d] [-o OUT] [-l] [-a] [-D] [-p] [-I] [--sym] [-S] [-R] input\n")

    print("Compiler for Mini C++ programs\n")

    print("positional arguments:")
    print("input MiniC            program file to compile\n")

    print("optional arguments:")
    print("-h, --help             show this help message and exit")
    print("-l, --lex              display tokens from lexer")
    print("-a, --AST              Display AST")
    print("-D, --dot              Generate AST graph as DOT format")
    print("-s, --sym              Dump the symbol table") #the Checker one
    print("-R, --exec             Execute the generated program")

def main(argv):
    if len(argv) == 2:
        menu()
        raise SystemExit()

    print("\t\t\t\n ********* BIENVENIDO AL COMPILADOR MINI C++ ********* \n")
    ctxt = Context()

    if len(argv) > 2:
        source = ""

        with open(argv[2]) as file:
            source = file.read()
        ctxt.parse(source)

        if ctxt.have_errors:
            if argv[1] in ["-h", "--help"]:
                menu()
        elif argv[1] in ["-l", "--lex"]:
            print("\n\n\t\t************ TOKENS ************\n\n")
            tokens = ctxt.lexer.tokenize(source)
            table=[["Type", "Value", "Line"]]
            for token in tokens:
                row = []
                row.append(token.type)
                row.append(token.value)
                row.append(token.lineno)
                table.append(row)
            print(tabulate(table, headers="firstrow", tablefmt="fancy_grid"))
        elif argv[1] in ["-a", "--AST"]:
            print("\n\n\t\t************ AST ************\n\n")
            print(ctxt.ast)
        elif argv[1] in ["-D", "--dot"]:
            print("\n\n\t\t************ AST - DOT LANGUAGE ************\n\n")
            dot = DotRender.render(ctxt.ast)
            with open('ast_output.dot', 'w') as dot_file:
                dot_file.write(str(dot))

            print(f"[green]El archivo DOT ha sido generado como 'ast_output.dot'. [/green] \n")
            
            print(dot)
        elif argv[1] in ["-s", "--sym"]:
            print("\n\n\t\t************ SYMBOL TABLE ************\n\n")
            print(ctxt.interp.env)
        elif argv[1] in ["-R", "--exec"]:
            print("\n\n\t\t************ OUTPUT ************\n\n")
            ctxt.run()
        else:
            print("Invalid option")
            op = int(input("Do you want to see the menu? (1: Yes, 0: No) "))
            if op == 1:
                menu()
    else:
        try:
            while True:
                source = input("MiniC++ > ")
                ctxt.parse(source)
                if ctxt.have_errors:
                    continue

                for stmt in ctxt.ast.decl:
                    ctxt.ast = stmt
                    ctxt.run()
        except EOFError:
            pass


if __name__ == "__main__":
    from sys import argv
    main(argv)