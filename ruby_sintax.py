import ply.yacc as yacc
import os
import datetime
from ruby_lexer import tokens, lexer

ruta_carpeta_logs = "logs"
ruta_archivos_ruby = "algoritmos"

errores_sintacticos = []

# --- Reglas de precedencia y asociatividad ---
# Aporte Isaac Criollo
precedence = (
    ('left', 'OR_LOGICO', 'O_SIGNO'),
    ('left', 'AND_LOGICO', 'Y_SIGNO'),
    ('left', 'IGUAL', 'DIFERENTE', 'MAYOR_IGUAL', 'MENOR_IGUAL', 'MAYOR_QUE', 'NAVE_ESPACIAL', 'TRIPLE_IGUAL'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULTIPLICACION', 'DIVISION', 'MODULO', 'PORCENTAJE'),
    ('right', 'UMINUS', 'NOT_LOGICO', 'EXCLAMACION_BAJO', 'METODO_EXCLAMACION'),
    ('right', 'EXPONENCIACION'),
    ('left', 'DOT_CALL')
)

# --- Definición de la gramática (reglas de producción) ---

def p_programa(p):
    '''
    programa : sentencias
    '''
    p[0] = p[1]

def p_sentencias(p):
    '''
    sentencias : sentencia
               | sentencias sentencia
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_sentencia(p):
    '''
    sentencia : sentencia_impresion
              | sentencia_entrada
              | sentencia_asignacion
              | expresion
              | sentencia_condicional
              | sentencia_bucle
              | definicion_metodo
              | definicion_clase
              | creacion_estructura_datos
              | sentencia_begin_rescue
              | metodo_inicializacion
              | RETURN expresion
              | RETURN
              | BREAK
              | BREAK expresion
              | NEXT
              | NEXT expresion
              | REDO
              | RETRY
              | YIELD
              | YIELD argumentos_metodo
              | SUPER
              | SUPER argumentos_metodo
              | vacio
    '''
    if p[1] == 'return':
        p[0] = ('retornar', p[2] if len(p) > 2 else None)
    elif p[1] == 'break':
        p[0] = ('romper', p[2] if len(p) > 2 else None)
    elif p[1] == 'next':
        p[0] = ('siguiente', p[2] if len(p) > 2 else None)
    elif p[1] == 'redo':
        p[0] = ('rehacer',)
    elif p[1] == 'retry':
        p[0] = ('reintentar',)
    elif p[1] == 'yield':
        p[0] = ('ceder', p[2] if len(p) > 2 else [])
    elif p[1] == 'super':
        p[0] = ('super', p[2] if len(p) > 2 else [])
    else:
        p[0] = p[1]

def p_vacio(p):
    '''
    vacio :
    '''
    pass

def p_expresion_aritmetica(p):
    '''
    expresion : expresion MAS expresion
              | expresion MENOS expresion
              | expresion MULTIPLICACION expresion
              | expresion DIVISION expresion
              | expresion MODULO expresion
              | expresion EXPONENCIACION expresion
    '''
    p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_expresion_unaria_menos(p):
    '''
    expresion : MENOS expresion %prec UMINUS
    '''
    p[0] = ('unario_menos', p[2])

def p_expresion_agrupada(p):
    '''
    expresion : PARENTESIS_IZQ expresion PARENTESIS_DER
    '''
    p[0] = p[2]

def p_termino_expresion(p):
    '''
    expresion : ENTERO
              | FLOTANTE
              | ID
              | VARIABLECLASE
              | ID_INSTANCIA
              | ID_GLOBAL
              | ID_CLASE
              | CADENA
              | CADENA_SIMPLE
              | CADENA_INTERPOLADA
              | TRUE
              | FALSE
              | NIL
              | SIMBOLO
              | REGEX
              | llamada_metodo
    '''
    p[0] = p[1]


def p_sentencia_asignacion(p):
    '''
    sentencia_asignacion : identificador_variable ASIGNACION expresion
                         | identificador_variable MAS_ASIGNACION expresion
                         | identificador_variable MENOS_ASIGNACION expresion
                         | identificador_variable MULT_ASIGNACION expresion
                         | identificador_variable DIV_ASIGNACION expresion
                         | identificador_variable MOD_ASIGNACION expresion
    '''
    p[0] = ('asignacion', p[2], p[1], p[3])

def p_identificador_variable(p):
    '''
    identificador_variable : ID
                           | ID_GLOBAL
                           | ID_INSTANCIA
                           | VARIABLECLASE
                           | ID_CLASE
    '''
    p[0] = p[1]


# Aporte Isaac Criollo: Set
def p_creacion_set(p):
    '''
    creacion_estructura_datos : ID PUNTO NEW PARENTESIS_IZQ elementos_array PARENTESIS_DER
                              | ID PUNTO NEW PARENTESIS_IZQ PARENTESIS_DER
    '''
    if len(p) == 6:
        p[0] = ('conjunto', p[5])
    else:
        p[0] = ('conjunto', [])

# Aporte Isaac Criollo: Bucle While
def p_bucle_while(p):
    '''
    sentencia_bucle : WHILE expresion DO sentencias END
                    | WHILE expresion sentencias END
    '''
    p[0] = ('bucle_mientras', p[2], p[4] if len(p) == 5 else p[3])



# Aporte Joel Guamani / Isaac Criollo (Definición de Función)
def p_definicion_metodo(p):
    '''
    definicion_metodo : DEF ID PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                      | DEF ID sentencias END
                      | DEF SELF PUNTO ID PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                      | DEF SELF PUNTO ID sentencias END
    '''
    if len(p) == 8:
        p[0] = ('definicion_metodo', p[2], p[4], p[6])
    elif len(p) == 5:
        p[0] = ('definicion_metodo', p[2], [], p[3])
    elif len(p) == 10:
        p[0] = ('definicion_metodo_clase', p[4], p[6], p[8])
    elif len(p) == 7:
        p[0] = ('definicion_metodo_clase', p[4], [], p[5])

def p_lista_parametros(p):
    '''
    lista_parametros : ID
                     | ID COMA lista_parametros
                     | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = [p[1]] + p[3]


# Aporte Isaac Criollo: Definición de Clase
def p_definicion_clase(p):
    '''
    definicion_clase : CLASS ID cuerpo_clase END
                     | CLASS ID MENOR_QUE ID cuerpo_clase END
    '''
    if len(p) == 5:
        p[0] = ('definicion_clase', p[2], None, p[3])
    else:
        p[0] = ('definicion_clase', p[2], p[4], p[5])

def p_cuerpo_clase(p):
    '''
    cuerpo_clase : sentencias
                 | vacio
    '''
    p[0] = p[1]

parser = yacc.yacc(debug=True)

def analizar_archivo_ruby(nombre_archivo, usuario_git):
    os.makedirs(ruta_carpeta_logs, exist_ok=True)
    ruta_completa_archivo = os.path.join(ruta_archivos_ruby, nombre_archivo)

    global errores_sintacticos
    errores_sintacticos = []

    try:
        with open(ruta_completa_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        print(f"\n--- Analizando sintácticamente: {nombre_archivo} (Usuario: {usuario_git}) ---")
        arbol_sintactico = parser.parse(codigo, lexer=lexer)

        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        nombre_archivo_log = f"sintactico-{usuario_git}-{timestamp}.txt"
        ruta_archivo_log = os.path.join(ruta_carpeta_logs, nombre_archivo_log)

        with open(ruta_archivo_log, 'w', encoding='utf-8') as archivo_log:
            archivo_log.write(f"Análisis sintáctico de: {nombre_archivo}\n")
            archivo_log.write(f"Usuario: {usuario_git}\n")
            archivo_log.write(f"Fecha y Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            archivo_log.write("="*50 + "\n")

            if errores_sintacticos:
                archivo_log.write("Errores sintácticos encontrados:\n")
                for error in errores_sintacticos:
                    archivo_log.write(f"- {error}\n")
                print(f"Análisis completado con errores. Detalles en: {ruta_archivo_log}")
            else:
                archivo_log.write("No se encontraron errores sintácticos.\n")
                print(f"Análisis sintáctico exitoso. Log en: {ruta_archivo_log}")

    except FileNotFoundError:
        print(f"Error: El archivo {ruta_completa_archivo} no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer o analizar el archivo: {e}")

if __name__ == '__main__':
    analizar_archivo_ruby("algoritmo1_Paulette_Maldonado.rb", "Pauyamal")
    analizar_archivo_ruby("algoritmo2_Isaac_Criollo.rb", "Isaac_Criollo")
    analizar_archivo_ruby("algoritmo3_Joel_Guamani.rb", "Joel_Guamani")