from typing import Dict, List

from generator import Generator
from lex import Scanner, EofToken, DedentToken, NewlineToken, CommentToken
from syx import Parser, ClassDefNode


class Compiler:
    def __init__(self, program):
        self.program = program + '$'
        self.name_codes: Dict[str, int] = {}
        self.names: List[str] = []
        
        self.classes: Dict[str, ClassDefNode] = {}

        self.tokens = []
        self.tree = None
        
    def add_class(self, node: ClassDefNode):
        self.classes[node.name.attr] = node
        
    def get_class(self, name):
        return self.classes[name]

    def add_name(self, name):
        if name in self.name_codes.keys():
            return self.name_codes[name]
        else:
            code = len(self.names)
            self.names.append(name)
            self.name_codes[name] = code
            return code

    def get_name(self, code):
        return self.names[code]

    def get_scanner(self):
        return Scanner(self.program, self)

    def get_parser(self):
        return Parser(self.tokens, self)

    def get_generator(self):
        return Generator(self)

    def compile(self):
        scanner = self.get_scanner()

        token = None
        nl = True
        dedent = False
        while not isinstance(token, EofToken):
            token = scanner.next_token(nl, dedent)
            if isinstance(token, CommentToken):
                continue
            self.tokens.append(token)

            nl = isinstance(token, NewlineToken)
            dedent = isinstance(token, DedentToken)

            # print(f'{token.tag} {token.attr if token.attr else ""}')

        parser = self.get_parser()
        self.tree = parser.parse()

        generator = self.get_generator()
        return generator.generate(self.tree)
