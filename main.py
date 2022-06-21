import re

import ply.yacc as yacc
from ply import lex
from ply.lex import TOKEN

from tokens_out_processed import reserved_keywords, get_tokens

error_formatting = '\033[1;41m'

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
comparison_symbol = r'(' + t_EQ + t_EQ + r'|' + t_GT + r'|' + t_LT + r'|' + t_GT + t_EQ + \
                    r'|' + t_LT + t_EQ + '|' + t_EM + t_EQ + r')'
ID = r'[a-zA-Z_][a-zA-Z_0-9]*'
# TODO
concatenation_body = r'(' + ID + t_COM + 'r)*' + ID + r'|(0-9)* ' + t_OWB + ID + t_CWB + ')'

comment = t_SLASH + t_SLASH + r'.*'
size = r'\[(0-9)+:(0-9)+\]'
number = r'(-|\+)?[0-9]*`((b)([0-1])|(o)([0-7])*|(d)([0-9])*|(h)([0-9|a-f|A-F])*)'
integer = r'[0-9]+'


def t_error(t):
    print(f"{error_formatting}Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore = ' \t'

module_name = ""
start = 'module_declaration'


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


@TOKEN(integer)
def t_INTEGER(t):
    return t


# @TOKEN(size)
# def t_SIZE(t):
#     return t


def p_SIZE(p):
    '''SIZE : OSB INTEGER CLN INTEGER CSB
    '''
    return p


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
    '''condition : value comparison value
                  | value
       comparison : EQ EQ
                  | GT
                  | LT
                  | GT EQ
                  | LT EQ
                  | EM EQ
    '''
    p[0] = f'condition({p[1]}, {p[2]}, {p[3]})'
    return p


def p_value(p):
    '''value : value BIN_OPERATOR value
             | NOT value
             | NUMBER
             | ID
             | OB value CB
             | ternary_operator
    '''
    if len(p) == 3 and re.match(bin_operator, p[2]):
        p[0] = f'binary_operator({p[1]}, {p[2]}, {p[3]})'
    else:
        # TODO
        pass
    return p


@TOKEN(comparison_symbol)
def t_COMPARISON_SYMBOL(t):
    return t


def p_begin_synch_end(p):
    '''begin_synch_end : BEGIN synch_stmts END
    '''
    return p


def p_initial_stmt(p):
    '''initial_stmt : INITIAL synch_stmt
                    | INITIAL begin_synch_end
    '''
    return p


def p_synch_stmt(p):
    '''synch_stmt : content SCLN COMMENT
                  | content SCLN
       content : initial_stmt
               | reg_assign
               | ternary_operator
    '''
    return p


def p_synch_stmts(p):
    '''synch_stmts : synch_stmts synch_stmt
                   | synch_stmt
    '''
    return p


def p_wire_declaration(p):
    '''wire_declaration : WIRE ID
    '''
    p[0] = f'{module_name}.add_wire({p[2]}, Wire(1))'
    return p


# TODO
def p_wire_assign(p):
    '''wire_assign : ASSIGN ID EQ wire_assignable
       wire_assignable : ID
                       | value
    '''
    p[0] = f'{module_name}.assign({p[0]}, assignable)'
    return p


def p_reg_declaration(p):
    '''reg_declaration : REG ID
    '''

    x = f'{module_name}.add_register(ID, Register(1))'
    return p


def p_reg_assign(p):
    '''reg_assign : ID SYNCH_ASSIGN reg_assignable
       reg_assignable : ID
                      | value
    '''
    x = f'{module_name}.synchronous_block.add_procedure(synch_assign, (ID, assignable))'
    return p


def p_ternary_operator(p):
    '''ternary_operator : OB condition CB QM value CLN value
    '''
    p[0] = f'ternary_operator({p[2]}, {p[5]}, {p[7]})'
    return p


def p_declaration(p):
    '''declaration : wire_declaration
                   | reg_declaration

                   '''
    # TODO | local_param_declaration ?
    return p


# TODO
def p_body(p):
    '''body : body part
            | part
            | empty
       part : declaration
            | synch_part
            | asynch_part
            | COMMENT
    '''
    return p


def p_synch_part(p):
    '''synch_part : ALWAYS at_part synch_part_body
       synch_part_body : BEGIN synch_stmts END
                       | synch_stmt
       at_part : AT OB at_assignment ID CB
       at_assignment : posnegedge
                     | value
       posnegedge : POS EDGE
                  | NEG EDGE
    '''
    return p


def p_asynch_statement(p):
    '''asynch_statement : asynch_body SCLN COMMENT
                        | asynch_body SCLN
       asynch_body : wire_assign
                   | ternary_operator
    '''

    return p


def p_asynch_part(p):
    '''asynch_part : asynch_part asynch_statement
                   | asynch_statement
    '''
    return p


def p_module_declaration(p):
    '''module_declaration : MODULE ID body ENDMODULE
                          | MODULE ID ports_declaration body ENDMODULE
    '''
    global module_name
    module_name = p[2]
    return p


def p_ports_declaration(p):
    '''ports_declaration : OB inputs CB
       inputs : inputs COM input
              | input
       input : io SIZE ID
             | io ID
       io : INPUT
          | OUTPUT
          | INOUT
    '''
    return p


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    if p:
        print(f"{error_formatting}Syntax error at token {p.type}, line {p.lexer.lineno}")
        # Just discard the token and tell the parser it's okay.
        parser.restart()
    else:
        print(f"{error_formatting}Syntax error at EOF")


def p_assign(p):
    'assign : ID EQ ID BIN_OPERATOR value'
    return p


precedence = (

)

# dictionary of names
names = {}

if __name__ == '__main__':
    lexer = lex.lex()

    data = '''
module toplevel(input clock, input reset);

  // comment value

  reg flop1;
  reg flop2;

  always @ (posedge clock)
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
( input clk,
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
        print(tok)
        l_tok.append(tok)

    parser = yacc.yacc()
    parser.parse(data_2)
