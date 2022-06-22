from ply.lex import TOKEN, lex

error_formatting = '\033[1;41m'

t_ignore = ' \t'

t_SEP = r'`'
t_HASH = r'\#'
t_SLASH = r'\/'
t_DOT = r'\.'
t_COM = r','
t_AND = r'&'
t_AT = r'@'
t_DOL = r'\$'
t_EM = r'!'
t_QM = r'\?'
t_NOT = r'~'
t_OR = r'\|'
t_OSB = r'\['
t_CSB = r'\]'
t_OB = r'\('
t_CB = r'\)'
t_OWB = r'\{'
t_CWB = r'\}'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_CLN = r':'
t_SCLN = r';'
t_EQ = r'='
t_LT = r'<'
t_GT = r'>'
synch_assign = r'(' + t_LT + t_EQ + r')'
bin_operator = r'(' + t_OR + r'|' + t_AND + r'|' + t_PLUS + r'|' + t_MINUS + r'|' + t_TIMES + r')'
comparison_symbol = r'(' + t_EQ + t_EQ + r'|' + t_GT + r'|' + t_LT + r'|' + t_GT + t_EQ + \
                    r'|' + t_LT + t_EQ + '|' + t_EM + t_EQ + r')'
ID = r'[a-zA-Z_][a-zA-Z_0-9]*'
# TODO
concatenation_body = r'(' + ID + t_COM + 'r)*' + ID + r'|(0-9)* ' + t_OWB + ID + t_CWB + ')'

comment = t_SLASH + t_SLASH + r'.*'
size = r'\[(0-9)+:(0-9)+\]'
number = r'(-|\+)?[0-9]*`((b)([0-1])|(o)([0-7])*|(d)([0-9])*|(h)([0-9|a-f|A-F])*)'
integer = r'[0-9]+'


def reserved_keywords():
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'elsif': 'ELSIF',
        'case': 'CASE',
        'endcase': 'ENDCASE',
        'begin': 'BEGIN',
        'end': 'END',
        'module': 'MODULE',
        'endmodule': 'ENDMODULE',
        'param': 'PARAM',
        'localparam': 'LOCALPARAM',
        'always': 'ALWAYS',
        'assign': 'ASSIGN',
        'for': 'FOR',
        'while': 'WHILE',
        'input': 'INPUT',
        'output': 'OUTPUT',
        'inout': 'INOUT',
        'pos': 'POS',
        'neg': 'NEG',
        'edge': 'EDGE',
        'signed': 'SIGNED',
        'reg': 'REG',
        'wire': 'WIRE',
    }
    return reserved


def get_tokens():
    tokens = (
        'SEP',
        'HASH',
        'SLASH',
        'DOT',
        'COM',
        'AND',
        'AT',
        'DOL',
        'EM',
        'QM',
        'NOT',
        'OR',
        'OSB',
        'CSB',
        'OB',
        'CB',
        'OWB',
        'CWB',
        'PLUS',
        'MINUS',
        'TIMES',
        'CLN',
        'SCLN',
        'EQ',
        'LT',
        'GT',
        # non literals
        'COMMENT',
        'ID',
        'NUMBER',
        'BIN_OPERATOR',
        'CONCATENATION_BODY',
        'SYNCH_ASSIGN',
        'COMPARISON_SYMBOL',
        'INTEGER',
    )
    return tokens


def t_error(t):
    print(f"{error_formatting}Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


@TOKEN(ID)
def t_ID(t):
    t.type = reserved_keywords().get(t.value, 'ID')  # Check for reserved words
    return t


def t_CONCATENATION_BODY(t):
    r'(ID COM)* ID | (0-9)* OWB ID CWB'
    return t


@TOKEN(comment)
def t_COMMENT(t):
    pass


@TOKEN(integer)
def t_INTEGER(t):
    return t


@TOKEN(bin_operator)
def t_BIN_OPERATOR(t):
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


@TOKEN(number)
def t_NUMBER(t):
    return t


@TOKEN(synch_assign)
def t_SYNCH_ASSIGN(t):
    return t


@TOKEN(comparison_symbol)
def t_COMPARISON_SYMBOL(t):
    return t


tokens = list(get_tokens()) + list(reserved_keywords().values())
lexer = lex()
