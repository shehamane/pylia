from syntax_tree import *

types_map = {
    'int': 'Int64',
    'float': 'Float64'
}

functions_map = {
    'min': 'min',
    'max': 'max',
    'minimum': 'min.',
    'maximum': 'max.',
    'log': 'log.',
    'print': 'println',
    'round': 'round.',
    'len': 'size',
    'shape': 'size'
}

tensor_op_map = {
    'equal': '.==',
    'less': '.<',
    'less_equal': '.<=',
    'greater': '.>',
    'greater_equal': '.>=',
    'dot': '*',
    'multiply': '.*',
    'add': '.+',
    'subtract': '.-',
    'divide': './',
}


class Generator:
    program = ''
    indent_count = 0

    def __init__(self, compiler):
        self.compiler = compiler

    def generate(self, tree):
        self.statements(tree)
        return self.program

    def w(self):
        self.program += ' '

    def nl(self):
        self.program += '\n'
        self.program += '    ' * self.indent_count

    def indent(self):
        self.indent_count += 1

    def dedent(self):
        self.indent_count -= 1

    def statements(self, node: StatementsNode):
        for i, statement in enumerate(node.statements):
            self.statement(statement)
            if i < len(node.statements) - 1:
                self.nl()

    def statement(self, node: StatementNode):
        if isinstance(node.statement, SimpleStatementNode):
            self.simple_statement(node.statement)
        elif isinstance(node.statement, CompoundStatementNode):
            self.compound_statement(node.statement)

    def simple_statement(self, node: SimpleStatementNode):
        if isinstance(node.simple_statement, AssignmentNode):
            self.assignment(node.simple_statement)
        elif isinstance(node.simple_statement, ExpressionsNode):
            self.expressions(node.simple_statement)
        elif isinstance(node.simple_statement, SimpleStmtKeywordToken):
            self.program += node.simple_statement.attr
            self.w()
        elif isinstance(node.simple_statement, ReturnStatementNode):
            self.return_statement(node.simple_statement)

    def compound_statement(self, node: CompoundStatementNode):
        if isinstance(node.compound_statement, FunctionDefNode):
            self.function_def(node.compound_statement)
        elif isinstance(node.compound_statement, IfStatementNode):
            self.if_stmt(node.compound_statement)
        elif isinstance(node.compound_statement, ForStatementNode):
            self.for_stmt(node.compound_statement)
        elif isinstance(node.compound_statement, WhileStatementNode):
            self.while_stmt(node.compound_statement)

    def assignment(self, node: AssignmentNode):
        for i, declaration in enumerate(node.declarations):
            self.declaration(declaration)
            if i < len(node.declarations) - 1:
                self.program += ', '

        self.w()
        self.program += '='
        self.w()
        self.expressions(node.expressions)

    def declaration(self, node: DeclarationNode):
        self.program += self.compiler.get_name(node.name)

        if node.annotation and isinstance(node.annotation, TypeNode):
            self.program += '::'
            self.type(node.annotation)

    def return_statement(self, node: ReturnStatementNode):
        self.program += 'return'
        self.w()
        self.expressions(node.expressions)

    def block(self, node: BlockNode):
        self.indent()
        self.nl()
        self.statements(node.statements)
        self.dedent()
        self.nl()
        self.program += 'end'

    def function_def(self, node: FunctionDefNode):
        self.program += 'function'
        self.w()
        self.program += self.compiler.get_name(node.name.attr)
        self.program += '('
        if node.params:
            self.params(node.params)
        self.program += ')'

        if node.return_type:
            self.program += '::'

            start = len(self.program)
            self.expression(node.return_type)
            type_ = self.program[start:]
            if type_ in types_map:
                self.program = self.program[:start] + types_map[type_]

        self.block(node.block)
        self.nl()

    def params(self, node: ParamsNode):
        for i, param in enumerate(node.params):
            self.param(param)
            if i < len(node.params) - 1:
                self.program += ', '

    def param(self, node: ParamNode):
        self.program += self.compiler.get_name(node.name.attr)
        if node.annotation and isinstance(node.annotation, TypeNode):
            self.program += '::'
            self.type(node.annotation)

    def if_stmt(self, node: IfStatementNode):
        self.program += 'if'
        self.w()
        self.program += '('
        self.expression(node.condition)
        self.program += ')'
        self.block(node.block)
        if isinstance(node.else_block, ElifStatementNode):
            self.elif_stmt(node.else_block)
        elif isinstance(node.else_block, ElseBlockNode):
            self.else_stmt(node.else_block)

    def elif_stmt(self, node: ElifStatementNode):
        self.program += 'elseif'
        self.w()
        self.program += '('
        self.expression(node.condition)
        self.program += ')'
        self.block(node.block)
        if isinstance(node.else_block, ElifStatementNode):
            self.elif_stmt(node.else_block)
        elif isinstance(node.else_block, ElseBlockNode):
            self.else_stmt(node.else_block)

    def else_stmt(self, node: ElseBlockNode):
        self.program += 'else'
        self.w()
        self.block(node.block)

    def while_stmt(self, node: WhileStatementNode):
        self.program += 'while'
        self.w()
        self.expression(node.condition)
        self.block(node.block)

    def for_stmt(self, node: ForStatementNode):
        self.program += 'for'
        self.w()
        self.program += self.compiler.get_name(node.name.attr)
        self.w()
        self.program += 'in'
        self.w()
        self.expressions(node.expressions)
        self.w()
        self.block(node.block)

    def expressions(self, node: ExpressionsNode):
        for i, expression in enumerate(node.expressions):
            self.expression(expression)
            if i < len(node.expressions) - 1:
                self.program += ', '

    def expression(self, node: ExpressionNode):
        self.disjunction(node.disjunction)

    def disjunction(self, node: DisjunctionNode):
        for i, conjunction in enumerate(node.conjuctions):
            self.conjunction(conjunction)
            if i < len(node.conjuctions) - 1:
                self.program += ' || '

    def conjunction(self, node: ConjunctionNode):
        for i, inversion in enumerate(node.inverstions):
            self.inversion(inversion)
            if i < len(node.inverstions) - 1:
                self.program += ' && '

    def inversion(self, node: InversionNode):
        if node.inv:
            self.program += '!'
        self.comparison(node.comparison)

    def comparison(self, node: ComparisonNode):
        self.sum(node.sum)

        if node.comparison_:
            self.comparison_(node.comparison_)

    def comparison_(self, node: ComparisonNode_):
        self.w()
        self.program += '.' + node.op.attr
        self.w()
        self.sum(node.sum)

        if node.comparison_:
            self.comparison_(node.comparison_)

    def sum(self, node: SumNode):
        self.term(node.term)

        if node.sum_:
            self.sum_(node.sum_)

    def sum_(self, node: SumNode_):
        self.w()
        self.program += '.' + node.op.attr
        self.w()
        self.term(node.term)

        if node.sum_:
            self.sum_(node.sum_)

    def term(self, node: TermNode):
        self.factor(node.factor)

        if node.term_:
            self.term_(node.term_)

    def term_(self, node: TermNode_):
        self.w()
        self.program += '.' + node.op.attr
        self.w()
        self.factor(node.factor)

        if node.term_:
            self.term_(node.term_)

    def factor(self, node: FactorNode):
        if node.op:
            self.program += node.op.attr
        self.power(node.power)

    def power(self, node: PowerNode):
        self.primary(node.primary)
        if node.op:
            self.program += node.op.attr
            self.factor(node.factor)

    def primary(self, node: PrimaryNode):
        self.atom(node.atom)
        if node.primary_:
            self.primary_(node.primary_)

    def primary_(self, node: PrimaryNode_):
        if node.subscript is not None:
            self.program += '.'
            self.program += self.compiler.get_name(node.subscript.attr)
        elif node.arguments is not None:
            self.program += '('
            self.arguments(node.arguments)
            self.program += ')'
        elif node.slices is not None:
            self.program += '['
            self.slices(node.slices)
            self.program += ']'
        if node.primary_:
            self.primary_(node.primary_)

    def arguments(self, node: ArgumentsNode):
        for i, expression in enumerate(node.expressions):
            self.expression(expression)
            if i < len(node.expressions) - 1:
                self.program += ', '

    def slices(self, node: SlicesNode):
        for i, slice in enumerate(node.slices):
            self.slice(slice)
            if i < len(node.slices) - 1:
                self.program += ', '

    def slice(self, node: SliceNode):
        if node.from_expression:
            self.expression(node.from_expression)
        if node.to_expression:
            self.program += ':'
            self.expression(node.to_expression)
        if node.step_expression:
            self.program += ':'
            self.expression(node.step_expression)

    def atom(self, node: AtomNode):
        if isinstance(node.atom, IdentifierToken):
            self.program += self.compiler.get_name(node.atom.attr)
        elif isinstance(node.atom, AtomKeywordToken):
            if node.atom.attr == 'True':
                self.program += 'true'
            elif node.atom.attr == 'False':
                self.program += 'false'
            elif node.atom.attr == 'None':
                self.program += 'nothing'
        elif isinstance(node.atom, NumberToken):
            self.program += str(node.atom.attr)
        elif isinstance(node.atom, GroupNode):
            self.group(node.atom)
        elif isinstance(node.atom, ListNode):
            self.list(node.atom)
        elif isinstance(node.atom, NumpyNode):
            self.numpy(node.atom)
        elif isinstance(node.atom, BuiltinFunctionNode):
            self.function(node.atom)

    def numpy(self, node: NumpyNode):
        self.function(node.function)

    def function(self, node: BuiltinFunctionNode):
        if node.name in tensor_op_map.keys():
            arguments = node.arguments
            for i, exp in enumerate(arguments.expressions):
                self.expression(exp)
                if i < len(arguments.expressions) - 1:
                    self.w()
                    self.program += tensor_op_map[node.name]
                    self.w()

        elif node.name in functions_map:
            self.program += functions_map[node.name]
            self.program += '('
            self.arguments(node.arguments)
            self.program += ')'
        elif node.name == 'range':
            if len(node.arguments.expressions) == 1:
                self.program += '1:'
                self.expression(node.arguments.expressions[0])
            elif len(node.arguments.expressions) == 2:
                self.expression(node.arguments.expressions[0])
                self.program += ':'
                self.expression(node.arguments.expressions[1])
            elif len(node.arguments.expressions) == 3:
                self.expression(node.arguments.expressions[0])
                self.program += ':'
                self.expression(node.arguments.expressions[2])
                self.program += ':'
                self.expression(node.arguments.expressions[1])
            else:
                raise Exception('Range must have maximum 3 arguments')
        else:
            self.program += node.name
            self.program += '('
            self.arguments(node.arguments)
            self.program += ')'

    def group(self, node: GroupNode):
        self.program += '('
        self.expression(node.expression)
        self.program += ')'

    def list(self, node: ListNode):
        self.program += '['
        self.expressions(node.expressions)
        self.program += ']'
        
    def type(self, node: TypeNode):
        if node.type in types_map:
            self.program += types_map[node.type]
        else:
            raise Exception('Unsupported type')
