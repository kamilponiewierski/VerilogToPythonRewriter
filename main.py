import ply.yacc as yacc
from ply import lex
from ply.lex import TOKEN

from tokens_out_processed import reserved_keywords, get_tokens

reserved = reserved_keywords()
tokens = list(get_tokens()) + list(reserved.values())
t_SEP = r'`'
t_HASH = r'\#'
t_SLASH = r'/'
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
ID = r'[a-zA-Z_][a-zA-Z_0-9]*'
# TODO
concatenation_body = r'(' + ID + t_COM + 'r)*' + ID + r'|(0-9)* ' + t_OWB + ID + t_CWB + ')'

comment = t_SLASH + t_SLASH + r'.*'
size = r'[(0-9)+:(0-9)+]'
number = r'(-|\+)?[0-9]*`((b)([0-1])|(o)([0-7])*|(d)([0-9])*|(h)([0-9|a-f|A-F])*)'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore = ' \t'


@TOKEN(bin_operator)
def t_BIN_OPERATOR(t):
    return t


@TOKEN(ID)
def t_ID(t):
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_CONCATENATION_BODY(t):
    r'(ID COM)* ID | (0-9)* OWB ID CWB'
    return t


@TOKEN(comment)
def t_COMMENT(t):
    return t


@TOKEN(size)
def t_SIZE(t):
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


# Parsing rules
def p_condition(p):
    '''expression : value comparison value
                  | value
       comparison : EQ EQ
                  | GT
                  | LT
                  | GT EQ
                  | LT EQ
                  | EM EQ
    '''
    return p


def p_expression_genvar_statement(p):
    'expression : GENVAR ID SCLN'
    return p


def p_term_concatenation(p):
    '''expression : OWB CONCATENATION_BODY CWB'''
    return p


def p_term_value(p):
    '''term : value BIN_OPERATOR value
                  | NOT value
                  | concatenation
                  | NUMBER
                  | ID
                  | OB value CB'''
    return p


def p_term_edge(p):
    '''sign : POS
            | NEG
       term : sign EDGE
    '''


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    if p:
        print("Syntax error at token", p.type)
        # Just discard the token and tell the parser it's okay.
        parser.restart()
    else:
        print("Syntax error at EOF")


def p_term_wire_declaration(p):
    '''expression : WIRE opt_size ID opt_size
       opt_size   : SIZE
                  | empty
    '''
    return p


def p_term_assign(p):
    'expression : ID EQ ID BIN_OPERATOR value'
    return p


precedence = ()

# dictionary of names
names = {}

if __name__ == '__main__':
    lexer = lex.lex()

    data = '''
module toplevel(clock,reset);
  input clock;
  input reset;
  // comment value

  reg flop1;
  reg flop2;

  always @ (posedge reset or posedge clock)
    if (reset)
      begin
        flop1 <= 0;
        flop2 <= 1;
      end
    else
      begin
        flop1 <= flop2;
        flop2 <= flop1;
      end
endmodule
     '''

    data_2 = '''
    module DELAY
// sample comment
(
    input clk,
    input ce,
    input [7:0] X,    
    output [7:0] Y
);
  
1`b0
reg [7:0] val = 0;
always @(posedge clk)
begin
    if (ce) val<=X;
    else val<=val;
end
assign Y=val;
endmodule
    '''

    # Give the lexer some input
    lexer.input(data_2)

    l_tok = []

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        # print(tok)
        l_tok.append(tok)

    parser = yacc.yacc()

    # while l_tok:
    #     try:
    #         s = l_tok.pop()  # Use raw_input on Python 2
    #     except EOFError:
    #         break
    #     parser.parse(s)
