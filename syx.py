from pyclbr import Function

from syntax_tree import *

class NameSpace:
    def __init__(self):
        self.names = []
        self.name2code = {}
        
    def add(self, name):
        if name in self.name2code:
            return self.name_codes[name]
        else:
            code = len(self.names)
            self.names.append(name)
            self.name2code[name] = code
            return code


class Parser:
    def __init__(self, seq: List[Token], compiler):
        self.seq = seq
        self.i = 0
        self.compiler = compiler

    def parse(self):
        return self.statements()

    def _next(self):
        self.i += 1

    def _sym(self):
        return self.seq[self.i]

    def expect(self, type_, attr, message):
        if isinstance(self._sym(), type_) and (attr is None or self._sym().attr == attr):
            self._next()
        else:
            raise Exception(message)

    def statements(self):
        # statements: statement+
        node = StatementsNode()

        node.statements.append(self.statement())

        while type(self._sym()) in (IdentifierToken, AtomKeywordToken,
                                    SimpleStmtKeywordToken, SumOperatorToken,
                                    IdentifierToken, NumberToken,
                                    IntegerToken, FloatToken,
                                    FunctionToken, NumpyToken,
                                    CompoundStmtKeywordToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[' or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return':
            node.statements.append(self.statement())

        return node

    def statement(self):
        # statement: compound_stmt  | simple_stmt NEWLINE
        node = StatementNode()

        if type(self._sym()) in (IdentifierToken, AtomKeywordToken,
                                 SimpleStmtKeywordToken, SumOperatorToken,
                                 IdentifierToken, NumberToken,
                                 IntegerToken, FloatToken,
                                 FunctionToken, NumpyToken, SuperKeywordToken) or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[' or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return':
            node.statement = self.simple_statement()
        elif isinstance(self._sym(), CompoundStmtKeywordToken):
            node.statement = self.compound_stmt()
        else:
            raise Exception('Statement parsing error: Keyword expected')

        return node

    def simple_statement(self):
        # simple_stmt:
        # | assignment
        # | expressions
        # | return_stmt
        # | 'pass'
        # | 'break'
        # | 'continue'
        node = SimpleStatementNode()
        
        if isinstance(self._sym(), IdentifierToken):
            is_assign = False
            j = 1
            while (not isinstance(self.seq[self.i + j], (NewlineToken, EofToken))):
                if isinstance(self.seq[self.i + j], DelimiterToken) and self.seq[self.i + j].attr == '=':
                    is_assign = True
                    break
                j += 1
                
            if is_assign:
                node.simple_statement = self.assigment()
            else:
                node.simple_statement = self.expressions()
        elif isinstance(self._sym(), SuperKeywordToken):
            node.simple_statement = self.super_stmt()
        elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return':
            node.simple_statement = self.return_stmt()
        elif isinstance(self._sym(), SimpleStmtKeywordToken):
            node.simple_statement = self._sym()
            self._next()
        elif type(self._sym()) in (SumOperatorToken, AtomKeywordToken,
                                   IdentifierToken, NumberToken,
                                   IntegerToken, FloatToken,
                                   FunctionToken, NumpyToken) or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[':
            node.simple_statement = self.expressions()
        else:
            raise Exception('Simple statement parsing error')

        if isinstance(self._sym(), NewlineToken):
            self._next()
        elif not isinstance(self._sym(), DedentToken) and not isinstance(self._sym(), EofToken):
            raise Exception('Simple statements must be divided by newlines')

        return node
    
    def super_stmt(self):
        node = SuperStatementNode()
        
        self.expect(SuperKeywordToken, 'super', 'Expected "super" keyword')
        self.expect(DelimiterToken, '(', 'Error')
        if isinstance(self._sym(), IdentifierToken):
            node.super_name = IdentifierToken
        self.expect(DelimiterToken, ')', 'Error')        
        node.super_call = self.primary_()
        
        return node

    def assigment(self):
        # assignment: ','.(declaration)+ '=' expressions
        node = AssignmentNode()

        if isinstance(self._sym(), IdentifierToken):
            node.declarations.append(self.declaration())

            while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
                self._next()
                node.declarations.append(self.declaration())
        else:
            raise Exception('Assignment parsing error: Declaration expected')

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '=':
            self._next()
            node.expressions = self.expressions()
        else:
            raise Exception('Assignment parsing error: Symbol "=" expected')
        return node

    def declaration(self):
        # declaration: NAME [annotation]
        # annotation: ':' expression
        node = DeclarationNode()

        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym().attr
            self._next()
        else:
            raise Exception('Declaration parsing error: Identifier expected')
        
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('.', '(', '['):
            node.primary_ = self.primary_()
        
        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
            self._next()
            if isinstance(self._sym(), TypeToken):
                node.annotation = self.type()
            else:
                node.annotation = self.expression()
        return node

    def return_stmt(self):
        # return_stmt: 'return' [expressions]
        node = ReturnStatementNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'return':
            self._next()

            node.expressions = self.expressions()
        else:
            raise Exception('Return statement parsing error: Keyword "return" expected')
        return node

    def compound_stmt(self):
        # compound_stmt:
        # | function_def
        # | if_stmt
        # | for_stmt
        # | while_stmt
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
            elif self._sym().attr == 'class':
                node.compound_statement = self.class_def()
            else:
                raise Exception('Compound statement parsing error: Keyword expected')
        else:
            raise Exception('Compound statement parsing error: Keyword expected')
        return node

    def params(self):
        # params: ','.param+
        node = ParamsNode()
        node.params.append(self.param())

        while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
            self._next()
            node.params.append(self.param())
        return node

    def param(self):
        # param: NAME [annotation]
        node = ParamNode()

        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym()
            self._next()

            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                if isinstance(self._sym(), TypeToken):
                    node.annotation = self.type()
                else:
                    node.annotation = self.expression()
        else:
            raise Exception('Function parameter parsing error: Identifier expected')
        return node

    def function_def(self):
        # function_def: 'def' NAME '(' [params] ')' ['->' expression ] ':'  block
        node = FunctionDefNode()

        self.expect(CompoundStmtKeywordToken, 'def', 'Function definition parsing error: Keyword "def" expected')

        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym()
            self._next()

            self.expect(DelimiterToken, '(', 'Function definition parsing: Symbol "(" expected')

            if isinstance(self._sym(), IdentifierToken):
                node.params = self.params()

            self.expect(DelimiterToken, ')', 'Function definition parsing: Symbol ")" expected')

            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '->':
                self._next()
                node.return_type = self.type()

            self.expect(DelimiterToken, ':', 'Function definition parsing: Symbol ":" expected')

            node.block = self.block()

        else:
            raise Exception('Function definition parsing error: Identifier expected')

        return node
    
    def class_def(self):
        # class_def: 'class' NAME '(' [NAME] ')' ':' block
        node = ClassDefNode()
        
        self.expect(CompoundStmtKeywordToken, 'class', 'Class definition parsing error: Keyword "class" expected')
        
        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym()
            self._next()
            
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == '(':
                self._next()
                if not isinstance(self._sym(), IdentifierToken):
                    raise Exception('Class definition parsing error: Identifier expected')
                
                node.super_name = self._sym()
                self._next()
                
                self.expect(DelimiterToken, ')', 'Class definition parsing error: Symbol ")" expected')
                
            self.expect(DelimiterToken, ':', 'Class definition parsing error: Symbol ":" expected')
            node.block = self.block()
            
            for statement in node.block.statements.statements:
                if isinstance(statement.statement, CompoundStatementNode)\
                    and isinstance(statement.statement.compound_statement, FunctionDefNode)\
                    and statement.statement.compound_statement.name.attr == '__init__':
                        constructor_node = statement.statement.compound_statement
                        for c_statement in constructor_node.block.statements.statements:
                            if isinstance(c_statement.statement, SimpleStatementNode)\
                                and isinstance(c_statement.statement.simple_statement, AssignmentNode):
                                for decl in c_statement.statement.simple_statement.declarations:
                                    if decl.name == 'self' and decl.primary_ and decl.primary_.subscript and not decl.primary_.primary_:
                                        node.attrs.append(decl.primary_.subscript.attr)
                                        if decl.annotation and isinstance(decl.annotation, TypeNode):
                                            node.attr2type[decl.primary_.subscript.attr] = decl.annotation.type
                                                        
        else:
            raise Exception('Class definition parsing error: Identifier expected')
        
        self.compiler.add_class(node)
        
        return node
        

    def if_stmt(self):
        # if_stmt:
        #     | 'if' expression ':' block elif_stmt
        #     | 'if' expression ':' block [else_block]
        node = IfStatementNode()

        self.expect(CompoundStmtKeywordToken, 'if', '"if"-statement parsing error: Keyword "if" expected')

        node.condition = self.expression()

        self.expect(DelimiterToken, ':', '"if"-statement parsing error: Symbol ":" expected')

        node.block = self.block()

        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'elif':
            node.else_block = self.elif_stmt()
        elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
            node.else_block = self.else_block()

        return node

    def elif_stmt(self):
        # elif_stmt:
        #     | 'elif' expression ':' block elif_stmt
        #     | 'elif' expression ':' block [else_block]
        node = ElifStatementNode()

        self.expect(KeywordToken, 'elif', '"elif"-statement parsing error: Keyword "elif" expected')

        node.condition = self.expression()

        self.expect(DelimiterToken, ':', '"elif"-statement parsing error: Symbol ":" expected')

        node.block = self.block()

        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'elif':
            node.else_block = self.elif_stmt()
        elif isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
            node.else_block = self.else_block()

        return node

    def for_stmt(self):
        # for_stmt: 'for' NAME 'in' expressions ':' block [else_block]
        node = ForStatementNode()

        self.expect(CompoundStmtKeywordToken, 'for', '"for"-loop parsing error: Keyword "for" expected')

        if isinstance(self._sym(), IdentifierToken):
            node.name = self._sym()
            self._next()

            self.expect(KeywordToken, 'in', '"for"-loop parsing error: Keyword "in" expected')

            node.expressions = self.expressions()

            self.expect(DelimiterToken, ':', '"for"-loop parsing error: Symbol ":" expected')

            node.block = self.block()

            if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
                node.else_block = self.else_block()
        else:
            raise Exception('For statement parsing error: Identifier expected')

        return node

    def while_stmt(self):
        # while_stmt: 'while' expression ':' block [else_block]
        node = WhileStatementNode()

        self.expect(CompoundStmtKeywordToken, 'while', '"while"-loop parsing error: Keyword "while" expected')

        node.condition = self.expression()

        self.expect(DelimiterToken, ':', '"while"-loop parsing error: Symbol ":" expected')

        node.block = self.block()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'else':
            node.else_block = self.else_block()

        return node

    def block(self):
        # block: NEWLINE INDENT statements DEDENT
        node = BlockNode()

        self.expect(NewlineToken, None, 'Block parsing error: Newline expected')

        self.expect(IndentToken, None, 'Block parsing error: Indentation expected')

        node.statements = self.statements()

        self.expect(DedentToken, None, 'Block parsing error: Dedentation expected')

        return node

    def else_block(self):
        # else_block: 'else' ':' block
        node = ElseBlockNode()

        self.expect(KeywordToken, 'else', '"Else"-block parsing error: Keyword "else" expected')

        self.expect(DelimiterToken, ':', '"Else"-block parsing error: Symbol ":" expected')

        node.block = self.block()

        return node

    def expressions(self):
        # expressions:
        #     | expression (',' NEWLINE* expression )+
        #     | expression
        node = ExpressionsNode()
        node.expressions.append(self.expression())

        while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
            self._next()
            node.expressions.append(self.expression())
        return node

    def expression(self):
        # expression: disjunction
        node = ExpressionNode()

        if type(self._sym()) in (SumOperatorToken, IdentifierToken,
                                 AtomKeywordToken, NumberToken,
                                 IntegerToken, FloatToken,
                                 FunctionToken, NumpyToken, StringToken) or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{'):
            node.disjunction = self.disjunction()
        else:
            raise Exception('Expression parsing error')

        return node

    def disjunction(self):
        # disjunction:
        #     | conjunction ('or' conjunction )+
        #     | conjunction
        node = DisjunctionNode()
        node.conjuctions.append(self.conjunction())

        while isinstance(self._sym(), KeywordToken) and self._sym().attr == 'or':
            self._next()
            node.conjuctions.append(self.conjunction())
        return node

    def conjunction(self):
        # conjunction:
        #     | inversion ('and' inversion )+
        #     | inversion
        node = ConjunctionNode()
        node.inverstions.append(self.inversion())

        while isinstance(self._sym(), KeywordToken) and self._sym().attr == 'and':
            self._next()
            node.inverstions.append(self.inversion())
        return node

    def inversion(self):
        # inversion:
        #     | 'not' inversion
        #     | comparison
        node = InversionNode()
        if isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not':
            self._next()
            node.inv = self.inversion()
        else:
            node.comparison = self.comparison()
        return node

    def comparison(self):
        # comparison:
        #     | sum comparison_
        #     | sum
        node = ComparisonNode()
        node.sum = self.sum()

        if isinstance(self._sym(), ComparisonOperatorToken):
            node.comparison_ = self.comparison_()
        return node

    def comparison_(self):
        # comparison_:
        #     | '==' sum comparison_
        #     | '!=' sum comparison_
        #     | '<' sum comparison_
        #     | '>' sum comparison_
        #     | '<=' sum comparison_
        #     | '>=' sum comparison_
        #     | 'in' sum comparison_
        #     | 'not' 'in' sum comparison_
        #     | '==' sum
        #     | '!=' sum
        #     | '<' sum
        #     | '>' sum
        #     | '<=' sum
        #     | '>=' sum
        #     | 'in' sum
        #     | 'not' 'in' sum
        node = ComparisonNode_()

        if isinstance(self._sym(), ComparisonOperatorToken):
            node.op = self._sym()
            self._next()
        else:
            raise Exception('Comparison parsing error: Operator expected')

        node.sum = self.sum()

        if isinstance(self._sym(), ComparisonOperatorToken):
            node.comparison_ = self.comparison_()
        return node

    def sum(self):
        # sum:
        #     | term sum_
        #     | term
        node = SumNode()
        node.term = self.term()

        if isinstance(self._sym(), SumOperatorToken):
            node.sum_ = self.sum_()
        return node

    def sum_(self):
        # sum_:
        #     | '+' term sum_
        #     | '-' term sum_
        #     | '+' term
        #     | '-' term
        node = SumNode_()

        if isinstance(self._sym(), SumOperatorToken):
            node.op = self._sym()
            self._next()
        else:
            raise Exception('Sum parsing error: Operator expected')
        node.term = self.term()

        if isinstance(self._sym(), SumOperatorToken):
            node.sum_ = self.sum_()

        return node

    def term(self):
        # term:
        #     | factor term_
        #     | factor
        node = TermNode()
        node.factor = self.factor()

        if isinstance(self._sym(), MulOperatorToken):
            node.term_ = self.term_()
        return node

    def term_(self):
        # term_:
        #     | '*' factor term_
        #     | '/' factor term_
        #     | '//' factor term_
        #     | '%' factor term_
        #     | '*' factor
        #     | '/' factor
        #     | '//' factor
        #     | '%' factor
        node = TermNode_()

        if isinstance(self._sym(), MulOperatorToken):
            node.op = self._sym()
            self._next()
        else:
            raise Exception('Mul parsing error: Operator expected')
        node.factor = self.factor()

        if isinstance(self._sym(), MulOperatorToken):
            node.term_ = self.term_()
        return node

    def factor(self):
        # factor:
        #     | '+' factor
        #     | '-' factor
        #     | power
        node = FactorNode()
        if isinstance(self._sym(), SumOperatorToken):
            node.op = self._sym()
            self._next()
        node.power = self.power()
        return node

    def power(self):
        # power:
        #     | primary '**' factor
        #     | primary
        node = PowerNode()
        node.primary = self.primary()
        if isinstance(self._sym(), OperatorToken) and self._sym().attr == '**':
            self._next()
            node.factor = self.factor()
        return node

    def primary(self):
        # primary:
        #     | atom primary_
        #     | atom
        node = PrimaryNode()
        node.atom = self.atom()

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('.', '(', '['):
            node.primary_ = self.primary_()
        return node

    def primary_(self):
        # primary_:
        #     | '.' NAME primary_
        #     | '(' [arguments] ')' primary_
        #     | '[' slices ']' primary_
        #     | '.' NAME
        #     | '(' [arguments] ')'
        #     | '[' slices ']'
        node = PrimaryNode_()

        if isinstance(self._sym(), DelimiterToken):
            if self._sym().attr == '.':
                self._next()
                if isinstance(self._sym(), IdentifierToken):
                    node.subscript = self._sym()
                    self._next()
                else:
                    raise Exception('Subscript parsing error: Identifier expected')
            elif self._sym().attr == '(':
                self._next()

                node.arguments = self.arguments()

                self.expect(DelimiterToken, ')', 'Arguments parsing error: Symbol ")" expected')
            elif self._sym().attr == '[':
                self._next()

                node.slices = self.slices()

                self.expect(DelimiterToken, ']', 'Slices parsing error: Symbol "]" expected')
            else:
                raise Exception('Primary_ parsing error')
        else:
            raise Exception('Primary_ parsing error: Delimiter expected')

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('.', '(', '['):
            node.primary_ = self.primary_()

        return node

    def arguments(self):
        # arguments:
        #     | expression
        #     | ','.(expression)+
        node = ArgumentsNode()

        if type(self._sym()) in (SumOperatorToken, AtomKeywordToken,
                                 NumberToken, IdentifierToken,
                                 IntegerToken, FloatToken,
                                 FunctionToken, NumpyToken, StringToken) or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{'):
            node.expressions.append(self.expression())

            while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
                self._next()

                node.expressions.append(self.expression())

        return node

    def slices(self):
        # slices:
        #     | slice
        #     | ','.(slice)+
        node = SlicesNode()
        node.slices.append(self.slice())

        while isinstance(self._sym(), DelimiterToken) and self._sym().attr == ',':
            self._next()
            node.slices.append(self.slice())
        return node

    def slice(self):
        # slice:
        #     | [expression] ':' [expression] [':' [expression]]
        node = SliceNode()

        if type(self._sym()) in (SumOperatorToken, AtomKeywordToken,
                                 IdentifierToken, NumberToken,
                                 IntegerToken, FloatToken,
                                 FunctionToken, NumpyToken) or \
                isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{'):
            node.from_expression = self.expression()

        if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
            self._next()
            if type(self._sym()) in (SumOperatorToken, AtomKeywordToken,
                                     IdentifierToken, NumberToken,
                                     IntegerToken, FloatToken,
                                     FunctionToken, NumpyToken) or \
                    isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                    isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{'):
                node.to_expression = self.expression()
            if isinstance(self._sym(), DelimiterToken) and self._sym().attr == ':':
                self._next()
                if type(self._sym()) in (SumOperatorToken, AtomKeywordToken,
                                         IdentifierToken, NumberToken,
                                         IntegerToken, FloatToken,
                                         FunctionToken, NumpyToken) or \
                        isinstance(self._sym(), KeywordToken) and self._sym().attr == 'not' or \
                        isinstance(self._sym(), DelimiterToken) and self._sym().attr in ('(', '[', '{'):
                    node.step_expression = self.expression()
        return node

    def atom(self):
        # atom:
        #     | NAME
        #     | 'True'
        #     | 'False'
        #     | 'None'
        #     | NUMBER
        #     | group
        #     | list
        node = AtomNode()

        if type(self._sym()) in (IdentifierToken, AtomKeywordToken,
                                 NumberToken, StringToken,
                                 IntegerToken, FloatToken):
            node.atom = self._sym()
            self._next()
        elif isinstance(self._sym(), DelimiterToken) and self._sym().attr == '(':
            node.atom = self.group()
        elif isinstance(self._sym(), DelimiterToken) and self._sym().attr == '[':
            node.atom = self.list()
        elif isinstance(self._sym(), NumpyToken):
            node.atom = self.numpy()
        elif isinstance(self._sym(), FunctionToken):
            node.atom = self.function()
        else:
            raise Exception('Atom parsing error')
        return node

    def numpy(self):
        # numpy: 'np' '.' function
        node = NumpyNode()

        self.expect(NumpyToken, None, 'Numpy call parsing error: Keyword "np" expected')

        self.expect(DelimiterToken, '.', 'Numpy call parsing error: Symbol "." expected')

        if isinstance(self._sym(), FunctionToken):
            node.function = self.function()
        else:
            raise Exception("Numpy call parsing error: Function expected")

        return node

    def function(self):
        # function: FUNC '(' arguments ')'
        node = BuiltinFunctionNode()
        if isinstance(self._sym(), FunctionToken):
            node.name = self._sym().attr
            self._next()
        else:
            raise Exception("Function parsing error: Function name expected")

        self.expect(DelimiterToken, '(', 'Function parsing error: Symbol "(" expected')

        node.arguments = self.arguments()

        self.expect(DelimiterToken, ')', 'Function parsing error: Symbol ")" expected')

        return node

    def group(self):
        # group:
        #     | '(' expressions ')'
        node = GroupNode()

        self.expect(DelimiterToken, '(', 'Group parsing error: Symbol "(" expected')

        node.expression = self.expression()

        self.expect(DelimiterToken, ')', 'Group parsing error: Symbol ")" expected')

        return node

    def list(self):
        # list: '[' expressions ']'
        node = ListNode()

        self.expect(DelimiterToken, '[', 'List parsing error: Symbol "[" expected')

        node.expressions = self.expressions()

        self.expect(DelimiterToken, ']', 'List parsing error: Symbol "]" expected')

        return node
    
    def type(self):
        node = TypeNode()
        if isinstance(self._sym(), TypeToken):
            node.type = self._sym().attr
            self._next()
        else:
            raise Exception("Function parsing error: Type expected")
        return node
