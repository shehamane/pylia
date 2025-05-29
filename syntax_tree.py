from typing import List, Any, Optional, Dict

from lex import *


class SyntaxNode:
    def __init__(self):
        pass


class StatementsNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.statements: List[StatementNode] = []


class StatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.statement: Any[CompoundStatementNode, SimpleStatementNode] = None


class SimpleStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.simple_statement: Any[AssignmentNode, ExpressionsNode, SimpleStmtKeywordToken] = None


class CompoundStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.compound_statement: Any[FunctionDefNode, IfStatementNode, ForStatementNode, WhileStatementNode] = None


class AssignmentNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.declarations: List[DeclarationNode] = []
        self.expressions: ExpressionsNode = None


class DeclarationNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.name: IdentifierToken = None
        self.annotation: Any[ExpressionNode, TypeNode] = None


class ReturnStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.expressions: Optional[ExpressionsNode] = None


class BlockNode(SyntaxNode):
    def __init__(self):
        super().__init__()

        self.statements: StatementsNode = None


class FunctionDefNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.name: IdentifierToken = None
        self.params: Optional[ParamsNode] = None
        self.return_type: Optional[ExpressionNode] = None
        self.block: BlockNode = None
        
class ClassDefNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.name: IdentifierToken = None
        self.super_name: IdentifierToken = None
        self.block: BlockNode = None
        self.attrs: List[IdentifierToken] = None
        self.attr2type: Dict[IdentifierToken, ] = None


class ParamsNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.params: List[ParamNode] = []


class ParamNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.name: IdentifierToken = None
        self.annotation: Any[ExpressionNode, TypeNode] = None


class IfStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.condition: ExpressionNode = None
        self.block: BlockNode = None
        self.else_block: Optional[Any[ElifStatementNode, ElseBlockNode]] = None


class ElifStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.condition: ExpressionNode = None
        self.block: BlockNode = None
        self.else_block: Optional[Any[ElifStatementNode, ElseBlockNode]] = None


class ElseBlockNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.block: BlockNode = None


class WhileStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.condition: ExpressionNode = None
        self.block: BlockNode = None
        self.else_block: Optional['ElseBlockNode'] = None


class ForStatementNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.name: IdentifierToken = None
        self.expressions: ExpressionsNode = None
        self.block: BlockNode = None
        self.else_block: Optional[ElseBlockNode] = None


class ExpressionsNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.expressions: List[ExpressionNode] = []


class ExpressionNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.disjunction: DisjunctionNode = None


class DisjunctionNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.conjuctions: List[ConjunctionNode] = []


class ConjunctionNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.inverstions: List[InversionNode] = []


class InversionNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.inv: Optional[KeywordToken] = None
        self.comparison: ComparisonNode = None


class ComparisonNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.sum: SumNode = None
        self.comparison_: Optional[ComparisonNode_] = None


class ComparisonNode_(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.op: ComparisonOperatorToken = None
        self.sum: SumNode = None
        self.comparison_: Optional[ComparisonNode_] = None


class SumNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.term: TermNode = None
        self.sum_: Optional[SumNode_] = None


class SumNode_(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.op: SumOperatorToken = None
        self.term: TermNode = None
        self.sum_: Optional[SumNode_] = None


class TermNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.factor: FactorNode = None
        self.term_: Optional[TermNode_] = None


class TermNode_(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.op: MulOperatorToken = None
        self.factor: FactorNode = None
        self.term_: Optional[TermNode_] = None


class FactorNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.op: Optional[OperatorToken] = None
        self.power: PowerNode = None


class PowerNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.op: Optional[OperatorToken] = None
        self.factor: Optional[FactorNode] = None
        self.primary: PrimaryNode = None


class PrimaryNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.atom: AtomNode = None
        self.primary_: Optional[PrimaryNode_] = None


class PrimaryNode_(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.slices: Optional[SlicesNode] = None
        self.arguments: Optional[ArgumentsNode] = None
        self.subscript: Optional[IdentifierToken] = None
        self.primary_: Optional[PrimaryNode_] = None


class ArgumentsNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.expressions: List[ExpressionNode] = []


class SlicesNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.slices: List[SliceNode] = []


class SliceNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.from_expression: Optional[ExpressionNode] = None
        self.to_expression: Optional[ExpressionNode] = None
        self.step_expression: Optional[ExpressionNode] = None


class AtomNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.atom: Any[IdentifierToken, AtomKeywordToken, NumberToken, GroupNode, ListNode] = None


class NumpyNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.function: BuiltinFunctionNode = None


class BuiltinFunctionNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.name: IdentifierToken = None
        self.arguments: Optional[ArgumentsNode] = None


class GroupNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.expression: ExpressionNode = None


class ListNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.expressions: ExpressionsNode = None
        
class TypeNode(SyntaxNode):
    def __init__(self):
        super().__init__()
        self.type: str = None
