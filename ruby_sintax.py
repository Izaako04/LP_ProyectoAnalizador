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

# Aporte Paulette Maldonado
def p_sentencia_impresion(p):
    '''
    sentencia_impresion : PUTS expresion
                        | PRINT expresion
                        | PRINTF expresion
    '''
    p[0] = ('imprimir', p[1], p[2])

# Aporte Paulette Maldonado
def p_sentencia_entrada(p):
    '''
    sentencia_entrada : GETS encadenamiento_metodos_opcional
    '''
    p[0] = ('entrada', p[1], p[2])

# Aporte Paulette Maldonado
def p_encadenamiento_metodos_opcional(p):
    '''
    encadenamiento_metodos_opcional : PUNTO ID PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER encadenamiento_metodos_opcional %prec DOT_CALL
                                    | PUNTO ID PARENTESIS_IZQ PARENTESIS_DER encadenamiento_metodos_opcional %prec DOT_CALL
                                    | PUNTO ID encadenamiento_metodos_opcional %prec DOT_CALL
                                    | PUNTO TO_I encadenamiento_metodos_opcional %prec DOT_CALL
                                    | PUNTO TO_F encadenamiento_metodos_opcional %prec DOT_CALL
                                    | PUNTO TO_S encadenamiento_metodos_opcional %prec DOT_CALL
                                    | CHOMP encadenamiento_metodos_opcional
                                    | vacio
    '''
    if len(p) > 1 and p[1] == '.':
        if len(p) == 6:
            p[0] = [('llamada_metodo', p[2], p[4])] + p[6]
        elif len(p) == 5:
            p[0] = [('llamada_metodo', p[2], [])] + p[5]
        elif len(p) == 4:
            p[0] = [('llamada_metodo', p[2], None)] + p[3]
    elif len(p) == 3:
        p[0] = [('llamada_metodo', p[1], None)] + p[2]
    else:
        p[0] = []

# Aporte Isaac Criollo
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

# Aporte Isaac Criollo
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

# Aporte Joel Guamani
def p_sentencia_condicional(p):
    '''
    sentencia_condicional : IF expresion THEN sentencias END
                          | IF expresion THEN sentencias ELSE sentencias END
                          | IF expresion THEN sentencias CLAUSULAS_ELSIF END
                          | IF expresion THEN sentencias CLAUSULAS_ELSIF ELSE sentencias END
                          | UNLESS expresion THEN sentencias END
                          | UNLESS expresion THEN sentencias ELSE sentencias END
                          | CASE expresion sentencias_when_case END
    '''
    if p[1] == 'if':
        if len(p) == 5:
            p[0] = ('si', p[2], p[4], None, None)
        elif len(p) == 7:
            p[0] = ('si_sino', p[2], p[4], p[6])
        elif len(p) == 6:
            p[0] = ('si_sino_si', p[2], p[4], p[5], None)
        elif len(p) == 8:
            p[0] = ('si_sino_si_sino', p[2], p[4], p[5], p[7])
    elif p[1] == 'unless':
        if len(p) == 5:
            p[0] = ('a_menos_que', p[2], p[4], None)
        else:
            p[0] = ('a_menos_que_sino', p[2], p[4], p[6])
    elif p[1] == 'case':
        p[0] = ('caso', p[2], p[3])

def p_CLAUSULAS_ELSIF(p):
    '''
    CLAUSULAS_ELSIF : ELSIF expresion THEN sentencias
                    | CLAUSULAS_ELSIF ELSIF expresion THEN sentencias
    '''
    if len(p) == 5:
        p[0] = [('sino_si', p[2], p[4])]
    else:
        p[0] = p[1] + [('sino_si', p[3], p[5])]

# Aporte Joel Guamani
def p_sentencias_when_case(p):
    '''
    sentencias_when_case : WHEN expresion THEN sentencias
                         | sentencias_when_case WHEN expresion THEN sentencias
                         | sentencias_when_case ELSE sentencias
    '''
    if len(p) == 5:
        p[0] = [('cuando', p[2], p[4])]
    elif len(p) == 4:
        p[0] = p[1] + [('rama_sino', p[2])]
    else:
        p[0] = p[1] + [('cuando', p[3], p[5])]

def p_expresion_comparacion(p):
    '''
    expresion : expresion IGUAL expresion
              | expresion DIFERENTE expresion
              | expresion MAYOR_QUE expresion
              | expresion MENOR_QUE expresion
              | expresion MAYOR_IGUAL expresion
              | expresion MENOR_IGUAL expresion
              | expresion NAVE_ESPACIAL expresion
              | expresion TRIPLE_IGUAL expresion
    '''
    p[0] = ('comparacion', p[2], p[1], p[3])

def p_expresion_logica(p):
    '''
    expresion : expresion AND_LOGICO expresion
              | expresion OR_LOGICO expresion
              | expresion Y_SIGNO expresion
              | expresion O_SIGNO expresion
    '''
    p[0] = ('operador_logico', p[2], p[1], p[3])

def p_expresion_negacion(p):
    '''
    expresion : NOT_LOGICO expresion
              | EXCLAMACION_BAJO expresion
    '''
    p[0] = ('negacion', p[2])

# Aporte Isaac Criollo
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

# Aporte Paulette Maldonado: Array
def p_creacion_array(p):
    '''
    creacion_estructura_datos : CORCHETE_IZQ elementos_array CORCHETE_DER
                              | CORCHETE_IZQ CORCHETE_DER
    '''
    if len(p) == 3:
        p[0] = ('arreglo', [])
    else:
        p[0] = ('arreglo', p[2])

def p_elementos_array(p):
    '''
    elementos_array : expresion
                    | elementos_array COMA expresion
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

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

# Aporte Joel Guamani: Hash
def p_creacion_hash(p):
    '''
    creacion_estructura_datos : LLAVE_IZQ elementos_hash LLAVE_DER
                              | LLAVE_IZQ LLAVE_DER
    '''
    if len(p) == 3:
        p[0] = ('hash', [])
    else:
        p[0] = ('hash', p[2])

def p_elementos_hash(p):
    '''
    elementos_hash : elemento_hash
                   | elementos_hash COMA elemento_hash
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_elemento_hash(p):
    '''
    elemento_hash : expresion ASIGNA_HASH expresion
                  | SIMBOLO DOS_PUNTOS expresion
    '''
    if len(p) == 4 and p[2] == '=>':
        p[0] = ('par_hash', p[1], p[3])
    else:
        p[0] = ('par_hash', p[1], p[3])

# Aporte Isaac Criollo: Bucle While
def p_bucle_while(p):
    '''
    sentencia_bucle : WHILE expresion DO sentencias END
                    | WHILE expresion sentencias END
    '''
    p[0] = ('bucle_mientras', p[2], p[4] if len(p) == 5 else p[3])

# Aporte Joel Guamani: Bucle For (each en Ruby)
def p_bucle_for_each(p):
    '''
    sentencia_bucle : ID PUNTO EACH bloque_o_do_end
    '''
    p[0] = ('bucle_para_cada', p[1], p[4])

def p_bloque_o_do_end(p):
    '''
    bloque_o_do_end : DO sentencias END
                    | LLAVE_IZQ argumentos_bloque PIPE sentencias LLAVE_DER
    '''
    if p[1] == 'do':
        p[0] = p[2]
    else:
        p[0] = ('bloque', p[2], p[4])

# Aporte Paulette Maldonado: Bucle Loop
def p_bucle_general(p):
    '''
    sentencia_bucle : LOOP DO sentencias END
                    | LOOP LLAVE_IZQ sentencias LLAVE_DER
    '''
    p[0] = ('bucle_infinito', p[3] if p[2] == 'do' else p[2])

def p_argumentos_bloque(p):
    '''
    argumentos_bloque : ID
                      | ID COMA argumentos_bloque
                      | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = [p[1]] + p[3]

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

# Aporte Paulette Maldonado (Llamada a función/método)
def p_llamada_metodo(p):
    '''
    llamada_metodo : ID PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER encadenamiento_mas_metodos
                   | ID PARENTESIS_IZQ PARENTESIS_DER encadenamiento_mas_metodos
                   | ID encadenamiento_mas_metodos
                   | ID PUNTO llamada_metodo
                   | ID_GLOBAL PUNTO llamada_metodo
                   | ID_INSTANCIA PUNTO llamada_metodo
                   | ID_CLASE PUNTO llamada_metodo
                   | SIMBOLO PUNTO llamada_metodo
                   | SELF PUNTO llamada_metodo
    '''
    if len(p) == 6:
        p[0] = ('llamada_funcion', p[1], p[3], p[5])
    elif len(p) == 5:
        p[0] = ('llamada_funcion', p[1], [], p[4])
    elif len(p) == 3 and p[2] not in ['.', '?', '!']:
        p[0] = ('llamada_funcion', p[1], None, p[2])
    elif len(p) == 4 and p[2] == '.':
        p[0] = ('cadena_metodos', p[1], p[3])
    else:
        p[0] = ('llamada_funcion', p[1], None, [])

def p_encadenamiento_mas_metodos(p):
    '''
    encadenamiento_mas_metodos : PUNTO ID PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO ID PARENTESIS_IZQ PARENTESIS_DER encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO ID encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO METODO_PREGUNTA encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO METODO_EXCLAMACION encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO TO_I encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO TO_F encadenamiento_mas_metodos %prec DOT_CALL
                               | PUNTO TO_S encadenamiento_mas_metodos %prec DOT_CALL
                               | CHOMP encadenamiento_mas_metodos
                               | vacio
    '''
    if len(p) > 1 and p[1] == '.':
        if len(p) == 6:
            p[0] = [('llamada_encadenada', p[2], p[4])] + p[6]
        elif len(p) == 5:
            p[0] = [('llamada_encadenada', p[2], [])] + p[5]
        elif len(p) == 4:
            p[0] = [('llamada_encadenada', p[2], None)] + p[3]
    elif len(p) == 3:
        p[0] = [('llamada_encadenada', p[1], None)] + p[2]
    else:
        p[0] = []

def p_argumentos_metodo(p):
    '''
    argumentos_metodo : expresion
                      | argumentos_metodo COMA expresion
                      | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]]

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

# Aporte Paulette Maldonado: Método 'initialize' (constructor)
def p_metodo_inicializacion(p):
    '''
    metodo_inicializacion : DEF INITIALIZE PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                          | DEF INITIALIZE sentencias END
    '''
    if len(p) == 8:
        p[0] = ('metodo_inicializacion', p[4], p[6])
    else:
        p[0] = ('metodo_inicializacion', [], p[3])

# Aporte Paulette Maldonado: BEGIN...RESCUE...END
def p_sentencia_begin_rescue(p):
    '''
    sentencia_begin_rescue : BEGIN sentencias clausulas_rescue_opcional END
    '''
    p[0] = ('begin_rescue', p[2], p[3])

def p_clausulas_rescue_opcional(p):
    '''
    clausulas_rescue_opcional : clausula_rescue clausulas_rescue_opcional
                              | clausula_ensure
                              | vacio
    '''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_clausula_rescue(p):
    '''
    clausula_rescue : RESCUE sentencias
                    | RESCUE identificador_variable ASIGNA_HASH ID sentencias
                    | RESCUE ID ASIGNA_HASH ID sentencias
                    | RESCUE ID sentencias
                    | RESCUE ID_CLASE sentencias
    '''
    if len(p) == 3:
        p[0] = ('captura_excepcion', None, None, p[2])
    elif len(p) == 6:
        p[0] = ('captura_excepcion', p[2], p[4], p[5])
    elif len(p) == 4:
        p[0] = ('captura_excepcion', p[2], None, p[3])

def p_clausula_ensure(p):
    '''
    clausula_ensure : ENSURE sentencias
    '''
    p[0] = ('asegurar', p[2])

def p_error(p):
    global errores_sintacticos
    if p:
        error_msg = f"Error de sintaxis en el token '{p.type}' ('{p.value}') en la línea {p.lineno}, columna {p.lexpos}"
        print(error_msg)
        errores_sintacticos.append(error_msg)
    else:
        error_msg = "Error de sintaxis en EOF (fin de archivo inesperado)."
        print(error_msg)
        errores_sintacticos.append(error_msg)

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