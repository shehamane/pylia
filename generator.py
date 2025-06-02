from syntax_tree import *

types_map = {
    'int': 'Int64',
    'float': 'Float64',
    'str': 'String',
}

functions_map = {
    'min': 'min',
    'max': 'max',
    'minimum': 'min.',
    'maximum': 'max.',
    'log': 'log.',
    'print': 'println',
    'round': 'round.',
    'shape': 'size',
    'str': 'string'
}

methods_map = {
    'append': 'push!',
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

def get_abstract_name(name: str):
    return f'_A{name}'


class Generator:
    program = ''
    indent_count = 0

    def __init__(self, compiler):
        self.compiler = compiler
        self.cur_class = None
        
    def _is_private(self, name: str):
        return name.startswith('__') and not name.endswith('__')

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
        elif isinstance(node.simple_statement, SuperStatementNode):
            self.super_stmt(node.simple_statement)
        elif isinstance(node.simple_statement, ExpressionsNode):
            self.expressions(node.simple_statement)
        elif isinstance(node.simple_statement, SimpleStmtKeywordToken):
            if node.simple_statement.attr != 'pass':
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
        elif isinstance(node.compound_statement, ClassDefNode):
            self.class_def(node.compound_statement)

    def assignment(self, node: AssignmentNode):
        for decl, expr in zip(node.declarations, node.expressions.expressions):
            cur_node = decl
            prev_node = None
            while cur_node.primary_:
                prev_node = cur_node
                cur_node = cur_node.primary_
                
            if prev_node and cur_node.subscript:
                subscript = cur_node.subscript
                if self.cur_class and self._is_private(subscript.attr):    
                    subscript_name = f'_{self.cur_class.name.attr}{subscript.attr}'
                else:
                    subscript_name = subscript.attr
                prev_node.primary_ = None
                self.program += f'setattr!('
                self.declaration(decl, hint=False)
                self.program += f', :{subscript_name}, '
                self.expression(expr)
                self.program += ')'
                prev_node.primary_ = cur_node
            else:
                self.declaration(decl)
                self.program += f' {node.op.attr} '
                self.expression(expr)
                self.nl()

    def declaration(self, node: DeclarationNode, hint: bool = True):
        primary_start_idx = len(self.program)
        self.program += node.name

        if self.cur_class and node.name == 'self' and node.primary_\
        and node.primary_.subscript and self._is_private(node.primary_.subscript.attr):
                node.primary_.subscript.attr = f'_{self.cur_class.name.attr}' + node.primary_.subscript.attr
        if node.primary_:
            self.primary_(node.primary_, primary_start_idx)
        elif hint and node.annotation and isinstance(node.annotation, TypeNode):
            self.program += '::'
            self.type(node.annotation)

    def return_statement(self, node: ReturnStatementNode):
        self.program += 'return'
        self.w()
        self.expressions(node.expressions)

    def block(self, node: BlockNode, constructor: bool = False, end: bool = True):
        self.indent()
        self.nl()
        self.statements(node.statements)
        
        if constructor:
            self.nl()
            self.nl()
            self.program += 'return self'
            
        self.dedent()
        self.nl()
        
        if end:
            self.program += 'end'
            self.nl()

    def function_def(self, node: FunctionDefNode):
        self.nl()
        self.program += 'function call('
        self.program += f'::Val' + '{' + f':{node.name.attr}' + '}'
            
        if node.params and len(node.params.params):
            self.program += ', '
            for i, param in enumerate(node.params.params):
                self.param(param)
                if i < len(node.params.params) - 1:
                    self.program += ', '
        self.program += ')'
        if node.return_type:
            self.program += '::'
            self.type(node.return_type)

        self.block(node.block)
        self.nl()
        
    def super_stmt(self, node: SuperStatementNode):
        class_node = self.cur_class
        if class_node is None:
            raise Exception('Error')
        
        if node.super_name:
            super_name = node.super_name.attr
        else:
            super_name = class_node.super_name.attr
            
        # Вызов метода суперкласса
        if node.super_call.subscript and node.super_call.primary_ and node.super_call.primary_.arguments:
            if self._is_private(node.super_call.subscript.attr):
                node.super_call.subscript.attr = f'_{super_name}' + node.super_call.subscript.attr
            
            self.program += f'call(Val(:{super_name}), Val(:{node.super_call.subscript.attr}), self'
            
            if node.super_call.primary_.arguments.expressions:
                self.program += ', '
                for i, expr in enumerate(node.super_call.primary_.arguments.expressions):
                    self.expression(expr)
                    if i < len(node.super_call.primary_.arguments.expressions) - 1:
                        self.program += ', '
            self.program += ')'
        else:
            raise Exception('Error')
        
    
    def method(self, node: FunctionDefNode, class_node: ClassDefNode):
        method_name = f'_{class_node.name.attr}{node.name.attr}' if self._is_private(node.name.attr) else node.name.attr
        
        if node.params.params[0].name.attr == 'self':
            self.nl()
            self.program += 'function call('
            
            self.program += f'::Val' + '{' + f':{method_name}' + '}' + f', self::{get_abstract_name(class_node.name.attr)}'

            if node.params and len(node.params.params) > 1:
                self.program += ', '
                for i, param in enumerate(node.params.params[1:]):
                    self.param(param)
                    if i < len(node.params.params) - 2:
                        self.program += ', '
            self.program += ')'
            if node.return_type:
                self.program += '::'
                self.type(node.return_type)
            
            self.block(node.block, constructor=(node.name.attr == '__init__'))
            self.nl()
            
        self.nl()
        self.program += 'function call('
        
        self.program += f'::Val' + '{' + f':{class_node.name.attr}' + '}, ' + f'::Val' + '{' + f':{method_name}' + '}'
            
        if node.params and len(node.params.params):
            self.program += ', '
            for i, param in enumerate(node.params.params):
                self.param(param)
                if i < len(node.params.params) - 1:
                    self.program += ', '
        self.program += ')'
        if node.return_type:
            self.program += '::'
            self.type(node.return_type)
        
        self.block(node.block, constructor=(node.name.attr == '__init__'))
        self.nl()
        
        
    def constructor(self, node: ClassDefNode):
        self.program += f'function {node.name.attr}()'
        self.indent()
        self.nl()
        self.program += 'x = new()'
        self.nl()
        self.program += 'x.__dynamic_attrs = Dict()'
        self.nl()
        self.program += 'return x'
        self.dedent()
        self.nl()
        self.program += 'end'
        
    def getter(self, abstract_name):
        self.program += f'function getattr(self::{abstract_name}, attr::Symbol)'
        self.indent()
        self.nl()
        self.program += 'if hasproperty(self, attr)'
        self.indent()
        self.nl()
        self.program += 'return getproperty(self, attr)'
        self.dedent()
        self.nl()
        self.program += 'elseif haskey(self.__dynamic_attrs, attr)'
        self.indent()
        self.nl()
        self.program += 'return self.__dynamic_attrs[attr]'
        self.dedent()
        self.nl()
        self.program += 'else'
        self.indent()
        self.nl()
        self.program += 'throw("Error: No such attribute")'
        self.dedent()
        self.nl()
        self.program += 'end'
        self.dedent()
        self.nl()
        self.program += 'end'
        
    def setter(self, abstract_name):
        self.program += f'function setattr!(self::{abstract_name}, attr::Symbol, val)'
        self.indent()
        self.nl()
        self.program += 'if hasproperty(self, attr)'
        self.indent()
        self.nl()
        self.program += 'setproperty!(self, attr, val)'
        self.dedent()
        self.nl()
        self.program += 'else'
        self.indent()
        self.nl()
        self.program += 'self.__dynamic_attrs[attr] = val'
        self.dedent()
        self.nl()
        self.program += 'end'
        self.dedent()
        self.nl()
        self.program += 'end'
                
        
    def class_def(self, node: ClassDefNode):
        self.cur_class = node
        
        self.nl()
        abstract_name = get_abstract_name(node.name.attr)
        self.program += f'abstract type {abstract_name}'
        if node.super_name:
            super_abstract_name = f'_A{node.super_name.attr}'
            self.program += f' <: {super_abstract_name}'
        self.program += ' end'
        self.nl()
        
        self.program += f'mutable struct {node.name.attr} <: {abstract_name}'
        
        self.indent()
        self.nl()
        self.program += '__dynamic_attrs::Dict'
        for attr in node.attrs:
            self.nl()
            if self._is_private(attr):
                self.program += f'_{node.name.attr}{attr}'
            else:
                self.program += attr
            if attr in node.attr2type:
                self.program += f'::{types_map[node.attr2type[attr]]}'
                
        if node.super_name:
            super_node = self.compiler.get_class(node.super_name.attr)
            for attr in super_node.attrs:
                if not self._is_private(attr) and attr in node.attrs:
                    continue
                self.nl()
                if self._is_private(attr):
                    self.program += f'_{node.super_name.attr}{attr}'
                else:
                    self.program += attr
                if attr in super_node.attr2type:
                    self.program += f'::{types_map[super_node.attr2type[attr]]}'
        
        self.nl()
        self.nl()
        
        self.constructor(node)
        self.dedent()
        self.nl()
        
        self.program += 'end'
        self.nl()
        
        if not node.has_init:
            self.nl()
            self.program += f'function call(::Val' + '{' + f':{node.name.attr}' + '}, ::Val{:__init__}, self)'
            self.indent()
            self.nl()
            self.program += f'return self'
            self.dedent()
            self.nl()
            self.program += 'end'
            self.nl()
            self.nl()
            self.program += 'function call(::Val{:__init__}, ' + f'self::{abstract_name})'
            self.indent()
            self.nl()
            self.program += f'return self'
            self.dedent()
            self.nl()
            self.program += 'end'
            self.nl()
            
        self.nl()
        self.getter(abstract_name)
        self.nl()
        self.nl()
        self.setter(abstract_name)
        self.nl()
            
        
        for statement in node.block.statements.statements:
            if isinstance(statement.statement, CompoundStatementNode) and isinstance(statement.statement.compound_statement, FunctionDefNode):
                func_def_node = statement.statement.compound_statement
                
                self.method(func_def_node, node)
                
        self.cur_class = None


    def params(self, node: ParamsNode, class_node: ClassDefNode = None, constructor: bool = False):
        for i, param in enumerate(node.params):
            if i == 0 and constructor:
                continue
            self.param(param)
            if i < len(node.params) - 1:
                self.program += ', '

    def param(self, node: ParamNode):
        self.program += node.name.attr
        if node.annotation and isinstance(node.annotation, TypeNode):
            self.program += '::'
            self.type(node.annotation)

    def if_stmt(self, node: IfStatementNode):
        self.program += 'if'
        self.w()
        self.program += '('
        self.expression(node.condition)
        self.program += ')'
        self.block(node.block, end=False)
        if isinstance(node.else_block, ElifStatementNode):
            self.elif_stmt(node.else_block)
        elif isinstance(node.else_block, ElseBlockNode):
            self.else_stmt(node.else_block)
        self.program += 'end'

    def elif_stmt(self, node: ElifStatementNode):
        self.program += 'elseif'
        self.w()
        self.program += '('
        self.expression(node.condition)
        self.program += ')'
        self.block(node.block, end=False)
        if isinstance(node.else_block, ElifStatementNode):
            self.elif_stmt(node.else_block)
        elif isinstance(node.else_block, ElseBlockNode):
            self.else_stmt(node.else_block)

    def else_stmt(self, node: ElseBlockNode):
        self.program += 'else'
        self.w()
        self.block(node.block, end=False)

    def while_stmt(self, node: WhileStatementNode):
        self.program += 'while'
        self.w()
        self.expression(node.condition)
        self.block(node.block)

    def for_stmt(self, node: ForStatementNode):
        self.program += 'for'
        self.w()
        self.program += node.name.attr
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
        if self.program[-2] == '"':
            self.program += '*'
        else:
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
        if node.factor:
            self.program += '^'
            self.factor(node.factor)

    def primary(self, node: PrimaryNode):
        if self.cur_class and isinstance(node.atom.atom, IdentifierToken) and node.atom.atom.attr == 'self'\
            and node.primary_ and node.primary_.subscript and self._is_private(node.primary_.subscript.attr):
                node.primary_.subscript.attr = f'_{self.cur_class.name.attr}' + node.primary_.subscript.attr
        primary_start_idx=len(self.program)
        self.atom(node.atom)
        if node.primary_:
            self.primary_(node.primary_, primary_start_idx)

    def primary_(self, node: PrimaryNode_, primary_start_idx):
        fragment = self.program[primary_start_idx:]
        
        # Вызов статического метода
        if node.subscript and fragment in self.compiler.classes\
        and node.primary_ and node.primary_.arguments:
            if self._is_private(node.subscript.attr):
                node.subscript.attr = f'_{fragment}' + node.subscript.attr
            self.program = self.program[:primary_start_idx]
            self.program += f'call(Val(:{fragment}), Val(:{node.subscript.attr})'
            if node.primary_.arguments.expressions:
                self.program += ', '
                for i, expr in enumerate(node.primary_.arguments.expressions):
                    self.expression(expr)
                    if i < len(node.primary_.arguments.expressions) - 1:
                        self.program += ', '
            self.program += ')'
            node.primary_ = node.primary_.primary_
        
        # Вызов метода
        elif node.subscript and fragment not in self.compiler.classes\
        and node.primary_ and node.primary_.arguments\
        and node.subscript.attr not in methods_map:
            if self._is_private(node.subscript.attr):
                node.subscript.attr = f'_{fragment}' + node.subscript.attr
            self.program = self.program[:primary_start_idx]
            self.program += f'call(Val(:{node.subscript.attr}), {fragment}'
            if node.primary_.arguments.expressions:
                self.program += ', '
                for i, expr in enumerate(node.primary_.arguments.expressions):
                    self.expression(expr)
                    if i < len(node.primary_.arguments.expressions) - 1:
                        self.program += ', '
            self.program += ')'
            node.primary_ = node.primary_.primary_
        elif node.arguments:
            # Вызов конструктора
            if fragment in self.compiler.classes:
                constructor_name = f'__init__'
                self.program = self.program[:primary_start_idx]
                self.program += f'call(Val(:{constructor_name}), {fragment}()'
                if node.arguments.expressions:
                    self.program += ', '
                    for i, expr in enumerate(node.arguments.expressions):
                        self.expression(expr)
                        if i < len(node.arguments.expressions) - 1:
                            self.program += ', '
                self.program += ')'
            # Вызов функции
            else:
                self.program = self.program[:primary_start_idx]
                self.program += f'call(Val(:{fragment})'
                if node.arguments.expressions:
                    self.program += ', '
                    for i, expr in enumerate(node.arguments.expressions):
                        self.expression(expr)
                        if i < len(node.arguments.expressions) - 1:
                            self.program += ', '
                self.program += ')'
        elif node.subscript is not None:
            if node.primary_ and node.primary_.arguments and node.subscript.attr in methods_map:
                fragment = self.program[primary_start_idx:]
                self.program = self.program[:primary_start_idx]
                self.program += f'{methods_map[node.subscript.attr]}({fragment}'
                if len(node.primary_.arguments.expressions):
                    self.program += ', '
                    for i, expr in enumerate(node.primary_.arguments.expressions):
                        self.expression(expr)
                        if i < len(node.primary_.arguments.expressions) - 1:
                            self.program += ', '
                    node.primary_ = node.primary_.primary_
                self.program += ')'
            elif not (node.primary_ and node.primary_.arguments):
                # доступ к полям
                self.program = self.program[:primary_start_idx]
                self.program += f'getattr({fragment}, :{node.subscript.attr})'
        elif node.slices is not None:
            self.program += '['
            self.slices(node.slices)
            self.program += ']'
        if node.primary_:
            self.primary_(node.primary_, primary_start_idx)

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
            self.program += '+ 1'
        elif node.to_expression or node.step_expression:
            self.program += '1'
        if node.to_expression:
            self.program += ':'
            self.expression(node.to_expression)
            self.program += ' - 1'
        if node.step_expression:
            self.program += ':'
            self.expression(node.step_expression)
            

    def atom(self, node: AtomNode):
        if isinstance(node.atom, IdentifierToken):
            self.program += node.atom.attr
        elif isinstance(node.atom, AtomKeywordToken):
            if node.atom.attr == 'True':
                self.program += 'true'
            elif node.atom.attr == 'False':
                self.program += 'false'
            elif node.atom.attr == 'None':
                self.program += 'nothing'
        elif isinstance(node.atom, NumberToken):
            self.program += str(node.atom.attr)
        elif isinstance(node.atom, StringToken):
            self.program += f'"{node.atom.attr}"'
        elif isinstance(node.atom, FStringNode):
            self.fstring(node.atom)
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
        elif node.name == 'len':
            self.program += 'size('
            self.arguments(node.arguments)
            self.program += ', 1)'
        elif node.name == 'range':
            if len(node.arguments.expressions) == 1:
                self.program += '0:'
                self.expression(node.arguments.expressions[0])
                self.program += ' - 1'
            elif len(node.arguments.expressions) == 2:
                self.expression(node.arguments.expressions[0])
                self.program += ':'
                self.expression(node.arguments.expressions[1])
                self.program += ' - 1'
            elif len(node.arguments.expressions) == 3:
                self.expression(node.arguments.expressions[0])
                self.program += ':'
                self.expression(node.arguments.expressions[2])
                self.program += ' - 1'
                self.program += ':'
                self.expression(node.arguments.expressions[1])
            else:
                raise Exception('Range must have maximum 3 arguments')
        else:
            self.program += node.name
            self.program += '('
            self.arguments(node.arguments)
            self.program += ')'
            
    def fstring(self, node: FStringNode):
        self.program += '"'
        for child in node.content:
            if isinstance(child, StringToken):
                self.program += child.attr
            elif isinstance(child, ExpressionNode):
                self.program += '$('
                self.expression(child)
                self.program += ')'
        self.program += '"'

    def group(self, node: GroupNode):
        self.program += '('
        self.expression(node.expression)
        self.program += ')'

    def list(self, node: ListNode):
        self.program += '['
        if node.expressions:
            self.expressions(node.expressions)
        self.program += ']'
        
    def type(self, node: TypeNode):
        if node.type in types_map:
            self.program += types_map[node.type]
        else:
            raise Exception('Unsupported type')
