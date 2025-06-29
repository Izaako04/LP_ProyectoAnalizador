import ply.yacc as yacc
import os
import datetime
from ruby_lexer import tokens, lexer

# --- Variables Globales ---
ruta_carpeta_logs = "logs"
ruta_archivos_ruby = "algoritmos"
tabla_variables = {}
errores_semanticos = []
errores_sintacticos = []

# --- Reglas de Precedencia y Asociatividad ---
precedence = (
    ('right', 'IF', 'UNLESS'),
    ('right', 'ASIGNACION', 'MAS_ASIGNACION', 'MENOS_ASIGNACION', 'MULT_ASIGNACION', 'DIV_ASIGNACION', 'MOD_ASIGNACION'),
    ('left', 'OR_LOGICO', 'O_SIGNO', 'OR'),
    ('left', 'AND_LOGICO', 'Y_SIGNO', 'AND'),
    ('nonassoc', 'IGUAL', 'DIFERENTE', 'MAYOR_IGUAL', 'MENOR_IGUAL', 'MAYOR_QUE', 'MENOR_QUE', 'NAVE_ESPACIAL', 'TRIPLE_IGUAL'),
    ('left', 'APPEND'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULTIPLICACION', 'DIVISION', 'MODULO'),
    ('right', 'EXPONENCIACION'),
    ('right', 'UMINUS', 'NOT_LOGICO', 'EXCLAMACION_BAJO', 'NOT'),
    ('left', 'PUNTO'),
)

# --- Definición de la Gramática (Reglas de Producción) ---

def p_programa(p):
    '''
    programa : sentencias
             | vacio
    '''
    p[0] = p[1]

def p_sentencias(p):
    '''
    sentencias : sentencia
               | sentencias sentencia
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        if p[2] is not None:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = p[1]

def p_sentencia(p):
    '''
    sentencia : expresion
              | sentencia_asignacion
              | sentencia_condicional
              | sentencia_bucle
              | definicion_metodo
              | definicion_clase
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
              | RAISE expresion
              | vacio
    '''
    if len(p) == 1:
        p[0] = None
        return

    # La mayoría de las sentencias son ahora expresiones,
    # así que solo manejamos las palabras clave específicas aquí.
    keyword = p[1]
    if isinstance(keyword, str):
        if keyword == 'return':
            p[0] = ('retornar', p[2] if len(p) > 2 else None)
        elif keyword == 'break':
            p[0] = ('romper', p[2] if len(p) > 2 else None)
        elif keyword == 'next':
            p[0] = ('siguiente', p[2] if len(p) > 2 else None)
        elif keyword == 'redo':
            p[0] = ('rehacer',)
        elif keyword == 'retry':
            p[0] = ('reintentar',)
        elif keyword == 'yield':
            p[0] = ('ceder', p[2] if len(p) > 2 else [])
        elif keyword == 'super':
            p[0] = ('super', p[2] if len(p) > 2 else [])
        elif keyword == 'raise':
            p[0] = ('raise', p[2])
        else:
            p[0] = p[1] # Para el resto de no-terminales
    else:
        p[0] = p[1] # Para 'expresion', etc.

def p_vacio(p):
    '''vacio :'''
    pass

def p_sentencia_modificador(p):
    '''
    sentencia : sentencia IF expresion
              | sentencia UNLESS expresion
    '''
    p[0] = ('modificador_if' if p[2] == 'if' else 'modificador_unless', p[1], p[3])

# --- NUEVA JERARQUÍA DE EXPRESIONES (ROBUSTA) ---

def p_expresion(p):
    '''
    expresion : llamada
              | expresion MAS expresion
              | expresion MENOS expresion
              | expresion MULTIPLICACION expresion
              | expresion DIVISION expresion
              | expresion MODULO expresion
              | expresion EXPONENCIACION expresion
              | expresion APPEND expresion
              | MENOS expresion %prec UMINUS
              | expresion IGUAL expresion
              | expresion DIFERENTE expresion
              | expresion MAYOR_QUE expresion
              | expresion MENOR_QUE expresion
              | expresion MAYOR_IGUAL expresion
              | expresion MENOR_IGUAL expresion
              | expresion NAVE_ESPACIAL expresion
              | expresion TRIPLE_IGUAL expresion
              | expresion AND_LOGICO expresion
              | expresion OR_LOGICO expresion
              | expresion Y_SIGNO expresion
              | expresion O_SIGNO expresion
              | expresion AND expresion
              | expresion OR expresion
              | NOT_LOGICO expresion
              | EXCLAMACION_BAJO expresion
              | NOT expresion
              | expresion RESCUE expresion
              | PUTS expresion
              | PRINT expresion
              | PRINTF expresion
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] in ['puts', 'print', 'printf']:
        p[0] = ('imprimir', p[1], p[2])
    elif p[1] in ['!', 'not']:
        p[0] = ('negacion', p[2])
    elif p[1] == '-':
        p[0] = ('unario_menos', p[2])
    elif p[2] == 'rescue':
        p[0] = ('rescue_inline', p[1], p[3])
    else: # Operación binaria
        p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_llamada(p):
    '''
    llamada : primario
            | llamada PUNTO metodo_id
            | llamada PUNTO metodo_id PARENTESIS_IZQ PARENTESIS_DER
            | llamada PUNTO metodo_id PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER
            | llamada CORCHETE_IZQ expresion CORCHETE_DER
            | llamada bloque_o_do_end
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[2] == '.':
        if len(p) == 4:
            p[0] = ('llamada_metodo', p[1], p[3], [])
        elif len(p) == 6: 
            p[0] = ('llamada_metodo', p[1], p[3], [])
        else:
            p[0] = ('llamada_metodo', p[1], p[3], p[5])
    elif p[2] == '[':
        p[0] = ('acceso_elemento', p[1], p[3])
    else:
        p[0] = ('expresion_con_bloque', p[1], p[2])

def p_metodo_id(p):
    '''
    metodo_id : ID
              | METODO_PREGUNTA
              | METODO_EXCLAMACION
              | TO_I
              | TO_F
              | TO_S
              | CHOMP
              | EACH
              | EMPTY
              | INCLUDE
              | MATCH
              | SPLIT
              | ADD
              | SIZE
              | MAX
              | MIN
              | SUM
              | PRINT
              | PRINTF
              | CONCAT
              | SORT
              | TO_SET
    '''
    p[0] = p[1]

def p_primario(p):
    '''
    primario : literal
             | identificador_variable
             | PARENTESIS_IZQ expresion PARENTESIS_DER
             | GETS
             | creacion_array
             | creacion_hash
    '''
    if p[1] == '(':
        p[0] = p[2]
    else:
        p[0] = p[1]

def p_literal(p):
    '''
    literal : ENTERO
            | FLOTANTE
            | CADENA
            | CADENA_SIMPLE
            | CADENA_INTERPOLADA
            | TRUE
            | FALSE
            | NIL
            | SIMBOLO
            | REGEX
    '''
    p[0] = p[1]

# --- FIN DE LA NUEVA JERARQUÍA DE EXPRESIONES ---

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

def p_creacion_array(p):
    '''
    creacion_array : CORCHETE_IZQ elementos_array CORCHETE_DER
                   | CORCHETE_IZQ CORCHETE_DER
    '''
    p[0] = ('arreglo', p[2] if len(p) == 4 else [])

def p_elementos_array(p):
    '''
    elementos_array : expresion
                    | elementos_array COMA expresion
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def evaluar_expresion(nodo):
    """Evalúa un nodo del AST para obtener su valor concreto."""
    if not isinstance(nodo, tuple):
        return nodo
        
    tipo = nodo[0]
    
    if tipo == 'operacion_binaria':
        _, op, izq, der = nodo
        izq_val = evaluar_expresion(izq)
        der_val = evaluar_expresion(der)
        
        if op == '+': return izq_val + der_val
        if op == '-': return izq_val - der_val
        if op == '*': return izq_val * der_val
        if op == '/': return izq_val / der_val
        if op == '%': return izq_val % der_val
        if op == '**': return izq_val ** der_val
        
    elif tipo == 'comparacion':
        _, op, izq, der, _ = nodo
        izq_val = evaluar_expresion(izq)
        der_val = evaluar_expresion(der)
        
        if op == '==': return izq_val == der_val
        if op == '!=': return izq_val != der_val
        if op == '>': return izq_val > der_val
        if op == '<': return izq_val < der_val
        if op == '>=': return izq_val >= der_val
        if op == '<=': return izq_val <= der_val
        
    elif tipo == 'unario_menos':
        return -evaluar_expresion(nodo[1])
        
    elif tipo == 'negacion':
        return not evaluar_expresion(nodo[1])
        
    return None


def p_creacion_hash(p):
    '''
    creacion_hash : LLAVE_IZQ elementos_hash LLAVE_DER
                  | LLAVE_IZQ LLAVE_DER
    '''
    p[0] = ('hash', p[2] if len(p) == 4 else [])

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
                  | ID DOS_PUNTOS expresion
    '''
    p[0] = ('par_hash', p[1], p[3])

def p_sentencia_condicional(p):
    '''
    sentencia_condicional : IF expresion optional_then sentencias END
                          | IF expresion optional_then sentencias ELSE sentencias END
                          | IF expresion optional_then sentencias CLAUSULAS_ELSIF END
                          | IF expresion optional_then sentencias CLAUSULAS_ELSIF ELSE sentencias END
                          | UNLESS expresion optional_then sentencias END
                          | UNLESS expresion optional_then sentencias ELSE sentencias END
                          | CASE expresion sentencias_when_case END
                          | CASE sentencias_when_case END
    '''
    # Manejo específico para CASE
    if p[1] == 'case':
        if len(p) == 5:  # CASE sentencias_when_case END
            p[0] = ('case', None, p[2])
        else:  # CASE expresion sentencias_when_case END
            p[0] = ('case', p[2], p[3])
    else:
        # Para IF y UNLESS - simplificado
        if len(p) == 6:  # IF expresion optional_then sentencias END
            p[0] = ('condicional', p[1], p[2], p[4], None)
        elif len(p) == 8:  # IF expresion optional_then sentencias ELSE sentencias END
            p[0] = ('condicional', p[1], p[2], p[4], p[6])

def p_optional_then(p):
    '''optional_then : THEN
                     | vacio'''
    pass

def p_CLAUSULAS_ELSIF(p):
    '''
    CLAUSULAS_ELSIF : ELSIF expresion optional_then sentencias
                    | CLAUSULAS_ELSIF ELSIF expresion optional_then sentencias
    '''
    if len(p) == 5:
        p[0] = [('sino_si', p[2], p[4])]
    else:
        p[0] = p[1] + [('sino_si', p[3], p[5])]

def p_sentencias_when_case(p):
    '''
    sentencias_when_case : lista_clausulas_when
                         | lista_clausulas_when ELSE sentencias
    '''
    if len(p) == 2:
        # Solo una lista de cláusulas 'when'
        p[0] = p[1]
    else:
        # Lista de 'when' seguida por un 'else'
        p[0] = p[1] + [('rama_sino', p[3])]

def p_lista_clausulas_when(p):
    '''
    lista_clausulas_when : clausula_when
                         | lista_clausulas_when clausula_when
    '''
    if len(p) == 2:
        # Es la primera cláusula 'when' que se encuentra
        p[0] = [p[1]]
    else:
        # Se agrega otra cláusula 'when' a la lista existente
        p[0] = p[1] + [p[2]]

def p_clausula_when(p):
    '''
    clausula_when : WHEN expresion sentencias
    '''
    # Crea la tupla para una única cláusula 'when'
    p[0] = ('cuando', p[2], p[3])

def p_bucle_while(p):
    '''
    sentencia_bucle : WHILE expresion optional_do sentencias END
    '''
    p[0] = ('bucle_mientras', p[2], p[4])

def p_optional_do(p):
    '''optional_do : DO
                   | vacio'''
    pass

def p_bucle_general(p):
    '''
    sentencia_bucle : LOOP bloque_o_do_end
    '''
    p[0] = ('bucle_infinito', p[2])

def p_bloque_o_do_end(p):
    '''
    bloque_o_do_end : DO PIPE argumentos_bloque PIPE sentencias END
                    | DO sentencias END
                    | LLAVE_IZQ PIPE argumentos_bloque PIPE sentencias LLAVE_DER
                    | LLAVE_IZQ sentencias LLAVE_DER
    '''
    if p[1] == 'do':
        p[0] = ('bloque', p[3] if len(p) == 6 else [], p[5] if len(p) == 6 else p[2])
    else:
        p[0] = ('bloque', p[3] if len(p) == 6 else [], p[5] if len(p) == 6 else p[2])


def p_argumentos_bloque(p):
    '''
    argumentos_bloque : ID
                      | argumentos_bloque COMA ID
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_definicion_metodo(p):
    '''
    definicion_metodo : DEF ID PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                      | DEF ID sentencias END
                      | DEF SELF PUNTO ID PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                      | DEF SELF PUNTO ID sentencias END
    '''
    if p[2] == 'self':
        p[0] = ('def_self', p[4], p[6] if len(p) == 9 else [], p[8] if len(p) == 9 else p[5])
    else:
        p[0] = ('def', p[2], p[4] if len(p) == 8 else [], p[6] if len(p) == 8 else p[3])

def p_lista_parametros(p):
    '''
    lista_parametros : ID
                     | lista_parametros COMA ID
                     | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]] if len(p) > 2 else []

def p_argumentos_metodo(p):
    '''
    argumentos_metodo : expresion
                      | argumentos_metodo COMA expresion
                      | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    elif len(p) > 2:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []

def p_definicion_clase(p):
    '''
    definicion_clase : CLASS ID cuerpo_clase END
                     | CLASS ID MENOR_QUE ID cuerpo_clase END
    '''
    if len(p) == 5:
        p[0] = ('clase', p[2], None, p[3])
    else:
        p[0] = ('clase', p[2], p[4], p[5])

def p_cuerpo_clase(p):
    '''
    cuerpo_clase : sentencias
                 | vacio
    '''
    p[0] = p[1]

def p_metodo_inicializacion(p):
    '''
    metodo_inicializacion : DEF INITIALIZE PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                          | DEF INITIALIZE sentencias END
    '''
    if len(p) == 8:
        p[0] = ('inicializar', p[4], p[6])
    else:
        p[0] = ('inicializar', [], p[3])

# CORRECCIÓN PRINCIPAL: Manejo completo de begin-rescue-end
def p_sentencia_begin_rescue(p):
    '''
    sentencia_begin_rescue : BEGIN sentencias rescue_clauses END
                           | BEGIN sentencias rescue_clauses ensure_clause END
                           | BEGIN sentencias ensure_clause END
                           | BEGIN sentencias END
    '''
    if len(p) == 5:  # BEGIN sentencias END
        p[0] = ('begin', p[2], [], None)
    elif len(p) == 6:  # BEGIN sentencias rescue_clauses END o BEGIN sentencias ensure_clause END
        if isinstance(p[3], list) and p[3] and p[3][0][0] == 'rescue':
            p[0] = ('begin', p[2], p[3], None)
        else:
            p[0] = ('begin', p[2], [], p[3])
    else:  # BEGIN sentencias rescue_clauses ensure_clause END
        p[0] = ('begin', p[2], p[3], p[4])

def p_rescue_clauses(p):
    '''
    rescue_clauses : rescue_clause
                   | rescue_clauses rescue_clause
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_rescue_clause(p):
    '''
    rescue_clause : RESCUE ASIGNA_HASH ID sentencias
                  | RESCUE ID_CLASE ASIGNA_HASH ID sentencias
                  | RESCUE ID_CLASE sentencias
                  | RESCUE ID sentencias
                  | RESCUE sentencias
    '''
    if len(p) == 5:
        if p[2] == '=>':
            # rescue => variable sentencias
            p[0] = ('rescue', None, p[3], p[4])
        else:
            # rescue ExceptionClass sentencias o rescue variable sentencias
            p[0] = ('rescue', p[2], None, p[3])
    elif len(p) == 6:
        # rescue ExceptionClass => variable sentencias
        p[0] = ('rescue', p[2], p[4], p[5])
    else:
        # rescue sentencias
        p[0] = ('rescue', None, None, p[2])

def p_ensure_clause(p):
    '''
    ensure_clause : ENSURE sentencias
    '''
    p[0] = ('ensure', p[2])

def p_clausulas_rescue_opcional(p):
    '''
    clausulas_rescue_opcional : clausula_rescue clausulas_rescue_opcional
                              | clausula_ensure
                              | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    elif len(p) == 3:
        p[0] = [p[1]] + p[2] if p[1] else p[2]
    else:
        p[0] = []

def p_clausula_rescue(p):
    '''
    clausula_rescue : RESCUE ID ASIGNA_HASH ID sentencias
                    | RESCUE ASIGNA_HASH ID sentencias
                    | RESCUE ID_CLASE sentencias
                    | RESCUE ID sentencias
                    | RESCUE sentencias
    '''
    if len(p) == 6:
        # Corresponde a: RESCUE ID ASIGNA_HASH ID sentencias
        p[0] = ('captura_excepcion', p[2], p[4], p[5])
    elif len(p) == 5:
        # Corresponde a: RESCUE ASIGNA_HASH ID sentencias
        p[0] = ('captura_excepcion', None, p[3], p[4])
    elif len(p) == 4:
        # Corresponde a: RESCUE ID_CLASE sentencias o RESCUE ID sentencias
        p[0] = ('captura_excepcion', p[2], None, p[3])
    elif len(p) == 3:
        # Corresponde a: RESCUE sentencias
        p[0] = ('captura_excepcion', None, None, p[2])

def p_clausula_ensure(p):
    '''
    clausula_ensure : ENSURE sentencias
    '''
    p[0] = ('asegurar', p[2])

def p_error(p):
    global errores_sintacticos
    if p:
        start_pos = p.lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
        end_pos = p.lexer.lexdata.find('\n', p.lexpos)
        if end_pos == -1: end_pos = len(p.lexer.lexdata)
        line_content = p.lexer.lexdata[start_pos:end_pos]
        
        error_msg = (f"Error de sintaxis en la línea {p.lineno}, token '{p.type}' ('{p.value}').\n"
                     f"Línea del error: -> {line_content.strip()}")
        print(error_msg)
        errores_sintacticos.append(error_msg)
    else:
        error_msg = "Error de sintaxis en EOF (fin de archivo inesperado)."
        print(error_msg)
        errores_sintacticos.append(error_msg)

# --- Construcción del Parser y Ejecución ---

parser = yacc.yacc(debug=True)

def analizar_archivo_ruby(nombre_archivo, usuario_git):
    os.makedirs(ruta_carpeta_logs, exist_ok=True)
    ruta_completa_archivo = os.path.join(ruta_archivos_ruby, nombre_archivo)

    global errores_sintacticos
    errores_sintacticos = []
    lexer.lineno = 1

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
                if arbol_sintactico:
                    archivo_log.write("\n--- Árbol de Sintaxis Abstracta (AST) ---\n")
                    import json
                    # Usamos un pretty print para el AST
                    archivo_log.write(json.dumps(arbol_sintactico, indent=2))
                print(f"Análisis sintáctico exitoso. Log en: {ruta_archivo_log}")

    except FileNotFoundError:
        print(f"Error: El archivo {ruta_completa_archivo} no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer o analizar el archivo: {e}")
        import traceback
        traceback.print_exc()

# Funciones de verificación semánticas

# --- Analizador Semántico ---

#Aporte Isaac Criollo
def verificar_variable_declarada(nombre_variable, linea):
    if nombre_variable not in tabla_variables:
        error = f"Error semántico (línea {linea}): Variable '{nombre_variable}' no declarada."
        errores_semanticos.append(error)
        return False
    return True

def verificar_tipo_variable(nombre_variable, tipo_esperado, linea):
    if not verificar_variable_declarada(nombre_variable, linea):
        return False

    valor = tabla_variables[nombre_variable]
    tipo_real = type(valor).__name__

    tipos = {
        'numero': (int, float),
        'cadena': str,
        'booleano': bool,
        'simbolo': lambda x: isinstance(x, str) and x.startswith(':')
    }

    if tipo_esperado in tipos and not isinstance(valor, tipos[tipo_esperado]):
        error = f"Error semántico (línea {linea}): Variable '{nombre_variable}' debe ser {tipo_esperado} (tiene {tipo_real})."
        errores_semanticos.append(error)
        return False

    return True

#Aporte Paulette Maldonado
def verificar_tipos_compatibles(valor1, valor2, operador, linea):
    if isinstance(valor1, str) and valor1 in tabla_variables:
        valor1 = tabla_variables[valor1]
    if isinstance(valor2, str) and valor2 in tabla_variables:
        valor2 = tabla_variables[valor2]

    if isinstance(valor1, tuple):
        valor1 = evaluar_expresion(valor1)
    if isinstance(valor2, tuple):
        valor2 = evaluar_expresion(valor2)

    if valor1 is None or valor2 is None:
        return False

    if operador in ['+', '-', '*', '/', '**', '%']:
        if not isinstance(valor1, (int, float)) or not isinstance(valor2, (int, float)):
            error = f"Error semántico (línea {linea}): Operador '{operador}' requiere números (tipos: {type(valor1).__name__}, {type(valor2).__name__})."
            errores_semanticos.append(error)
            return False

    elif operador in ['&&', '||', 'and', 'or']:
        if not isinstance(valor1, bool) or not isinstance(valor2, bool):
            error = f"Error semántico (línea {linea}): Operador '{operador}' requiere booleanos."
            errores_semanticos.append(error)
            return False

    return True

def verificar_tipo_retorno_funcion(tipo_esperado, valor_retorno, linea):
    tipo_real = type(valor_retorno).__name__

    tipos = {
        'numero': (int, float),
        'cadena': str,
        'booleano': bool
    }

    if tipo_esperado in tipos and not isinstance(valor_retorno, tipos[tipo_esperado]):
        error = f"Error semántico (línea {linea}): Retorno debe ser {tipo_esperado} (es {tipo_real})."
        errores_semanticos.append(error)
        return False

    return True

#Aporte Joel Guamani
def verificar_estructuras_control(estructura, contexto, linea):
    if estructura in ['break', 'next'] and contexto != 'bucle':
        error = f"Error semántico (línea {linea}): '{estructura}' fuera de un bucle."
        errores_semanticos.append(error)
        return False
    return True

def verificar_alcance_variable(nombre_variable, contexto_actual, linea):
    contexto_definicion = tabla_variables.get(nombre_variable, {}).get('contexto')
    if contexto_definicion != contexto_actual:
        error = f"Error semántico (línea {linea}): Variable '{nombre_variable}' fuera del contexto en que fue definida."
        errores_semanticos.append(error)
        return False
    return True

#Aporte Comunitario
def generar_log_semantico(usuario_git):
    """Genera un archivo de log con errores semánticos."""
    if not errores_semanticos:
        print("No se encontraron errores semánticos.")

    os.makedirs(ruta_carpeta_logs, exist_ok=True)
    fecha_hora = datetime.datetime.now().strftime("%d%m%Y-%Hh%M")
    nombre_archivo = f"semantico-{usuario_git}-{fecha_hora}.txt"
    ruta_archivo = os.path.join(ruta_carpeta_logs, nombre_archivo)

    with open(ruta_archivo, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Errores semánticos - Usuario: {usuario_git}\n")
        log_file.write(f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("=" * 50 + "\n")
        for error in errores_semanticos:
            log_file.write(f"{error}\n")

    print(f"Log de errores semánticos generado: {ruta_archivo}")


def analizar_archivo_ruby(nombre_archivo, usuario_git):
    os.makedirs(ruta_carpeta_logs, exist_ok=True)
    ruta_completa_archivo = os.path.join(ruta_archivos_ruby, nombre_archivo)

    global errores_sintacticos, errores_semanticos
    errores_sintacticos = []
    errores_semanticos = []
    tabla_variables.clear()  # Limpiar tabla antes del análisis

    try:
        with open(ruta_completa_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        print(f"\n--- Analizando sintácticamente: {nombre_archivo} (Usuario: {usuario_git}) ---")
        arbol_sintactico = parser.parse(codigo, lexer=lexer)

        # Generar log sintáctico
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        nombre_archivo_log_sintactico = f"sintactico-{usuario_git}-{timestamp}.txt"
        ruta_archivo_log_sintactico = os.path.join(ruta_carpeta_logs, nombre_archivo_log_sintactico)

        with open(ruta_archivo_log_sintactico, 'w', encoding='utf-8') as archivo_log:
            archivo_log.write(f"Análisis sintáctico de: {nombre_archivo}\n")
            archivo_log.write(f"Usuario: {usuario_git}\n")
            archivo_log.write(f"Fecha y Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            archivo_log.write("=" * 50 + "\n")

            if errores_sintacticos:
                archivo_log.write("Errores sintácticos encontrados:\n")
                for error in errores_sintacticos:
                    archivo_log.write(f"- {error}\n")
                print(f"Errores sintácticos detectados. Ver: {ruta_archivo_log_sintactico}")
            else:
                archivo_log.write("No se encontraron errores sintácticos.\n")
                print(f"Análisis sintáctico exitoso. Log en: {ruta_archivo_log_sintactico}")

        # Realizar análisis semántico
        realizar_analisis_semantico(arbol_sintactico)
        
        # Generar log semántico
        generar_log_semantico(usuario_git)

    except FileNotFoundError:
        print(f"Error: El archivo {ruta_completa_archivo} no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer o analizar el archivo: {e}")


def realizar_analisis_semantico(nodo, contexto_actual=None):
    if isinstance(nodo, tuple):
        tipo_nodo = nodo[0]

        if tipo_nodo == 'asignacion':
            _, operador, var, valor = nodo
            linea = getattr(valor, 'lineno', 'desconocida')
            verificar_variable_declarada(var, linea)
            tabla_variables[var] = evaluar_expresion(valor)

        elif tipo_nodo == 'operacion_binaria':
            _, operador, izq, der = nodo
            linea = getattr(izq, 'lineno', 'desconocida')
            verificar_tipos_compatibles(izq, der, operador, linea)

        elif tipo_nodo == 'retornar':
            _, valor = nodo
            linea = getattr(valor, 'lineno', 'desconocida')
            verificar_tipo_retorno_funcion('numero', evaluar_expresion(valor), linea)

        for hijo in nodo[1:]:
            realizar_analisis_semantico(hijo, contexto_actual)


if __name__ == '__main__':
    analizar_archivo_ruby("algoritmo1_Paulette_Maldonado.rb", "Pauyamal")
    analizar_archivo_ruby("algoritmo2_Isaac_Criollo.rb", "Izaako04")
    analizar_archivo_ruby("algoritmo3_Joel_Guamani.rb", "isaiasgh")