import ply.yacc as yacc
from ply import lex

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
t_CLN = r':'
t_SCLN = r';'
t_EQ = r'='
t_LT = r'<'
t_GT = r'>'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore = ' \t'


def t_VALUE(t):
    r'Value Bin_operator Value|NOT Value| Concatenation| Number| Identifier|OB Value CB|Interpreted'
    return t


def t_COMMENT(t):
    r'//.*'

    return t


def t_SIZE(t):
    r'[(0-9)+:(0-9)+]'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_NUM(t):
    r'(MINUS|PLUS)?[0-9]*SEP((b)(0-1)*|(o)(0-7)*|(d)(0-9)*|(h)(0-9|a-f|A-F))'
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


# Parsing rules


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
(
    input clk,
    input ce,
    input [7:0] X,    
    output [7:0] Y
);
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

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        print(tok)
