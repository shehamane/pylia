from pyclbr import Function

from syntax_tree import *


class Parser:
    def __init__(self, seq: List[Token]):
        self.seq = seq
        self.i = 0

    def parse(self):
        return self.statements()

    def _next(self):
        self.i += 1

    def _sym(self):
        return self.seq[self.i]

    def statements(self):
        node = StatementsNode()

        node.statements.append(self.statement())

        while isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), AtomKeywordToken) or \
                isinstance(self._sym(), SimpleStmtKeywordToken) or \
                isinstance(self._sym(), SumOperatorToken) or \
                isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), NumberToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[' or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return' or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr in ('def', 'if', 'for', 'while') or \
                isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
            node.statements.append(self.statement())
        return node

    def statement(self):
        node = StatementNode()

        if isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), AtomKeywordToken) or \
                isinstance(self._sym(), SimpleStmtKeywordToken) or \
                isinstance(self._sym(), SumOperatorToken) or \
                isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), NumberToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[' or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return' or \
                isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
            node.statement = self.simple_statement()
        elif isinstance(self._sym(), CompoundStmtKeywordToken):
            node.statement = self.compound_stmt()
        else:
            raise Exception('Statement parsing error')
        return node

    def simple_statement(self):
        node = SimpleStatementNode()

        if isinstance(self._sym(), IdentifierToken) and \
                isinstance(self.seq[self.i + 1], DelimiterToken) and self.seq[self.i + 1].attr in ('=', ',', ':'):
            node.simple_statement = self.assigment()


        elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return':
            node.simple_statement = self.return_stmt()
        elif isinstance(self._sym(), SimpleStmtKeywordToken):
            node.simple_statement = self._sym()
            self._next()
        elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), SumOperatorToken) or \
                isinstance(self._sym(), AtomKeywordToken) or \
                isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), NumberToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[' or \
                isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
            node.simple_statement = self.expressions()
        else:
            raise Exception('Simple statement parsing error')

        if isinstance(self._sym(), NewlineToken):
            self._next()
        elif not isinstance(self._sym(), DedentToken) and not isinstance(self._sym(), EofToken):
            raise Exception('Simple statements must be divided by newlines')
        return node

    def assigment(self):
        node = AssignmentNode()

        if isinstance(self._sym(), IdentifierToken):
            node.declarations.append(self.declaration())

            while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
                self._next()
                node.declarations.append(self.declaration())
        else:
            raise Exception('Name parsing error')

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '=':
            self._next()
            node.expressions = self.expressions()
        else:
            raise Exception('Assignment parsing error')
        return node

    def declaration(self):
        node = DeclarationNode()

        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym().attr
            self._next()
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
            self._next()
            node.annotation = self.expression()
        return node

    def return_stmt(self):
        node = ReturnStatementNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return':
            self._next()

            node.expressions = self.expressions()
        else:
            raise Exception('Return statement parsing error')
        return node

    def compound_stmt(self):
        node = CompoundStatementNode()
        if isinstance(self._sym(), KeywordToken):
            if self._sym().attr == 'def':
                node.compound_statement = self.function_def()
            elif self._sym().attr == 'if':
                node.compound_statement = self.if_stmt()
            elif self._sym().attr == 'for':
                node.compound_statement = self.for_stmt()
            elif self._sym().attr == 'while':
                node.compound_statement = self.while_stmt()
            else:
                raise Exception('Compound statement parsing error')
        else:
            raise Exception('Compound statement parsing error')
        return node

    def params(self):
        node = ParamsNode()
        node.params.append(self.param())

        while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
            self._next()
            node.params.append(self.param())
        return node

    def param(self):
        node = ParamNode()

        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym()
            self._next()

            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                node.annotation = self.expression()
        else:
            raise Exception('Function parameter parsing error')
        return node

    def function_def(self):
        node = FunctionDefNode()

        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'def':
            self._next()
            if isinstance(self._sym(), IdentifierToken):
                node.name = self._sym()
                self._next()
                if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '(':
                    self._next()

                    if isinstance(self._sym(), IdentifierToken):
                        node.params = self.params()

                    if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ')':
                        self._next()

                        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '->':
                            self._next()
                            node.return_type = self.expression()
                        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                            self._next()
                            node.block = self.block()
                        else:
                            raise Exception('Function block parsing error')
                else:
                    raise Exception('Function signature parsing error')
            else:
                raise Exception('Function name parsing error')
        else:
            raise Exception('Function define parsing error')
        return node

    def if_stmt(self):
        node = IfStatementNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'if':
            self._next()
            node.condition = self.expression()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                node.block = self.block()

                if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'elif':
                    node.else_block = self.elif_stmt()
                elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
                    node.else_block = self.else_block()
            else:
                raise Exception('If statement parsing error')
        else:
            raise Exception('If statement parsing error')
        return node

    def elif_stmt(self):
        node = ElifStatementNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'elif':
            self._next()
            node.condition = self.expression()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                node.block = self.block()

                if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'elif':
                    node.else_block = self.elif_stmt()
                elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
                    node.else_block = self.else_block()
        return node

    def for_stmt(self):
        node = ForStatementNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'for':
            self._next()
            if isinstance(self._sym(), IdentifierToken):
                node.name = self._sym()
                self._next()
                if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'in':
                    self._next()
                    node.expressions = self.expressions()
                    if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                        self._next()
                        node.block = self.block()
                        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
                            node.else_block = self.else_block()
                    else:
                        raise Exception('For statement block parsing error')
                else:
                    raise Exception('For statement condition parsing error')
            else:
                raise Exception('For statement condition parsing error')
        else:
            raise Exception('For statement parsing error')
        return node

    def while_stmt(self):
        node = WhileStatementNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'while':
            self._next()
            node.condition = self.expression()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                node.block = self.block()
                if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
                    node.else_block = self.else_block()
        return node

    def block(self):
        node = BlockNode()
        if isinstance(self._sym(), NewlineToken):
            self._next()
            if isinstance(self._sym(), IndentToken):
                self._next()
                node.statements = self.statements()
                if isinstance(self._sym(), DedentToken):
                    self._next()
                else:
                    raise Exception('Dedentation parsing error')
            else:
                raise Exception('Indentation parsing error')
        else:
            raise Exception('Newline parsing error')
        return node

    def else_block(self):
        node = ElseBlockNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
            self._next()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                node.block = self.block()
            else:
                raise Exception('Else block parsing error')
        else:
            raise Exception('Else block parsing error')
        return node

    def expressions(self):
        node = ExpressionsNode()
        node.expressions.append(self.expression())

        while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
            self._next()
            node.expressions.append(self.expression())
        return node

    def expression(self):
        node = ExpressionNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), SumOperatorToken) or \
                isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), AtomKeywordToken) or \
                isinstance(self._sym(), NumberToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{') or \
                isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
            node.disjunction = self.disjunction()
        else:
            raise Exception('Expression parsing error')
        return node

    def disjunction(self):
        node = DisjunctionNode()
        node.conjuctions.append(self.conjunction())

        while isinstance(self._sym(), KeywordToken) and self._sym().attr == 'or':
            self._next()
            node.conjuctions.append(self.conjunction())
        return node

    def conjunction(self):
        node = ConjunctionNode()
        node.inverstions.append(self.inversion())

        while isinstance(self._sym(), KeywordToken) and self._sym().attr == 'and':
            self._next()
            node.inverstions.append(self.inversion())
        return node

    def inversion(self):
        node = InversionNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not':
            self._next()
            node.inv = self.inversion()
        else:
            node.comparison = self.comparison()
        return node

    def comparison(self):
        node = ComparisonNode()
        node.sum = self.sum()

        if isinstance(self._sym(), ComparisonOperatorToken):
            node.comparison_ = self.comparison_()
        return node

    def comparison_(self):
        node = ComparisonNode_()

        if isinstance(self._sym(), ComparisonOperatorToken):
            node.op = self._sym()
            self._next()
        else:
            raise Exception('Comparison parsing error')

        node.sum = self.sum()

        if isinstance(self._sym(), ComparisonOperatorToken):
            node.comparison_ = self.comparison_()
        return node

    def sum(self):
        node = SumNode()
        node.term = self.term()

        if isinstance(self._sym(), SumOperatorToken):
            node.sum_ = self.sum_()
        return node

    def sum_(self):
        node = SumNode_()

        if isinstance(self._sym(), SumOperatorToken):
            node.op = self._sym()
            self._next()
        else:
            raise Exception('Sum parsing error')
        node.term = self.term()

        if isinstance(self._sym(), SumOperatorToken):
            node.sum_ = self.sum_()

        return node

    def term(self):
        node = TermNode()
        node.factor = self.factor()

        if isinstance(self._sym(), MulOperatorToken):
            node.term_ = self.term_()
        return node

    def term_(self):
        node = TermNode_()

        if isinstance(self._sym(), MulOperatorToken):
            node.op = self._sym()
            self._next()
        else:
            raise Exception('Mul parsing error')
        node.factor = self.factor()

        if isinstance(self._sym(), MulOperatorToken):
            node.term_ = self.term_()
        return node

    def factor(self):
        node = FactorNode()
        if isinstance(self._sym(), SumOperatorToken):
            node.op = self._sym()
            self._next()
        node.power = self.power()
        return node

    def power(self):
        node = PowerNode()
        node.primary = self.primary()
        if isinstance(self._sym(), OperatorToken) and self._sym().attr == '**':
            self._next()
            node.factor = self.factor()
        return node

    def primary(self):
        node = PrimaryNode()
        node.atom = self.atom()

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('.', '(', '['):
            node.primary_ = self.primary_()
        return node

    def primary_(self):
        node = PrimaryNode_()

        if isinstance(self._sym(), DelimiterToken):
            if self._sym().attr == '.':
                self._next()
                if isinstance(self._sym(), IdentifierToken):
                    node.subscript = self._sym()
                    self._next()
                else:
                    raise Exception('Subscript parsing error')
            elif self._sym().attr == '(':
                self._next()

                node.arguments = self.arguments()

                if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ')':
                    self._next()
                else:
                    raise Exception('Arguments parsing error')
            elif self._sym().attr == '[':
                self._next()
                node.slices = self.slices()
                if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ']':
                    self._next()
                else:
                    raise Exception('Slices parsing error')
            else:
                raise Exception('Primary_ parsing error')
        else:
            raise Exception('Primary_ parsing error')

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('.', '(', '['):
            node.primary_ = self.primary_()

        return node

    def arguments(self):
        node = ArgumentsNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), SumOperatorToken) or \
                isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), AtomKeywordToken) or \
                isinstance(self._sym(), NumberToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{') or \
                isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
            node.expressions.append(self.expression())

            while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
                self._next()

                node.expressions.append(self.expression())

        return node

    def slices(self):
        node = SlicesNode()
        node.slices.append(self.slice())

        while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
            self._next()
            node.slices.append(self.slice())
        return node

    def slice(self):
        node = SliceNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), SumOperatorToken) or \
                isinstance(self._sym(), IdentifierToken) or \
                isinstance(self._sym(), AtomKeywordToken) or \
                isinstance(self._sym(), NumberToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{') or \
                isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
            node.from_expression = self.expression()
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
            self._next()
            if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                    isinstance(self._sym(), SumOperatorToken) or \
                    isinstance(self._sym(), IdentifierToken) or \
                    isinstance(self._sym(), AtomKeywordToken) or \
                    isinstance(self._sym(), NumberToken) or \
                    isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{') or \
                    isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
                node.from_expression = self.expression()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                        isinstance(self._sym(), SumOperatorToken) or \
                        isinstance(self._sym(), IdentifierToken) or \
                        isinstance(self._sym(), AtomKeywordToken) or \
                        isinstance(self._sym(), NumberToken) or \
                        isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{') or \
                        isinstance(self._sym(), FunctionToken) or isinstance(self._sym(), NumpyToken):
                    node.from_expression = self.expression()
        return node

    def atom(self):
        node = AtomNode()
        if isinstance(self._sym(), IdentifierToken) or \
                (isinstance(self._sym(), KeywordToken) and self._sym().attr in ('True', 'False', 'None')) or \
                isinstance(self._sym(), IntegerToken) or isinstance(self._sym(), FloatToken):
            node.atom = self._sym()
            self._next()
        elif isinstance(self._sym(), DelimiterToken) and self._sym().attr == '(':
            node.atom = self.group()
        elif isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('[',):
            node.atom = self.list()
        elif isinstance(self._sym(), NumpyToken):
            node.atom = self.numpy()
        elif isinstance(self._sym(), FunctionToken):
            node.atom = self.function()
        else:
            raise Exception('Atom parsing error')
        return node

    def numpy(self):
        node = NumpyNode()
        if isinstance(self._sym(), NumpyToken):
            self._next()
        else:
            raise Exception()
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '.':
            self._next()
        else:
            raise Exception()
        if isinstance(self._sym(), FunctionToken):
            node.function = self.function()
        else:
            raise Exception()
        return node

    def function(self):
        node = BuiltinFunctionNode()
        if isinstance(self._sym(), FunctionToken):
            node.name = self._sym().attr
            self._next()
        else:
            raise Exception()
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '(':
            self._next()
            node.arguments = self.arguments()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ')':
                self._next()
            else:
                raise Exception()
        else:
            raise Exception
        return node

    def group(self):
        node = GroupNode()
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '(':
            self._next()
            node.expression = self.expression()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ')':
                self._next()
            else:
                raise Exception('Group parsing error')
        else:
            raise Exception('Group parsing error')
        return node

    def list(self):
        node = ListNode()
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[':
            self._next()
            node.expressions = self.expressions()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ']':
                self._next()
            else:
                raise Exception('List parsing error')
        else:
            raise Exception('List parsing error')
        return node
