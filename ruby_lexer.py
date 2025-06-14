
import os 
import ply.lex as lex

import datetime
ruta_carpeta="logs"
ruta_algoritmos="algoritmos"
noReconocidos=[]

reserved = {

    #Aporte Isaac Criollo
    "if": "IF",
    "else": "ELSE",
    "elsif": "ELSIF",
    "end": "END",
    "def": "DEF",
    "class": "CLASS",
    "module": "MODULE",
    "while": "WHILE",
    "until": "UNTIL",
    "for": "FOR",
    "do": "DO",
    "begin": "BEGIN",
    "rescue": "RESCUE",
    "ensure": "ENSURE",
    "retry": "RETRY",
    "break": "BREAK",
    "next": "NEXT",
    "redo": "REDO",
    "return": "RETURN",

    #Aporte Joel Guamani
    "yield": "YIELD",
    "super": "SUPER",
    "self": "SELF",
    "nil": "NIL",
    "true": "TRUE",
    "false": "FALSE",
    "and": "AND",
    "or": "OR",
    "not": "NOT",
    "alias": "ALIAS",
    "defined": "DEFINED",
    "undef": "UNDEF",
    "case": "CASE",
    "when": "WHEN",
    "then": "THEN",
    "in": "IN",
    "unless": "UNLESS", 
    "puts": "PUTS",

    #Aporte Paulette Maldonado
    "gets": "GETS",
    "chomp": "CHOMP",
    "each": "EACH",
    "require": "REQUIRE",
    "loop": "LOOP",
    "new": "NEW",
    "initialize": "INITIALIZE",
    "to_i": "TO_I",
    "to_f": "TO_F",
    "to_s": "TO_S",
    "include": "INCLUDE",
    "empty": "EMPTY",
    "match": "MATCH",
    "split": "SPLIT",
    "add": "ADD",
    "size": "SIZE",
    "max": "MAX",
    "min": "MIN",
    "sum": "SUM"
}

tokens = [
    #Aporte Isaac Criollo
    'RANGO_EXCLUSIVO',      # ...
    'RANGO_INCLUSIVO',      # ..
    'EXPONENCIACION',       # **
    'MAS_ASIGNACION',       # +=
    'MENOS_ASIGNACION',     # -=
    'MULT_ASIGNACION',      # *=
    'DIV_ASIGNACION',       # /=
    'MOD_ASIGNACION',       # %=
    'IGUAL',                # ==
    'DIFERENTE',            # !=
    'MAYOR_IGUAL',          # >=
    'MENOR_IGUAL',          # <=
    'NAVE_ESPACIAL',        # <=>
    'AND_LOGICO',           # &&
    'OR_LOGICO',            # ||
    'ASIGNACION_HASH',      # =>
    'FLOTANTE',             # Números decimales
    'ENTERO',               # Números enteros

    #Aporte Joel Guamani
    'REGEX',                # Expresiones regulares /pattern/
    'CADENA_INTERPOLADA',   # Cadenas con interpolación #{...}
    'CADENA',               # Cadenas entre comillas
    'CADENA_SIMPLE',        # Cadenas entre comillas simples
    'SIMBOLO',              # Símbolos :symbol
    'ID_GLOBAL',            # Variables globales $var
    'ID_INSTANCIA',         # Variables de instancia @var
    'ID_CLASE',             # Variables de clase @@var
    'METODO_PREGUNTA',      # match?, empty?, include?, etc.
    'MATCH_QUERY',          # match?
    'EMPTY_QUERY',          # empty?
    'INCLUDE_QUERY',        # include?
    'DEFINED_QUERY',        # defined?
    'ID',                   # Identificadores normales
    'COMENTARIO_LINEA',     # # comentario
    'COMENTARIO_BLOQUE',    # =begin ... =end

    #Aporte Paulette Maldonado
    'MAS',                  # +
    'MENOS',                # -
    'MULTIPLICACION',       # *
    'DIVISION',             # /
    'MODULO',               # %
    'ASIGNACION',           # =
    'MAYOR_QUE',            # >
    'MENOR_QUE',            # <
    'NOT_LOGICO',           # !
    'PARENTESIS_IZQ',       # (
    'PARENTESIS_DER',       # )
    'LLAVE_IZQ',            # {
    'LLAVE_DER',            # }
    'CORCHETE_IZQ',         # [
    'CORCHETE_DER',         # ]
    'COMA',                 # ,
    'PUNTO',                # .
    'DOS_PUNTOS',           # :
    'PUNTO_COMA',           # ;
    'INTERROGACION',        # ?
    'CIRCUMFLEJO',          # ^
    'PIPE',                 # |
    'BACKSLASH',            # \
    'DOLAR',                # $
] + list(reserved.values())

#Aporte Isaac Criollo
def t_RANGO_EXCLUSIVO(t):
    r'\.\.\.'
    return t

def t_RANGO_INCLUSIVO(t):
    r'\.\.'
    return t

def t_EXPONENCIACION(t):
    r'\*\*'
    return t

def t_MAS_ASIGNACION(t):
    r'\+='
    return t

def t_MENOS_ASIGNACION(t):
    r'-='
    return t

def t_MULT_ASIGNACION(t):
    r'\*='
    return t

def t_DIV_ASIGNACION(t):
    r'/='
    return t

def t_MOD_ASIGNACION(t):
    r'%='
    return t

def t_IGUAL(t):
    r'=='
    return t

def t_DIFERENTE(t):
    r'!='
    return t

def t_MAYOR_IGUAL(t):
    r'>='
    return t

def t_MENOR_IGUAL(t):
    r'<='
    return t

def t_NAVE_ESPACIAL(t):
    r'<=>'
    return t

def t_AND_LOGICO(t):
    r'&&'
    return t

def t_OR_LOGICO(t):
    r'\|\|'
    return t

def t_ASIGNACION_HASH(t):
    r'=>'
    return t

def t_FLOTANTE(t):
    r'-?\d+\.\d+'
    t.value = float(t.value)
    return t

def t_ENTERO(t):
    r'-?\d+'
    t.value = int(t.value)
    return t


#Aporte Joel Guamani 

def t_REGEX(t):
    r'/(?:[^/\\]|\\.)+/[gimoux]*'
    return t

def t_CADENA_INTERPOLADA(t):
    r'\"(?:[^\"\\]|\\.)*\"'

    if '#{' in t.value:
        t.type = 'CADENA_INTERPOLADA'
    else:
        t.type = 'CADENA'
    t.value = t.value[1:-1]
    return t

def t_CADENA_SIMPLE(t):
    r'\'(?:[^\'\\]|\\.)*\''
    t.value = t.value[1:-1]
    return t

def t_SIMBOLO(t):
    r':[a-zA-Z_]\w*'
    return t

def t_ID_GLOBAL(t):
    r'\$[a-zA-Z_]\w*'
    return t

def t_ID_INSTANCIA(t):
    r'@[a-zA-Z_]\w*'
    return t

def t_ID_CLASE(t):
    r'@@[a-zA-Z_]\w*'
    return t

def t_METODO_PREGUNTA(t):
    r'[a-zA-Z_]\w*\?'
    
    base_name = t.value[:-1]
    
    if base_name == 'match':
        t.type = 'MATCH_QUERY'
    elif base_name == 'empty':
        t.type = 'EMPTY_QUERY'
    elif base_name == 'include':
        t.type = 'INCLUDE_QUERY'
    elif base_name == 'defined':
        t.type = 'DEFINED_QUERY'
    else:
        t.type = 'METODO_PREGUNTA'
    return t

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved.get(t.value, 'ID')  
    return t

def t_COMENTARIO_LINEA(t):
    r'\#.*'
    pass

def t_COMENTARIO_BLOQUE(t):
    r'=begin[\s\S]*?=end'
    pass


#Aporte Paulette Maldonado
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
t_PUNTO_COMA = r';'
t_INTERROGACION = r'\?'
t_CIRCUMFLEJO = r'\^'
t_PIPE = r'\|'
t_BACKSLASH = r'\\'
t_DOLAR = r'\$'
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
    noReconocidos.append(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)


#Aporte Comun
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
        log_file.write("="*50 + "\n")
        
        for tok in lexer_instance:
            valor = tok.value if isinstance(tok.value, str) else str(tok.value)
            log_file.write(f"Línea {tok.lineno}: {tok.type:<20} {valor}\n")
        
        if noReconocidos:
            log_file.write("\nErrores:\n")
            log_file.write("\n".join(noReconocidos))
    
    print(f"Análisis completado. Resultados en: {ruta_log}")


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