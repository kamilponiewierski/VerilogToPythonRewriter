import os
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


def t_error(t):
    print(f"{error_formatting}Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore = ' \t'

module_name = ""
out_file = None
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
    pass


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
       comparison : COMPARISON_SYMBOL
    '''
    if len(p) == 4:
        p[0] = f'condition({p[1]}, "{p[2]}", {p[3]})'
    else:
        p[0] = p[1]
    return p


def p_value(p):
    '''value : value BIN_OPERATOR value
             | NOT value
             | NUMBER
             | ID
             | OB value CB
             | ternary_operator
             | INTEGER
    '''
    if len(p) == 4 and re.match(bin_operator, p[2]):
        p[0] = f'binary_operator({p[1]}, "{p[2]}", {p[3]})'
    elif p.slice[1].type == 'ID':
        p[0] = f'"{p[1]}"'
    else:
        p[0] = p[1]
    return p


@TOKEN(comparison_symbol)
def t_COMPARISON_SYMBOL(t):
    return t


def p_synch_stmt(p):
    '''synch_stmt : content SCLN
       content : reg_assign
               | ternary_operator
    '''
    p[0] = p[1]
    return p


def p_synch_stmts(p):
    '''synch_stmts : synch_stmts synch_stmt
                   | synch_stmt
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 3:
        p[0] = [*p[1], p[2]]
    return p


def p_wire_declaration(p):
    '''wire_declaration : WIRE ID SCLN
    '''
    p[0] = f'{module_name}.add_wire("{p[2]}", Wire(1))\n'
    out_file.write(p[0])
    return p


# TODO
def p_wire_assign(p):
    '''wire_assign : ASSIGN ID EQ wire_assignable
    '''
    p[0] = f'{module_name}.assign("{p[2]}", {p[4]})\n'
    out_file.write(p[0])
    return p


def p_wire_assignable(p):
    '''wire_assignable : ID
                       | value'''
    p[0] = p[1]
    return p


def p_reg_declaration(p):
    '''reg_declaration : REG ID SCLN
    '''

    p[0] = f'{module_name}.add_register("{p[2]}", Register(1))\n'
    out_file.write(p[0])
    return p


def p_reg_assign(p):
    '''reg_assign : ID SYNCH_ASSIGN reg_assignable
       reg_assignable : ID
                      | value
    '''
    if len(p) == 4 and p.slice[2].type == 'SYNCH_ASSIGN':
        p[0] = f'{module_name}.synchronous_block.add_procedure(synch_assign, ("{p[1]}", {p[3]}))'
    else:
        p[0] = p[1]
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
    '''
    p[0] = p[1]
    return p


def p_synch_part(p):
    '''synch_part : ALWAYS at_part synch_part_body
    '''
    val_list = []
    pos_list = []
    neg_list = []

    if p.slice[2].value[0] == '"posedge"':
        pos_list.append(p.slice[2].value[1])
    elif p.slice[2].value[0] == '"negedge"':
        neg_list.append(p.slice[2].value[1])
    else:
        val_list.append(p.slice[2].value[1])
    
    synch_block_declaration = f"{module_name}.add_synchronous_block(SynchronousBlock({val_list}, {pos_list}, {neg_list}))"
    value = [synch_block_declaration, *p.slice[3].value]
    value.reverse()

    p[0] = '\n'.join(value)
    out_file.write(p[0] + '\n')
    return p


def p_synch_part_body(p):
    '''synch_part_body : BEGIN synch_stmts END
                       | synch_stmt'''
    if len(p) == 4:
        p[0] = p[2]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        raise Exception()
    return p
    
def p_at_part(p):
    '''at_part : AT OB at_assignment ID CB
    '''
    p[0] = (p[3], p[4])
    return p

def p_at_assignment(p):
    '''at_assignment : posnegedge
                     | value'''
    p[0] = p[1]
    return p

def p_pos_neg_edge(p):
    '''posnegedge : POS EDGE
                  | NEG EDGE
    '''
    p[0] = p[1]
    return p

def p_asynch_statement(p):
    '''asynch_statement : asynch_body SCLN
       asynch_body : wire_assign
                   | ternary_operator
    '''
    p[0] = p[1]
    return p


def p_asynch_part(p):
    '''asynch_part : asynch_part asynch_statement
                   | asynch_statement
    '''
    return p


def p_module_declaration(p):
    '''module_declaration : MODULE ID ports_declaration SCLN body ENDMODULE
                          | MODULE ID body ENDMODULE

    '''
    global module_name
    module_name = p[2]
    if len(p) == 7:
        ins, outs = p[3]
        ins = list(map(lambda io: io[1], ins))
        outs = list(map(lambda io: io[1], outs))
    else:
        ins, outs = ([], [])

    p[0] = f'{module_name} = Module(None, {ins}, {outs})'
    out_file.write(p[0])
    return p


def p_ports_declaration(p):
    '''ports_declaration : OB inputs CB
    '''
    p[0] = p[2]
    return p


def p_inputs(p):
    '''inputs : inputs COM input
              | input'''
    if len(p) == 4:
        ins, outs = p[1]
        new_input = p[3]
        input_type, _ = new_input
        if input_type == 'input':
            ins.append(new_input)
            p[0] = [ins, outs]
        elif input_type == 'output':
            outs.append(new_input)
            p[0] = [ins, outs]
        else:
            raise Exception()
        return p
    elif len(p) == 2:
        input_type, _ = p[1]
        if input_type == 'input':
            p[0] = [[p[1]], []]
            return p
        elif input_type == 'output':
            p[0] = [[], [p[1]]]
            return p
        else:
            raise Exception()
    else:
        raise Exception()


def p_input(p):
    '''input : io SIZE ID
             | io ID
    '''
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        raise Exception()

    return p


def p_io(p):
    '''io : INPUT
          | OUTPUT'''
    p[0] = p[1]
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


def prepare_imports(file):
    file.write('from verilogstructures import *\n')


if __name__ == '__main__':
    lexer = lex.lex()

    # Give the lexer some input
    with open('delay.txt', 'r') as f:
        lines = f.readlines()
        file = ''.join(lines)
        lexer.input(file)

    l_tok = []

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        # print(tok)
        l_tok.append(tok)

    with open('tmp.py', 'w') as f:
        out_file = f

        parser = yacc.yacc()
        parser.parse(file)

    with open('tmp.py', 'r') as tmp_in:
        lines = tmp_in.readlines()
        lines.reverse()

        processed_lines = [f'{lines[0]}\n']
        for line in lines[1:]:
            processed_lines.append(f'{module_name}{line}')

        with open('out.py', 'w') as out:
            prepare_imports(out)
            out.writelines(processed_lines)

    os.remove('tmp.py')
