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
metodos_definidos = {}
contexto_actual = []

# --- Reglas de Precedencia y Asociatividad ---
precedence = (
    ('right', 'IF', 'UNLESS', 'RESCUE'),
    ('right', 'ASIGNACION', 'MAS_ASIGNACION', 'MENOS_ASIGNACION', 'MULT_ASIGNACION', 'DIV_ASIGNACION', 'MOD_ASIGNACION'),
    ('left', 'INTERROGACION', 'DOS_PUNTOS'),  # Operador ternario
    ('left', 'OR_LOGICO', 'O_SIGNO', 'OR'),
    ('left', 'AND_LOGICO', 'Y_SIGNO', 'AND'),
    ('nonassoc', 'IGUAL', 'DIFERENTE', 'MAYOR_IGUAL', 'MENOR_IGUAL', 'MAYOR_QUE', 'MENOR_QUE', 'NAVE_ESPACIAL', 'TRIPLE_IGUAL'),
    ('left', 'APPEND'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'MULTIPLICACION', 'DIVISION', 'MODULO'),
    ('right', 'EXPONENCIACION'),
    ('right', 'UMINUS', 'NOT_LOGICO', 'EXCLAMACION_BAJO', 'NOT'),
    ('left', 'PUNTO'),
    ('left', 'CORCHETE_IZQ', 'CORCHETE_DER'),
    ('nonassoc', 'PARENTESIS_IZQ', 'PARENTESIS_DER'),
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
              | sentencia_require
              | sentencia_modificador
              | llamada_metodo_statement
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
            p[0] = p[1]
    else:
        p[0] = p[1]

def p_llamada_metodo_statement(p):
    '''
    llamada_metodo_statement : ID PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER
                             | ID argumentos_no_parentesis
    '''
    if len(p) == 5:
        p[0] = ('llamada_metodo', None, p[1], p[3])
    else:
        p[0] = ('llamada_metodo', None, p[1], p[2])

def p_argumentos_no_parentesis(p):
    '''
    argumentos_no_parentesis : argumento_no_parentesis
                             | argumentos_no_parentesis COMA argumento_no_parentesis
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_argumento_no_parentesis(p):
    '''
    argumento_no_parentesis : expresion_comparacion
    '''
    p[0] = p[1]

def p_sentencia_require(p):
    '''
    sentencia_require : REQUIRE CADENA
                      | REQUIRE CADENA_SIMPLE
    '''
    p[0] = ('require', p[2])

def p_vacio(p):
    '''vacio :'''
    pass

def p_sentencia_modificador(p):
    '''
    sentencia_modificador : expresion IF expresion
                          | expresion UNLESS expresion
    '''
    p[0] = ('modificador_if' if p[2] == 'if' else 'modificador_unless', p[1], p[3])

# --- EXPRESIONES ---

def p_expresion(p):
    '''
    expresion : expresion_rescue
    '''
    p[0] = p[1]

def p_expresion_rescue(p):
    '''
    expresion_rescue : expresion_ternaria
                     | expresion_ternaria RESCUE expresion_rescue
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('rescue_inline', p[1], p[3])

def p_expresion_ternaria(p):
    '''
    expresion_ternaria : expresion_logica
                       | expresion_logica INTERROGACION expresion_ternaria DOS_PUNTOS expresion_ternaria
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('ternario', p[1], p[3], p[5])

def p_expresion_logica(p):
    '''
    expresion_logica : expresion_comparacion
                     | expresion_logica AND_LOGICO expresion_comparacion
                     | expresion_logica OR_LOGICO expresion_comparacion
                     | expresion_logica Y_SIGNO expresion_comparacion
                     | expresion_logica O_SIGNO expresion_comparacion
                     | expresion_logica AND expresion_comparacion
                     | expresion_logica OR expresion_comparacion
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_expresion_comparacion(p):
    '''
    expresion_comparacion : expresion_aritmetica
                          | expresion_comparacion IGUAL expresion_aritmetica
                          | expresion_comparacion DIFERENTE expresion_aritmetica
                          | expresion_comparacion MAYOR_QUE expresion_aritmetica
                          | expresion_comparacion MENOR_QUE expresion_aritmetica
                          | expresion_comparacion MAYOR_IGUAL expresion_aritmetica
                          | expresion_comparacion MENOR_IGUAL expresion_aritmetica
                          | expresion_comparacion NAVE_ESPACIAL expresion_aritmetica
                          | expresion_comparacion TRIPLE_IGUAL expresion_aritmetica
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_expresion_aritmetica(p):
    '''
    expresion_aritmetica : expresion_termino
                         | expresion_aritmetica MAS expresion_termino
                         | expresion_aritmetica MENOS expresion_termino
                         | expresion_aritmetica APPEND expresion_termino
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_expresion_termino(p):
    '''
    expresion_termino : expresion_factor
                      | expresion_termino MULTIPLICACION expresion_factor
                      | expresion_termino DIVISION expresion_factor
                      | expresion_termino MODULO expresion_factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_expresion_factor(p):
    '''
    expresion_factor : expresion_unaria
                     | expresion_factor EXPONENCIACION expresion_unaria
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('operacion_binaria', p[2], p[1], p[3])

def p_expresion_unaria(p):
    '''
    expresion_unaria : expresion_postfix
                     | MENOS expresion_unaria %prec UMINUS
                     | NOT_LOGICO expresion_unaria
                     | EXCLAMACION_BAJO expresion_unaria
                     | NOT expresion_unaria
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif p[1] == '-':
        p[0] = ('unario_menos', p[2])
    else:
        p[0] = ('negacion', p[2])

def p_expresion_postfix(p):
    '''
    expresion_postfix : primario
                      | expresion_postfix PUNTO metodo_id
                      | expresion_postfix PUNTO metodo_id PARENTESIS_IZQ PARENTESIS_DER
                      | expresion_postfix PUNTO metodo_id PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER
                      | expresion_postfix PUNTO NEW
                      | expresion_postfix PUNTO NEW PARENTESIS_IZQ PARENTESIS_DER
                      | expresion_postfix PUNTO NEW PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER
                      | expresion_postfix CORCHETE_IZQ expresion CORCHETE_DER
                      | expresion_postfix bloque_o_do_end
                      | llamada_metodo_sin_receptor
                      | PUTS expresion
                      | PUTS PARENTESIS_IZQ expresion PARENTESIS_DER
                      | PRINT expresion
                      | PRINT PARENTESIS_IZQ expresion PARENTESIS_DER
                      | PRINTF expresion
                      | PRINTF PARENTESIS_IZQ expresion PARENTESIS_DER
                      | RAISE expresion
                      | RAISE
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        if p[1] in ['puts', 'print', 'printf']:
            p[0] = ('imprimir', p[1], p[2])
        elif p[1] == 'raise':
            p[0] = ('raise', p[2])
        else:
            p[0] = p[1]  # Para otros casos
    elif len(p) == 5 and p[1] in ['puts', 'print', 'printf']:
        p[0] = ('imprimir', p[1], p[3])
    elif p[2] == '.':
        if p[3] == 'new':
            if len(p) == 4:
                p[0] = ('llamada_metodo', p[1], 'new', [])
            elif len(p) == 6:
                p[0] = ('llamada_metodo', p[1], 'new', [])
            else:
                p[0] = ('llamada_metodo', p[1], 'new', p[5])
        else:
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

def p_llamada_metodo_sin_receptor(p):
    '''
    llamada_metodo_sin_receptor : metodo_id PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER
                                | metodo_id argumentos_metodo
                                | metodo_id
                                | ID_CLASE PARENTESIS_IZQ argumentos_metodo PARENTESIS_DER
    '''
    if len(p) == 2:
        p[0] = ('llamada_metodo', None, p[1], [])
    elif len(p) == 3:
        p[0] = ('llamada_metodo', None, p[1], p[2])
    elif p[2] == '(':
        p[0] = ('llamada_metodo', None, p[1], p[3])
    else:
        p[0] = ('llamada_metodo', None, p[1], p[2])

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
             | creacion_array
             | creacion_hash
             | SELF
             | ID_CLASE
             | GETS
    '''
    if p[1] == '(':
        p[0] = p[2]
    elif p[1] == 'gets':
        p[0] = ('llamada_metodo', None, 'gets', [])
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
    p[0] = ('literal', p[1])

# --- ASIGNACIONES ---

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
    '''
    p[0] = p[1]

# --- ESTRUCTURAS DE DATOS ---

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
                  | hash_key_symbol DOS_PUNTOS expresion
    '''
    if p[2] == ':':
        # Sintaxis nueva de Ruby: nombre: valor se convierte en :nombre => valor
        p[0] = ('par_hash', ':' + str(p[1]), p[3])
    else:
        p[0] = ('par_hash', p[1], p[3])

def p_hash_key_symbol(p):
    '''
    hash_key_symbol : ID
                    | SIMBOLO
    '''
    p[0] = p[1]

# --- ESTRUCTURAS DE CONTROL ---

def p_sentencia_condicional(p):
    '''
    sentencia_condicional : IF expresion optional_then sentencias END
                          | IF expresion optional_then sentencias ELSE sentencias END
                          | IF expresion optional_then sentencias clausulas_elsif END
                          | IF expresion optional_then sentencias clausulas_elsif ELSE sentencias END
                          | UNLESS expresion optional_then sentencias END
                          | UNLESS expresion optional_then sentencias ELSE sentencias END
                          | CASE expresion sentencias_when_case END
                          | CASE sentencias_when_case END
    '''
    if p[1] == 'case':
        if len(p) == 5:
            p[0] = ('case', None, p[2])
        else:
            p[0] = ('case', p[2], p[3])
    elif p[1] in ['if', 'unless']:
        if len(p) == 6:
            p[0] = ('condicional', p[1], p[2], p[4], None)
        elif len(p) == 8:
            p[0] = ('condicional', p[1], p[2], p[4], p[6])
        elif len(p) == 7:
            p[0] = ('condicional', p[1], p[2], p[4], p[5])
        else:
            p[0] = ('condicional', p[1], p[2], p[4], p[5], p[7])

def p_optional_then(p):
    '''optional_then : THEN
                     | vacio'''
    pass

def p_clausulas_elsif(p):
    '''
    clausulas_elsif : ELSIF expresion optional_then sentencias
                    | clausulas_elsif ELSIF expresion optional_then sentencias
    '''
    if len(p) == 5:
        p[0] = [('sino_si', p[2], p[4])]
    else:
        p[0] = p[1] + [('sino_si', p[3], p[5])]

def p_sentencias_when_case(p):
    '''
    sentencias_when_case : clausula_when
                         | sentencias_when_case clausula_when
                         | sentencias_when_case clausula_when ELSE sentencias
                         | clausulas_when ELSE sentencias
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif p[3] == 'else':
        p[0] = p[1] + [p[2], ('rama_sino', p[4])]
    else:
        p[0] = p[1] + [('rama_sino', p[3])]

def p_clausulas_when(p):
    '''
    clausulas_when : clausula_when
                   | clausulas_when clausula_when
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_clausula_when(p):
    '''
    clausula_when : WHEN lista_expresiones_when THEN sentencias
                  | WHEN lista_expresiones_when sentencias
    '''
    if len(p) == 5:
        p[0] = ('cuando', p[2], p[4])
    else:
        p[0] = ('cuando', p[2], p[3])

def p_lista_expresiones_when(p):
    '''
    lista_expresiones_when : expresion
                           | lista_expresiones_when COMA expresion
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# --- BUCLES ---

def p_sentencia_bucle(p):
    '''
    sentencia_bucle : WHILE expresion optional_do sentencias END
                    | UNTIL expresion optional_do sentencias END
                    | FOR ID IN expresion optional_do sentencias END
                    | LOOP bloque_o_do_end
                    | expresion_postfix PUNTO EACH bloque_o_do_end
    '''
    if p[1] == 'while':
        p[0] = ('bucle_mientras', p[2], p[4])
    elif p[1] == 'until':
        p[0] = ('bucle_hasta', p[2], p[4])
    elif p[1] == 'for':
        p[0] = ('bucle_for', p[2], p[4], p[6])
    elif p[1] == 'loop':
        p[0] = ('bucle_infinito', p[2])
    else:
        # Para entrada.each
        p[0] = ('llamada_metodo', p[1], 'each', [], p[4])

def p_optional_do(p):
    '''optional_do : DO
                   | vacio'''
    pass

def p_bloque_o_do_end(p):
    '''
    bloque_o_do_end : DO PIPE argumentos_bloque PIPE sentencias END
                    | DO sentencias END
                    | LLAVE_IZQ PIPE argumentos_bloque PIPE sentencias LLAVE_DER
                    | LLAVE_IZQ sentencias LLAVE_DER
    '''
    if p[1] == 'do':
        if len(p) == 7:
            p[0] = ('bloque', p[3], p[5])
        else:
            p[0] = ('bloque', [], p[2])
    else:
        if len(p) == 7:
            p[0] = ('bloque', p[3], p[5])
        else:
            p[0] = ('bloque', [], p[2])

def p_argumentos_bloque(p):
    '''
    argumentos_bloque : ID
                      | argumentos_bloque COMA ID
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# --- MÉTODOS Y CLASES ---

def p_definicion_metodo(p):
    '''
    definicion_metodo : DEF ID PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                      | DEF ID sentencias END
                      | DEF SELF PUNTO ID PARENTESIS_IZQ lista_parametros PARENTESIS_DER sentencias END
                      | DEF SELF PUNTO ID sentencias END
    '''
    if p[2] == 'self':
        if len(p) == 10:
            p[0] = ('def_self', p[4], p[6], p[8])
        else:
            p[0] = ('def_self', p[4], [], p[5])
    else:
        if len(p) == 8:
            p[0] = ('def', p[2], p[4], p[6])
        else:
            p[0] = ('def', p[2], [], p[3])

def p_lista_parametros(p):
    '''
    lista_parametros : parametro
                     | lista_parametros COMA parametro
                     | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    else:
        p[0] = p[1] + [p[3]] if len(p) > 2 else []

def p_parametro(p):
    '''
    parametro : ID
              | ID ASIGNACION expresion
              | MULTIPLICACION ID
    '''
    if len(p) == 2:
        p[0] = ('parametro', p[1])
    elif len(p) == 4:
        p[0] = ('parametro_default', p[1], p[3])
    else:
        p[0] = ('parametro_splat', p[2])

def p_argumentos_metodo(p):
    '''
    argumentos_metodo : argumento
                      | argumentos_metodo COMA argumento
                      | vacio
    '''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] is not None else []
    elif len(p) > 2:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []

def p_argumento(p):
    '''
    argumento : expresion
              | MULTIPLICACION expresion
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ('splat', p[2])

def p_definicion_clase(p):
    '''
    definicion_clase : CLASS ID cuerpo_clase END
                     | CLASS ID MENOR_QUE ID cuerpo_clase END
                     | MODULE ID cuerpo_clase END
    '''
    if p[1] == 'class':
        if len(p) == 5:
            p[0] = ('clase', p[2], None, p[3])
        else:
            p[0] = ('clase', p[2], p[4], p[5])
    else:
        p[0] = ('modulo', p[2], p[3])

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

# --- BEGIN-RESCUE-END ---

def p_sentencia_begin_rescue(p):
    '''
    sentencia_begin_rescue : BEGIN sentencias rescue_clauses END
                           | BEGIN sentencias rescue_clauses ensure_clause END
                           | BEGIN sentencias ensure_clause END
                           | BEGIN sentencias END
    '''
    if len(p) == 4:
        p[0] = ('begin', p[2], [], None)
    elif len(p) == 5:
        if isinstance(p[3], list) and p[3] and p[3][0][0] == 'rescue':
            p[0] = ('begin', p[2], p[3], None)
        else:
            p[0] = ('begin', p[2], [], p[3])
    else:
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
                  | RESCUE ASIGNA_HASH ID
                  | RESCUE ID_CLASE ASIGNA_HASH ID sentencias
                  | RESCUE ID_CLASE ASIGNA_HASH ID
                  | RESCUE ID_CLASE sentencias
                  | RESCUE ID_CLASE
                  | RESCUE ID sentencias
                  | RESCUE ID
                  | RESCUE sentencias
                  | RESCUE
    '''
    # Determinar qué elementos tenemos
    if len(p) == 2:
        # Solo RESCUE
        p[0] = ('rescue', None, None, [])
    elif len(p) == 3:
        if p[2] == '=>':
            # Error: rescue => sin variable
            p[0] = ('rescue', None, None, [])
        else:
            # RESCUE sentencias o RESCUE ID_CLASE/ID
            p[0] = ('rescue', None, None, p[2])
    elif len(p) == 4:
        if p[2] == '=>':
            # RESCUE => variable
            p[0] = ('rescue', None, p[3], [])
        else:
            # RESCUE tipo sentencias
            p[0] = ('rescue', p[2], None, p[3])
    elif len(p) == 5:
        if p[2] == '=>':
            # RESCUE => variable sentencias
            p[0] = ('rescue', None, p[3], p[4])
        else:
            # RESCUE tipo => variable
            p[0] = ('rescue', p[2], p[4], [])
    else:
        # RESCUE tipo => variable sentencias
        p[0] = ('rescue', p[2], p[4], p[5])

def p_ensure_clause(p):
    '''
    ensure_clause : ENSURE sentencias
    '''
    p[0] = ('ensure', p[2])

# --- MANEJO DE ERRORES ---

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
        
        # Intentar recuperarse del error
        parser.errok()
    else:
        error_msg = "Error de sintaxis en EOF (fin de archivo inesperado)."
        print(error_msg)
        errores_sintacticos.append(error_msg)

# --- Funciones auxiliares ---

def evaluar_expresion(nodo):
    """Evalúa un nodo del AST para obtener su valor concreto."""
    if not isinstance(nodo, tuple):
        return nodo
        
    tipo = nodo[0]
    
    if tipo == 'operacion_binaria':
        _, op, izq, der = nodo
        izq_val = evaluar_expresion(izq)
        der_val = evaluar_expresion(der)
        
        try:
            if op == '+': return izq_val + der_val
            if op == '-': return izq_val - der_val
            if op == '*': return izq_val * der_val
            if op == '/': return izq_val / der_val
            if op == '%': return izq_val % der_val
            if op == '**': return izq_val ** der_val
            if op == '==': return izq_val == der_val
            if op == '!=': return izq_val != der_val
            if op == '>': return izq_val > der_val
            if op == '<': return izq_val < der_val
            if op == '>=': return izq_val >= der_val
            if op == '<=': return izq_val <= der_val
        except:
            return None
            
    elif tipo == 'unario_menos':
        val = evaluar_expresion(nodo[1])
        return -val if val is not None else None
        
    elif tipo == 'negacion':
        val = evaluar_expresion(nodo[1])
        return not val if val is not None else None
        
    elif tipo == 'ternario':
        cond = evaluar_expresion(nodo[1])
        if cond:
            return evaluar_expresion(nodo[2])
        else:
            return evaluar_expresion(nodo[3])
            
    return None

# --- Análisis Semántico ---

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

def verificar_metodo_definido(nombre_metodo, linea):
    if nombre_metodo not in metodos_definidos:
        error = f"Error semántico (línea {linea}): Método '{nombre_metodo}' no definido."
        errores_semanticos.append(error)
        return False
    return True

def generar_log_semantico(usuario_git):
    """Genera un archivo de log con errores semánticos."""
    if not errores_semanticos:
        print("No se encontraron errores semánticos.")
        return

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

def realizar_analisis_semantico(nodo, contexto='global'):
    """Realiza análisis semántico del AST."""
    if nodo is None:
        return
        
    if isinstance(nodo, list):
        for item in nodo:
            realizar_analisis_semantico(item, contexto)
        return
        
    if not isinstance(nodo, tuple):
        return
        
    tipo_nodo = nodo[0]
    
    if tipo_nodo == 'asignacion':
        _, operador, var, valor = nodo
        tabla_variables[var] = {'tipo': 'variable', 'valor': valor, 'contexto': contexto}
        realizar_analisis_semantico(valor, contexto)
        
    elif tipo_nodo == 'def':
        _, nombre, params, cuerpo = nodo
        metodos_definidos[nombre] = {'params': params, 'cuerpo': cuerpo}
        realizar_analisis_semantico(cuerpo, f'metodo_{nombre}')
        
    elif tipo_nodo == 'clase':
        _, nombre, padre, cuerpo = nodo
        realizar_analisis_semantico(cuerpo, f'clase_{nombre}')
        
    elif tipo_nodo == 'llamada_metodo':
        # Puede tener 4 o 5 elementos (con bloque opcional)
        if len(nodo) == 4:
            _, receptor, metodo, args = nodo
            bloque = None
        else:
            _, receptor, metodo, args, bloque = nodo
            
        # Solo verificar si el método es local (no tiene receptor)
        if receptor is None and metodo not in ['puts', 'print', 'printf', 'gets', 'require', 'split', 'each', 'new']:
            verificar_metodo_definido(metodo, 0)
            
        realizar_analisis_semantico(receptor, contexto)
        for arg in args:
            realizar_analisis_semantico(arg, contexto)
        if bloque:
            realizar_analisis_semantico(bloque, contexto)
            
    elif tipo_nodo == 'operacion_binaria':
        _, op, izq, der = nodo
        realizar_analisis_semantico(izq, contexto)
        realizar_analisis_semantico(der, contexto)
        
    elif tipo_nodo in ['bucle_mientras', 'bucle_hasta', 'bucle_for', 'bucle_infinito']:
        for parte in nodo[1:]:
            realizar_analisis_semantico(parte, 'bucle')
            
    elif tipo_nodo == 'condicional':
        for parte in nodo[1:]:
            realizar_analisis_semantico(parte, contexto)
            
    elif tipo_nodo == 'bloque':
        _, params, cuerpo = nodo
        # Los parámetros del bloque se agregan al contexto local
        for param in params:
            tabla_variables[param] = {'tipo': 'parametro_bloque', 'contexto': contexto}
        realizar_analisis_semantico(cuerpo, contexto)
        
    elif tipo_nodo == 'modificador_if' or tipo_nodo == 'modificador_unless':
        _, sentencia, condicion = nodo
        realizar_analisis_semantico(sentencia, contexto)
        realizar_analisis_semantico(condicion, contexto)
        
    elif tipo_nodo == 'ternario':
        _, condicion, si_verdadero, si_falso = nodo
        realizar_analisis_semantico(condicion, contexto)
        realizar_analisis_semantico(si_verdadero, contexto)
        realizar_analisis_semantico(si_falso, contexto)
        
    elif tipo_nodo == 'imprimir':
        _, metodo, expresion = nodo
        realizar_analisis_semantico(expresion, contexto)
        
    elif tipo_nodo in ['romper', 'siguiente']:
        verificar_estructuras_control(tipo_nodo.replace('romper', 'break').replace('siguiente', 'next'), contexto, 0)
        if len(nodo) > 1 and nodo[1]:
            realizar_analisis_semantico(nodo[1], contexto)
            
    elif tipo_nodo == 'require':
        pass  # No necesita análisis semántico adicional
        
    elif tipo_nodo == 'expresion_con_bloque':
        _, expresion, bloque = nodo
        realizar_analisis_semantico(expresion, contexto)
        realizar_analisis_semantico(bloque, contexto)
        
    else:
        # Para otros tipos de nodos, analizar recursivamente sus hijos
        for hijo in nodo[1:]:
            if isinstance(hijo, (list, tuple)):
                realizar_analisis_semantico(hijo, contexto)

# --- Construcción del Parser ---

parser = yacc.yacc(debug=True)

def analizar_archivo_ruby(nombre_archivo, usuario_git):
    """Analiza sintáctica y semánticamente un archivo Ruby."""
    os.makedirs(ruta_carpeta_logs, exist_ok=True)
    ruta_completa_archivo = os.path.join(ruta_archivos_ruby, nombre_archivo)

    global errores_sintacticos, errores_semanticos
    errores_sintacticos = []
    errores_semanticos = []
    tabla_variables.clear()
    metodos_definidos.clear()

    try:
        with open(ruta_completa_archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
            
        print(f"\n--- Analizando: {nombre_archivo} (Usuario: {usuario_git}) ---")
        
        # Reiniciar lexer
        lexer.lineno = 1
        
        # Análisis sintáctico
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
                archivo_log.write("\n--- Árbol de Sintaxis Abstracta (AST) ---\n")
                import json
                
                def serializar_ast(nodo):
                    """Convierte el AST a un formato serializable en JSON."""
                    if isinstance(nodo, (str, int, float, bool, type(None))):
                        return nodo
                    elif isinstance(nodo, list):
                        return [serializar_ast(item) for item in nodo]
                    elif isinstance(nodo, tuple):
                        return [serializar_ast(item) for item in nodo]
                    else:
                        return str(nodo)
                
                ast_serializable = serializar_ast(arbol_sintactico)
                archivo_log.write(json.dumps(ast_serializable, indent=2, ensure_ascii=False))
                print(f"Análisis sintáctico exitoso. Log en: {ruta_archivo_log_sintactico}")

            realizar_analisis_semantico(arbol_sintactico)
            generar_log_semantico(usuario_git)

    except FileNotFoundError:
        print(f"Error: El archivo {ruta_completa_archivo} no fue encontrado.")
    except Exception as e:
        print(f"Ocurrió un error inesperado al leer o analizar el archivo: {e}")
        import traceback
        traceback.print_exc()

# --- Main ---

if __name__ == '__main__':
    # Pruebas
    analizar_archivo_ruby("algoritmo1_Paulette_Maldonado.rb", "Pauyamal")
    analizar_archivo_ruby("algoritmo2_Isaac_Criollo.rb", "Izaako04")
    analizar_archivo_ruby("algoritmo3_Joel_Guamani.rb", "isaiasgh")