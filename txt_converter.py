from dataclasses import dataclass


@dataclass
class Token:
    name: str
    expression: str

    def expression_as_regex(self):
        characters_needing_escape = ['\\', '[', ']', '(', ')', '{', '}', '*', '+', '?', '|', '^', '$', '.', ]
        regex_compliant_expression: str = self.expression
        for character in characters_needing_escape:
            regex_compliant_expression = regex_compliant_expression.replace(character, f'\\{character}')
        return regex_compliant_expression


if __name__ == '__main__':
    with open('tokens.txt', 'r') as f:
        tokens = []
        for line in f:
            expression, name = line.replace('\n', '').split('\t')
            tokens.append(Token(name=name.replace(' ', ''), expression=expression.replace(' ', '')))

    with open('tokens_out.py', 'w+') as out:
        out.write('tokens = (\n')
        for token in tokens:
            out.write(f'    \'{token.name}\',\n')
        out.write(')\n\n\n')

        for token in tokens:
            out.write(f't_{token.name} = r\'{token.expression_as_regex()}\'\n')
