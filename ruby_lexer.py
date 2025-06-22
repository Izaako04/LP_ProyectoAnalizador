import os
import ply.lex as lex
import datetime

ruta_carpeta = "logs"
ruta_algoritmos = "algoritmos"
noReconocidos = []

reserved = {
    # Aporte Isaac Criollo
    "if": "IF", "else": "ELSE", "elsif": "ELSIF", "end": "END",
    "def": "DEF", "class": "CLASS", "module": "MODULE", "while": "WHILE",
    "until": "UNTIL", "for": "FOR", "do": "DO", "begin": "BEGIN",
    "rescue": "RESCUE", "ensure": "ENSURE", "retry": "RETRY",
    "break": "BREAK", "next": "NEXT", "redo": "REDO", "return": "RETURN",
    "when": "WHEN",

    # Aporte Joel Guamani
    "yield": "YIELD", "super": "SUPER", "self": "SELF", "nil": "NIL",
    "and": "AND", "or": "OR", "not": "NOT", "alias": "ALIAS",
    "defined": "DEFINED", "undef": "UNDEF", "case": "CASE", "then": "THEN",
    "in": "IN", "unless": "UNLESS", "puts": "PUTS",

    # Aporte Paulette Maldonado
    "gets": "GETS", "chomp": "CHOMP", "each": "EACH", "require": "REQUIRE",
    "loop": "LOOP", "new": "NEW", "initialize": "INITIALIZE",
    "to_i": "TO_I", "to_f": "TO_F", "to_s": "TO_S", "include": "INCLUDE",
    "empty": "EMPTY", "match": "MATCH", "split": "SPLIT", "add": "ADD",
    "size": "SIZE", "max": "MAX", "min": "MIN", "sum": "SUM",
    "print": "PRINT", "printf": "PRINTF", "concat": "CONCAT",
    "sort": "SORT", "to_set": "TO_SET",

    # Aporte (común o previo, reclasificado para coherencia)
    "true": "TRUE",
    "false": "FALSE",
}

tokens = [
    # Aporte Isaac Criollo
    'Y_SIGNO', 'O_SIGNO', 'TRIPLE_IGUAL', 'IGUAL_DOBLEP', 'ASIGNA_HASH', 'PREGUNTA',
    'EXCLAMACION_BAJO', 'EXCLAMACION_ALTO', 'PORCENTAJE', 'BARRA',
    'RANGO_EXCLUSIVO', 'RANGO_INCLUSIVO', 'EXPONENCIACION',
    'MAS_ASIGNACION', 'MENOS_ASIGNACION', 'MULT_ASIGNACION',
    'DIV_ASIGNACION', 'MOD_ASIGNACION', 'IGUAL', 'DIFERENTE',
    'MAYOR_IGUAL', 'MENOR_IGUAL', 'NAVE_ESPACIAL', 'AND_LOGICO', 'OR_LOGICO',
    'FLOTANTE', 'ENTERO',
    'COMENTARIO_LINEA', 'COMENTARIO_BLOQUE', # Reubicados para claridad

    # Aporte Joel Guamani
    'REGEX',
    'CADENA_INTERPOLADA', # <--- ¡AHORA SÍ, ESTÁ AQUÍ!
    'CADENA',
    'CADENA_SIMPLE', 'SIMBOLO',
    'ID_GLOBAL', 'ID_INSTANCIA', 'ID_CLASE',
    'VARIABLECLASE', # <--- ¡Y ESTE TAMBIÉN!
    'METODO_PREGUNTA', 'METODO_EXCLAMACION', # Nuevo, para ! al final
    'ID',

    # Aporte Paulette Maldonado
    'MAS', 'MENOS', 'MULTIPLICACION', 'DIVISION', 'MODULO', 'ASIGNACION',
    'MAYOR_QUE', 'MENOR_QUE', 'NOT_LOGICO',
    'PARENTESIS_IZQ', 'PARENTESIS_DER', 'LLAVE_IZQ', 'LLAVE_DER',
    'CORCHETE_IZQ', 'CORCHETE_DER', 'COMA', 'PUNTO', 'DOS_PUNTOS',
    'TRES_PUNTOS', # Definido explícitamente ahora
    'PUNTO_COMA', 'INTERROGACION', 'CIRCUMFLEJO', 'PIPE', 'BACKSLASH', 'DOLAR',
] + list(reserved.values())

# ---------------------------------------------------------------------
# REGLAS DE EXPRESIONES REGULARES PARA LOS TOKENS
# ---------------------------------------------------------------------

# Aporte Comun (Comentarios - orden de especificidad)
def t_COMENTARIO_BLOQUE(t):
    r'=begin.*?=end'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_COMENTARIO_LINEA(t):
    r'\#.*'
    pass

# Aporte Joel Guamani (Cadenas - esta función manejará CADENA y CADENA_INTERPOLADA)
def t_CADENA(t):
    r'\"(?:[^"\\]|\\.)*\"' # Cualquier carácter que no sea " o \, o una secuencia de escape
    
    if '#{' in t.value:
        t.type = 'CADENA_INTERPOLADA'
    else:
        t.type = 'CADENA'
    t.value = t.value[1:-1] # Elimina las comillas
    return t

def t_CADENA_SIMPLE(t): # Esta se mantiene igual.
    r'\'(?:[^\'\\]|\\.)*\''
    t.value = t.value[1:-1]
    return t

def t_REGEX(t):
    r'/(?:[^/\\]|\\.)+/[gimoux]*'
    return t

def t_SIMBOLO(t):
    r':[a-zA-Z_]\w*|\"[^"]*\"|\'[^\']*\''
    return t

# Aporte Joel Guamani / Isaac Criollo (Identificadores y Palabras Reservadas - orden de especificidad)
def t_VARIABLECLASE(t): # Aporte Isaac Criollo / Joel Guamani
    r'@@[a-zA-Z_]\w*'
    return t

def t_ID_INSTANCIA(t): # Aporte Joel Guamani
    r'@[a-zA-Z_]\w*'
    return t

def t_ID_GLOBAL(t): # Aporte Joel Guamani
    r'\$[a-zA-Z_]\w*'
    return t

def t_METODO_EXCLAMACION(t): # Aporte (común)
    r'[a-zA-Z_]\w*!'
    return t

def t_METODO_PREGUNTA(t): # Aporte Joel Guamani
    r'[a-zA-Z_]\w*\?'
    return t

def t_ID_CLASE(t): # Aporte Joel Guamani
    r'[A-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID_CLASE')
    return t

def t_ID(t): # Aporte Joel Guamani
    r'[a-zA-Z_]\w*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Aporte Isaac Criollo (Números - flotantes antes que enteros)
def t_FLOTANTE(t):
    r'-?\d+\.\d+'
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'-?\d+'
    t.value = int(t.value)
    return t

# Aporte Isaac Criollo (Operadores complejos - más largos antes que más cortos)
t_RANGO_EXCLUSIVO = r'\.\.\.'
t_RANGO_INCLUSIVO = r'\.\.'
t_EXPONENCIACION = r'\*\*'
t_MAS_ASIGNACION = r'\+='
t_MENOS_ASIGNACION = r'-='
t_MULT_ASIGNACION = r'\*='
t_DIV_ASIGNACION = r'/='
t_MOD_ASIGNACION = r'%='
t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MAYOR_IGUAL = r'>='
t_MENOR_IGUAL = r'<='
t_NAVE_ESPACIAL = r'<=>'
t_AND_LOGICO = r'&&'
t_OR_LOGICO = r'\|\|'
t_TRIPLE_IGUAL = r'==='
t_ASIGNA_HASH = r'=>'

# Aporte Paulette Maldonado (Operadores simples y delimitadores)
t_MAS = r'\+'
t_MENOS = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'
t_MODULO = r'%'
t_ASIGNACION = r'='
t_MAYOR_QUE = r'>'
t_MENOR_QUE = r'<'
t_NOT_LOGICO = r'!'
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'
t_LLAVE_IZQ = r'\{'
t_LLAVE_DER = r'\}'
t_CORCHETE_IZQ = r'\['
t_CORCHETE_DER = r'\]'
t_COMA = r','
t_PUNTO = r'\.'
t_DOS_PUNTOS = r':'
t_TRES_PUNTOS = r'\.{3}' # Aporte Paulette Maldonado (definición explícita)
t_PUNTO_COMA = r';'
t_INTERROGACION = r'\?'
t_CIRCUMFLEJO = r'\^'
t_PIPE = r'\|'
t_BACKSLASH = r'\\'
t_DOLAR = r'\$'

# Aporte Comun
t_ignore = ' \t'

def t_nuevalinea(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    error_msg = f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}"
    print(error_msg)
    noReconocidos.append(error_msg)
    t.lexer.skip(1)

# Aporte Comun
lexer = lex.lex()

def analizar_y_loguear(lexer_instance, archivo_ruby, prefijo_log):
    """Analiza un archivo Ruby y guarda los tokens en un log"""
    os.makedirs(ruta_carpeta, exist_ok=True)
    ruta_completa = os.path.join(ruta_algoritmos, archivo_ruby)
    try:
        with open(ruta_completa, 'r', encoding='utf-8') as f:
            codigo_ruby = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {ruta_completa}")
        return
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    global noReconocidos
    noReconocidos = []

    lexer_instance.input(codigo_ruby)

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    nombre_log = f"{prefijo_log}-{timestamp}.txt"
    ruta_log = os.path.join(ruta_carpeta, nombre_log)

    with open(ruta_log, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Análisis léxico de: {archivo_ruby}\n")
        log_file.write(f"Fecha y Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write("="*50 + "\n")

        for tok in lexer_instance:
            valor = tok.value if isinstance(tok.value, str) else str(tok.value)
            log_file.write(f"Línea {tok.lineno}: {tok.type:<20} {valor}\n")

        if noReconocidos:
            log_file.write("\nErrores de caracteres no reconocidos:\n")
            log_file.write("\n".join(noReconocidos))
        else:
            log_file.write("\nNo se encontraron caracteres no reconocidos.\n")

    print(f"Análisis léxico completado. Resultados en: {ruta_log}")


def pruebas_Isaac():
    lexer = lex.lex()
    analizar_y_loguear(lexer, "algoritmo2_Isaac_Criollo.rb", "lexico-IsaacCriollo")

def pruebas_Joel():
    lexer = lex.lex()
    analizar_y_loguear(lexer, "algoritmo3_Joel_Guamani.rb", "lexico-Joel_Guamani")

def pruebas_Paulette():
    lexer = lex.lex()
    analizar_y_loguear(lexer, "algoritmo1_Paulette_Maldonado.rb", "lexico-PauletteMaldonado")


if __name__ == "__main__":
    pruebas_Isaac()
    pruebas_Joel()
    pruebas_Paulette()