test_cases = [
    {
        "description": "Prueba con declaración de clase simple",
        "code": '''class Hola {
            int a = 5;
            float b = 5.5;
            printf("Hola mundo\n");
        }'''
    },
    {
        "description": "Prueba con un bucle while",
        "code": '''int i = 0;
        while (i < 10) {
            i = i + 1;
        }'''
    },
    {
        "description": "Prueba con declaración de función con retorno",
        "code": '''int suma(int a, int b) {
            return a + b;
        }'''
    },
    {
        "description": "Prueba con operador lógico AND y OR",
        "code": '''bool resultado = true && false || true;'''
    },
    {
        "description": "Prueba con declaración de array",
        "code": '''int arr[5] = {1, 2, 3, 4, 5};'''
    },
    {
        "description": "Prueba con estructura if-else",
        "code": '''if (a < b) {
            printf("a es menor que b");
        } else {
            printf("a es mayor o igual que b\n");
        }'''
    },
    {
        "description": "Prueba con constructor de clase",
        "code": '''class Persona {
            public:
            Persona() {
                nombre = "Juan";
            }
            private:
            string nombre;
        };'''
    },
    {
        "description": "Prueba con función miembro de clase",
        "code": '''class Calculadora {
            public:
            int multiplicar(int a, int b) {
                return a * b;
            }
        };'''
    },
    {
        "description": "Prueba con declaración de destructor",
        "code": '''class Recurso {
            public:
            ~Recurso() {
                liberarMemoria();
            }
        };'''
    }
]
