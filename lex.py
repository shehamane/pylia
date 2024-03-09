from abc import ABC
from copy import copy
from enum import Enum


class Position:
    def __init__(self, text: str):
        self.text = text
        self.line = 1
        self.pos = 1
        self.idx = 0

    def __iadd__(self, other):
        if isinstance(other, int):
            if self.idx < len(self.text):
                if self.isNl():
                    if self.text[self.idx] == '\r':
                        self.idx += 1
                    self.line += 1
                    self.pos = 1
                    self.idx += 1
                else:
                    self.idx += 1
                    self.pos += 1
        return self

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.idx == other.idx

    def __str__(self):
        return f'({self.line}, {self.pos})'

    def cp(self):
        return self.text[self.idx]

    def isWs(self):
        return self.idx != len(self.text) and self.text[self.idx] == ' '

    def isLetter(self):
        return self.idx != len(self.text) and self.text[self.idx].isalpha()

    def isLetterOrDigit(self):
        return self.idx != len(self.text) and \
            (self.text[self.idx].isalpha() or self.text[self.idx].isdigit() or self.text[self.idx] == '_')

    def isNl(self):
        if self.idx == len(self.text):
            return True
        if self.text[self.idx] == '\r' and self.idx < len(self.text) + 1:
            return self.text[self.idx + 1] == '\n'
        return self.text[self.idx] == '\n'


class Fragment:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def __str__(self):
        return f'{self.start} - {self.end}'

    def get(self):
        return self.start.text[self.start.idx:self.end.idx]


class Message:
    def __init__(self, text: str, pos: Position, error: bool = False):
        self.text = text
        self.pos = pos
        self.error = error


class DomainTag(Enum):
    INDENT = 0
    DEDENT = 1
    NEWLINE = 2
    IDENTIFIER = 3
    KEYWORD = 4
    INTEGER = 5
    FLOAT = 6
    STRING = 7
    OPERATOR = 8
    DELIMITER = 9
    EOF = 10
    NUMBER = 11
    ATOM_KEYWORD = 12
    SUM_OP = 13
    MUL_OP = 14
    POWER_OP = 15
    SIMPLE_STMT_KEYWORD = 16
    COMPOUND_STMT_KEYWORD = 17
    COMPARISON_OPERATORS = 18
    NUMPY = 19
    FUNCTION = 20


KEYWORDS = ('if', 'else', 'for', 'while', 'continue', 'break', 'elif', 'def', 'class',
            'True', 'False', 'None', 'import', 'and', 'or', 'not', 'async', 'await',
            'as', 'assert', 'del', 'finally', 'except', 'raise', 'pass', 'return',
            'try', 'with', 'yield', 'from', 'global', 'lambda', 'is', 'in')
ATOM_KEYWORDS = ('None', 'True', 'False')
SIMPLE_STMT_KEYWORDS = ('pass', 'break', 'continue')
COMPOUND_STMT_KEYWORDS = ('def', 'for', 'while', 'if')
SPEC_SYMBOLS = ('+', '-', '*', '/', '%', '=', '!', '(', ')', ':', '[', ']',
                '{', '}', '.', ':', ';', '<', '>', '!', '@', ',', '&', '^')
BINOP_SYMBOLS = ('+', '-', '*', '/', '%')
OPERATORS = ('+', '-', '*', '/', '%', '**', '//', '@', '<<', '>>',
             '&', '|', '^', '~', ':=', '<', '>', '<=', '>=', '==',
             '!=')
SUM_OPERATORS = ('+', '-')
MUL_OPERATORS = ('*', '/', '//', '%')
POWER_OPERATORS = ('**',)
COMPARISON_OPERATORS = ('==', '!=', '<', '>', '<=', '>=')
DELIMITERS = ('(', ')', '+=', '-=', '*=', '/=', '**=',
              '//=', ':', '.', ';', ',', '=', '->',
              '@=', '&=', '|=', '^=', '>>=', '<<=',
              '[', ']', '{', '}', '%=')
NUMPY_FUNCTIONS = (
    'min', 'max', 'sum', 'subtract', 'multiply', 'divide', 'minimum', 'maximum', 'round',
    'mean', 'median', 'std',
    'log', 'sin', 'cos',
    'dot', 'zeros', 'ones', 'shape', 'transpose',
    'equal', 'less', 'greater', 'less_equal', 'greater_equal',
)
BUILTIN_FUNCTIONS = (
    'print', 'len', 'range'
)


class Token(ABC):
    def __init__(self, tag: DomainTag, start: Position, end: Position):
        self.tag = tag
        self.frag = Fragment(start, end)
        self.attr = None


class IndentToken(Token):
    def __init__(self, start: Position, end: Position):
        super().__init__(DomainTag.INDENT, start, end)


class DedentToken(Token):
    def __init__(self, start: Position, end: Position):
        super().__init__(DomainTag.DEDENT, start, end)


class NewlineToken(Token):
    def __init__(self, start: Position, end: Position):
        super().__init__(DomainTag.NEWLINE, start, end)


class IdentifierToken(Token):
    def __init__(self, start: Position, end: Position, code: int):
        super().__init__(DomainTag.IDENTIFIER, start, end)
        self.attr = code


class NumpyToken(Token):
    def __init__(self, start: Position, end: Position):
        super().__init__(DomainTag.NUMPY, start, end)


class FunctionToken(Token):
    def __init__(self, start: Position, end: Position, kind):
        super().__init__(DomainTag.FUNCTION, start, end)
        self.attr = kind


class KeywordToken(Token):
    def __init__(self, start: Position, end: Position, kind: str, tag=DomainTag.KEYWORD):
        super().__init__(DomainTag.KEYWORD, start, end)
        self.attr = kind


class AtomKeywordToken(KeywordToken):
    def __init__(self, start: Position, end: Position, kind: str):
        super().__init__(start, end, kind, tag=DomainTag.ATOM_KEYWORD)


class SimpleStmtKeywordToken(KeywordToken):
    def __init__(self, start: Position, end: Position, kind: str):
        super().__init__(start, end, kind, tag=DomainTag.SIMPLE_STMT_KEYWORD)


class CompoundStmtKeywordToken(KeywordToken):
    def __init__(self, start: Position, end: Position, kind: str):
        super().__init__(start, end, kind, tag=DomainTag.COMPOUND_STMT_KEYWORD)


class StringToken(Token):
    def __init__(self, start: Position, end: Position, content: str):
        super().__init__(DomainTag.STRING, start, end)
        self.attr = content


class NumberToken(Token):
    def __init__(self, start: Position, end: Position, number, tag=DomainTag.NUMBER):
        super().__init__(tag, start, end)
        self.attr = number


class IntegerToken(NumberToken):
    def __init__(self, start: Position, end: Position, number):
        super().__init__(start, end, number, tag=DomainTag.INTEGER)


class FloatToken(NumberToken):
    def __init__(self, start: Position, end: Position, number):
        super().__init__(start, end, number, tag=DomainTag.FLOAT)


class OperatorToken(Token):
    def __init__(self, start: Position, end: Position, kind, tag=DomainTag.OPERATOR):
        super().__init__(tag, start, end)
        self.attr = kind


class SumOperatorToken(OperatorToken):
    def __init__(self, start: Position, end: Position, kind):
        super().__init__(start, end, kind, DomainTag.SUM_OP)


class MulOperatorToken(OperatorToken):
    def __init__(self, start: Position, end: Position, kind):
        super().__init__(start, end, kind, DomainTag.MUL_OP)


class PowerOperatorToken(OperatorToken):
    def __init__(self, start: Position, end: Position):
        super().__init__(start, end, '**', DomainTag.POWER_OP)


class ComparisonOperatorToken(OperatorToken):
    def __init__(self, start: Position, end: Position, kind):
        super().__init__(start, end, kind, DomainTag.COMPARISON_OPERATORS)


class DelimiterToken(Token):
    def __init__(self, start: Position, end: Position, kind):
        super().__init__(DomainTag.DELIMITER, start, end)
        self.attr = kind


class EofToken(Token):
    def __init__(self, start: Position, end: Position):
        super().__init__(DomainTag.EOF, start, end)


class Scanner:
    indents = [0]
    INDENT_BASE = 4

    def __init__(self, program: str, compiler):
        self.program = program
        self.cur = Position(program)
        self.compiler = compiler
        self.last_indent = 0
        self.indents = [0]

    def next_token(self, nl=False, dedent=False) -> Token:
        while self.cur.cp() != '$':

            start = copy(self.cur)

            if dedent:
                if self.last_indent < self.indents[-1]:
                    self.indents = self.indents[:-1]
                    return DedentToken(start, copy(self.cur))
                elif self.last_indent > self.indents[-1]:
                    self.indents.append(self.last_indent)

            if not nl:
                while self.cur.isWs() or self.cur.cp() == '\\':
                    if self.cur.isWs():
                        self.cur += 1
                    if self.cur.cp() == '\\':
                        self.cur += 1

                        while self.cur.isWs():
                            self.cur += 1

                        if self.cur.isNl():
                            self.cur += 1

            if (self.cur.isWs() or self.cur.isNl()) and nl:
                ws = 0
                while self.cur.isWs() or self.cur.isNl():
                    while self.cur.isWs():
                        ws += 1
                        self.cur += 1

                    if self.cur.isNl():
                        ws = 0
                        self.cur += 1

                if ws % self.INDENT_BASE:
                    raise Exception('Invalid indentation')

                indent = ws // self.INDENT_BASE

                self.last_indent = indent
                if indent > self.indents[-1]:
                    self.indents.append(indent)
                    return IndentToken(start, copy(self.cur))
                elif indent < self.indents[-1]:
                    self.indents = self.indents[:-1]
                    return DedentToken(start, copy(self.cur))

            elif self.cur.isNl():
                self.cur += 1
                return NewlineToken(start, copy(self.cur))

            elif self.cur.isLetter():
                cum = ''
                while self.cur.isLetterOrDigit():
                    cum += self.cur.cp()
                    self.cur += 1

                if cum in KEYWORDS:
                    if cum in ATOM_KEYWORDS:
                        return AtomKeywordToken(start, copy(self.cur), cum)
                    if cum in SIMPLE_STMT_KEYWORDS:
                        return SimpleStmtKeywordToken(start, copy(self.cur), cum)
                    if cum in COMPOUND_STMT_KEYWORDS:
                        return CompoundStmtKeywordToken(start, copy(self.cur), cum)
                    return KeywordToken(start, copy(self.cur), cum)
                elif cum == 'np':
                    return NumpyToken(start, copy(self.cur))
                elif cum in BUILTIN_FUNCTIONS or cum in NUMPY_FUNCTIONS:
                    return FunctionToken(start, copy(self.cur), cum)
                else:
                    return IdentifierToken(start, copy(self.cur), self.compiler.add_name(cum))

            elif self.cur.cp().isdigit():
                cum = ''
                while self.cur.cp().isdigit():
                    cum += self.cur.cp()
                    self.cur += 1
                if len(cum) > 1 and cum[0] == '0':
                    raise Exception('Decimal cannot starts with zero')

                if self.cur.cp() == '.':
                    cum += self.cur.cp()
                    self.cur += 1
                    if self.cur.cp().isdigit():
                        while self.cur.cp().isdigit():
                            cum += self.cur.cp()
                            self.cur += 1
                        if self.cur.isLetter():
                            raise Exception('Invalid identifier')
                        return FloatToken(start, copy(self.cur), float(cum))
                    else:
                        raise Exception('Invalid number')
                elif self.cur.cp() == 'e':
                    cum += self.cur.cp()
                    self.cur += 1

                    if self.cur.cp() in ('+', '-'):
                        cum += self.cur.cp()
                        self.cur += 1

                    if not self.cur.cp().isdigit():
                        raise Exception('Invalid mantis')
                    while self.cur.cp().isdigit():
                        cum += self.cur.cp()
                        self.cur += 1
                    if self.cur.isLetter():
                        raise Exception('Invalid mantis')

                    return FloatToken(start, copy(self.cur), float(cum))

                elif self.cur.isLetter():
                    raise Exception('Invalid identifier')
                else:
                    return IntegerToken(start, copy(self.cur), int(cum))

            elif self.cur.cp() == '\'' or self.cur.cp() == '"':
                quote = self.cur.cp()
                cum = ''
                self.cur += 1
                while self.cur.cp() != quote or self.cur.cp() != '\n' or self.cur.cp() != -1:
                    cum += self.cur.cp()
                    self.cur += 1

                    if self.cur.cp() == '\\':
                        self.cur += 1
                        if self.cur.isNl():
                            self.cur += 1

                if self.cur.cp() == '\n' or self.cur.cp() != -1:
                    raise Exception('Invalid string literal')

            elif self.cur.cp() in SPEC_SYMBOLS:
                cum = ''
                cum += self.cur.cp()
                self.cur += 1

                if (cum == '/' and self.cur.cp() == '/') or \
                        (cum == '*' and self.cur.cp() == '*') or \
                        (cum == '<' and self.cur.cp() == '<') or \
                        (cum == '>' and self.cur.cp() == '>') or \
                        (cum == ':' and self.cur.cp() == '=') or \
                        ((cum == '<' or cum == '>' or cum == '=' or cum == '!') and self.cur.cp() == '='):
                    cum += self.cur.cp()
                    self.cur += 1

                    if cum == '**':
                        return PowerOperatorToken(start, copy(self.cur))
                    elif cum == '//':
                        return MulOperatorToken(start, copy(self.cur), cum)
                    elif cum in COMPARISON_OPERATORS:
                        return ComparisonOperatorToken(start, copy(self.cur), cum)

                    return OperatorToken(start, copy(self.cur), cum)

                if (cum == '-' and self.cur.cp() == '>') or \
                        (cum in BINOP_SYMBOLS and self.cur.cp() == '='):
                    cum += self.cur.cp()
                    self.cur += 1
                    return DelimiterToken(start, copy(self.cur), cum)

                if cum in SUM_OPERATORS:
                    return SumOperatorToken(start, copy(self.cur), cum)
                if cum in MUL_OPERATORS:
                    return MulOperatorToken(start, copy(self.cur), cum)
                if cum in COMPARISON_OPERATORS:
                    return ComparisonOperatorToken(start, copy(self.cur), cum)
                if cum in OPERATORS:
                    return OperatorToken(start, copy(self.cur), cum)
                if cum in DELIMITERS:
                    return DelimiterToken(start, copy(self.cur), cum)

            else:
                raise Exception('Unexpected symbol')

        if len(self.indents) > 1:
            self.indents = self.indents[:-1]
            return DedentToken(copy(self.cur), copy(self.cur))
        return EofToken(copy(self.cur), copy(self.cur))
