from abc import ABC

from typedb.analyze import Pipeline, Constraint, ConstraintVertex  # , Variable
from typedb.driver import ConceptRow, Concept, RoleType
from typedb.common.enums import Comparator, ConstraintExactness

from typing import List, Optional


class DataVertex(ABC):
    pass


class ConceptVertex(DataVertex):
    def __init__(self, concept: Concept):
        self.concept = concept

    def __hash__(self):
        return hash(self.concept)

    def __eq__(self, other):
        if other is self:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        return self.concept == other.concept

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return self.concept.__repr__()


class NamedRoleVertex(DataVertex):
    def __init__(self, variable, name: str):  # TODO: Type annotate variable: Variable
        self._name = name
        self._variable = variable

    def name(self):
        return self._name

    def __hash__(self):
        return hash(self._variable)

    def __eq__(self, other):
        if other is self:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        return self._variable == other._variable

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return f"RoleVertex({self.name})"


class FunctionCallVertex(DataVertex):
    def __init__(self, name: str, assigned: List[ConceptVertex], arguments: List[ConceptVertex]):
        self.name = name
        self.assigned = tuple(assigned)
        self.arguments = tuple(arguments)

    def __hash__(self):
        return hash((self.name, self.assigned, self.arguments))

    def __eq__(self, other):
        if other is self:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        return (self.name, self.assigned, self.arguments) == (other.name, other.assigned, other.arguments)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return f"Func({self.assigned} = {self.name}[{self.arguments}])"


class ExpressionVertex(DataVertex):
    def __init__(self, text: str, assigned: ConceptVertex, arguments: List[ConceptVertex]):
        self.text = text
        self.arguments = tuple(arguments)
        self.assigned = assigned

    def __hash__(self):
        return hash((self.text, self.assigned, self.arguments))

    def __eq__(self, other):
        if other is self:
            return True
        if other is None or not isinstance(other, self.__class__):
            return False
        return (self.text, self.assigned, self.arguments) == (other.text, other.assigned, other.arguments)

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        return f"Expr({self.text})"
        # return f"Expr({self.text}, {self.assigned}, [{self.arguments}])"


def resolve_constraint_vertex(pipeline: Pipeline, vertex: ConstraintVertex, concept_row: ConceptRow) -> Optional[DataVertex]:
    if vertex.is_label():
        return ConceptVertex(vertex.as_label())
    elif vertex.is_variable():
        var_name = pipeline.get_variable_name(vertex.as_variable())
        return ConceptVertex(concept_row.get(var_name)) if var_name else None
    elif vertex.is_value():
        return ConceptVertex(vertex.as_value())
    elif vertex.is_named_role():
        return NamedRoleVertex(vertex.as_named_role().variable(), vertex.as_named_role().name())
    else:
        return None


class DataConstraint(ABC):
    """
    The pattern in the database that matched the TypeQLConstraint
    """

    def __init__(self, pipeline_constraint: Constraint, answer_index: Optional[int]):
        self.pipeline_constraint = pipeline_constraint
        self.answer_index = answer_index

    @staticmethod
    def of(pipeline: Pipeline, constraint: Constraint, answer_index: Optional[int],
           concept_row: ConceptRow) -> Optional["DataConstraint"]:
        if constraint.is_isa():
            isa = constraint.as_isa()
            instance = resolve_constraint_vertex(pipeline, isa.instance(), concept_row)
            type_ = resolve_constraint_vertex(pipeline, isa.type(), concept_row)
            exactness = isa.exactness()
            return Isa(constraint, answer_index, instance, type_, exactness)

        elif constraint.is_has():
            has = constraint.as_has()
            owner = resolve_constraint_vertex(pipeline, has.owner(), concept_row)
            attribute = resolve_constraint_vertex(pipeline, has.attribute(), concept_row)
            exactness = has.exactness()
            return Has(constraint, answer_index, owner, attribute, exactness)

        elif constraint.is_links():
            links = constraint.as_links()
            relation = resolve_constraint_vertex(pipeline, links.relation(), concept_row)
            player = resolve_constraint_vertex(pipeline, links.player(), concept_row)
            role = resolve_constraint_vertex(pipeline, links.role(), concept_row)
            exactness = links.exactness()
            return Links(constraint, answer_index, relation, player, role, exactness)

        elif constraint.is_sub():
            sub = constraint.as_sub()
            subtype = resolve_constraint_vertex(pipeline, sub.subtype(), concept_row)
            supertype = resolve_constraint_vertex(pipeline, sub.supertype(), concept_row)
            exactness = sub.exactness()
            return Sub(constraint, answer_index, subtype, supertype, exactness)

        elif constraint.is_owns():
            owns = constraint.as_owns()
            owner = resolve_constraint_vertex(pipeline, owns.owner(), concept_row)
            attribute = resolve_constraint_vertex(pipeline, owns.attribute(), concept_row)
            exactness = owns.exactness()
            return Owns(constraint, answer_index, owner, attribute, exactness)

        elif constraint.is_relates():
            relates = constraint.as_relates()
            relation = resolve_constraint_vertex(pipeline, relates.relation(), concept_row)
            role = resolve_constraint_vertex(pipeline, relates.role(), concept_row)
            exactness = relates.exactness()
            return Relates(constraint, answer_index, relation, role, exactness)

        elif constraint.is_plays():
            plays = constraint.as_plays()
            player = resolve_constraint_vertex(pipeline, plays.player(), concept_row)
            role = resolve_constraint_vertex(pipeline, plays.role(), concept_row)
            exactness = plays.exactness()
            return Plays(constraint, answer_index, player, role, exactness)

        elif constraint.is_function_call():
            fc = constraint.as_function_call()
            name = fc.name()
            arguments = [resolve_constraint_vertex(pipeline, v, concept_row) for v in fc.arguments()]
            assigned = [resolve_constraint_vertex(pipeline, v, concept_row) for v in fc.assigned()]
            fc_vertex = FunctionCallVertex(name, assigned, arguments)
            return FunctionCall(constraint, answer_index, fc_vertex, arguments, assigned)

        elif constraint.is_expression():
            expr = constraint.as_expression()
            text = expr.text()
            arguments = [resolve_constraint_vertex(pipeline, v, concept_row) for v in expr.arguments()]
            assigned = resolve_constraint_vertex(pipeline, expr.assigned(), concept_row)
            expr_vertex = ExpressionVertex(text, assigned, arguments)
            return Expression(constraint, answer_index, expr_vertex, arguments, assigned)

        elif constraint.is_is():
            isc = constraint.as_is()
            lhs = resolve_constraint_vertex(pipeline, isc.lhs(), concept_row)
            rhs = resolve_constraint_vertex(pipeline, isc.rhs(), concept_row)
            return Is(constraint, answer_index, lhs, rhs)

        elif constraint.is_iid():
            iid = constraint.as_iid()
            variable = resolve_constraint_vertex(pipeline, iid.variable(), concept_row)
            iid_value = iid.iid()
            return Iid(constraint, answer_index, variable, iid_value)

        elif constraint.is_comparison():
            comp = constraint.as_comparison()
            lhs = resolve_constraint_vertex(pipeline, comp.lhs(), concept_row)
            rhs = resolve_constraint_vertex(pipeline, comp.rhs(), concept_row)
            comparator = comp.comparator()
            return Comparison(constraint, answer_index, lhs, rhs, comparator)

        elif constraint.is_kind_of():
            kindc = constraint.as_kind()
            kind_enum = kindc.kind()
            type_ = resolve_constraint_vertex(pipeline, kindc.type(), concept_row)
            return Kind(constraint, answer_index, kind_enum, type_)

        elif constraint.is_label():
            label = constraint.as_label()
            variable = resolve_constraint_vertex(pipeline, label.variable(), concept_row)
            label_value = label.label()
            return Label(constraint, answer_index, variable, label_value)

        elif constraint.is_value():
            val = constraint.as_value()
            attribute_type = resolve_constraint_vertex(pipeline, val.attribute_type(), concept_row)
            value_type = val.value_type()
            return Value(constraint, answer_index, attribute_type, value_type)
        elif constraint.is_or() or constraint.is_not() or constraint.is_try():
            return None  # We're not interested in the structure in this case
        else:
            raise TypeError("Unsupported constraint variant: %s" % (type(constraint),))

    def is_isa(self) -> bool:
        return False

    def is_has(self) -> bool:
        return False

    def is_links(self) -> bool:
        return False

    def is_sub(self) -> bool:
        return False

    def is_owns(self) -> bool:
        return False

    def is_relates(self) -> bool:
        return False

    def is_plays(self) -> bool:
        return False

    def is_function_call(self) -> bool:
        return False

    def is_expression(self) -> bool:
        return False

    def is_is(self) -> bool:
        return False

    def is_iid(self) -> bool:
        return False

    def is_comparison(self) -> bool:
        return False

    def is_kind_of(self) -> bool:
        return False

    def is_label(self) -> bool:
        return False

    def is_value(self) -> bool:
        return False

    def as_isa(self) -> "Isa":
        raise TypeError("Bad cast. Expected: 'Isa'; was: '%s'" % (self.__class__.__name__,))

    def as_has(self) -> "Has":
        raise TypeError("Bad cast. Expected: 'Has'; was: '%s'" % (self.__class__.__name__,))

    def as_links(self) -> "Links":
        raise TypeError("Bad cast. Expected: 'Links'; was: '%s'" % (self.__class__.__name__,))

    def as_sub(self) -> "Sub":
        raise TypeError("Bad cast. Expected: 'Sub'; was: '%s'" % (self.__class__.__name__,))

    def as_owns(self) -> "Owns":
        raise TypeError("Bad cast. Expected: 'Owns'; was: '%s'" % (self.__class__.__name__,))

    def as_relates(self) -> "Relates":
        raise TypeError("Bad cast. Expected: 'Relates'; was: '%s'" % (self.__class__.__name__,))

    def as_plays(self) -> "Plays":
        raise TypeError("Bad cast. Expected: 'Plays'; was: '%s'" % (self.__class__.__name__,))

    def as_function_call(self) -> "FunctionCall":
        raise TypeError("Bad cast. Expected: 'FunctionCall'; was: '%s'" % (self.__class__.__name__,))

    def as_expression(self) -> "Expression":
        raise TypeError("Bad cast. Expected: 'Expression'; was: '%s'" % (self.__class__.__name__,))

    def as_is(self) -> "Is":
        raise TypeError("Bad cast. Expected: 'Is'; was: '%s'" % (self.__class__.__name__,))

    def as_iid(self) -> "Iid":
        raise TypeError("Bad cast. Expected: 'Iid'; was: '%s'" % (self.__class__.__name__,))

    def as_comparison(self) -> "Comparison":
        raise TypeError("Bad cast. Expected: 'Comparison'; was: '%s'" % (self.__class__.__name__,))

    def as_kind(self) -> "Kind":
        raise TypeError("Bad cast. Expected: 'Kind'; was: '%s'" % (self.__class__.__name__,))

    def as_label(self) -> "Label":
        raise TypeError("Bad cast. Expected: 'Label'; was: '%s'" % (self.__class__.__name__,))

    def as_value(self) -> "Value":
        raise TypeError("Bad cast. Expected: 'Value'; was: '%s'" % (self.__class__.__name__,))


class Isa(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], instance: ConceptVertex, type_: ConceptVertex,
                 exactness):
        super().__init__(constraint, answer_index)
        self._instance = instance
        self._type = type_
        self._exactness = exactness

    def is_isa(self) -> bool:
        return True

    def as_isa(self):
        return self

    def instance(self) -> ConceptVertex:
        return self._instance

    def type(self) -> ConceptVertex:
        return self._type

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class Has(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], owner: ConceptVertex, attribute: ConceptVertex,
                 exactness):
        super().__init__(constraint, answer_index)
        self._owner = owner
        self._attribute = attribute
        self._exactness = exactness

    def is_has(self) -> bool:
        return True

    def as_has(self):
        return self

    def owner(self) -> ConceptVertex:
        return self._owner

    def attribute(self) -> ConceptVertex:
        return self._attribute

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class Links(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], relation: ConceptVertex, player: ConceptVertex,
                 role: DataVertex, exactness):
        super().__init__(constraint, answer_index)
        self._relation = relation
        self._player = player
        self._role = role
        self._exactness = exactness

    def is_links(self) -> bool:
        return True

    def as_links(self):
        return self

    def relation(self) -> ConceptVertex:
        return self._relation

    def player(self) -> ConceptVertex:
        return self._player

    def role(self) -> DataVertex:
        return self._role

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class Sub(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], subtype: ConceptVertex, supertype: ConceptVertex,
                 exactness):
        super().__init__(constraint, answer_index)
        self._subtype = subtype
        self._supertype = supertype
        self._exactness = exactness

    def is_sub(self) -> bool:
        return True

    def as_sub(self):
        return self

    def subtype(self) -> ConceptVertex:
        return self._subtype

    def supertype(self) -> ConceptVertex:
        return self._supertype

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class Owns(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], owner: ConceptVertex, attribute: ConceptVertex,
                 exactness):
        super().__init__(constraint, answer_index)
        self._owner = owner
        self._attribute = attribute
        self._exactness = exactness

    def is_owns(self) -> bool:
        return True

    def as_owns(self):
        return self

    def owner(self) -> ConceptVertex:
        return self._owner

    def attribute(self) -> ConceptVertex:
        return self._attribute

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class Relates(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], relation: ConceptVertex, role: DataVertex,
                 exactness):
        super().__init__(constraint, answer_index)
        self._relation = relation
        self._role = role
        self._exactness = exactness

    def is_relates(self) -> bool:
        return True

    def as_relates(self):
        return self

    def relation(self) -> ConceptVertex:
        return self._relation

    def role(self) -> DataVertex:
        return self._role

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class Plays(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], player: ConceptVertex, role: ConceptVertex, exactness):
        super().__init__(constraint, answer_index)
        self._player = player
        self._role = role
        self._exactness = exactness

    def is_plays(self) -> bool:
        return True

    def as_plays(self):
        return self

    def player(self) -> ConceptVertex:
        return self._player

    def role(self) -> ConceptVertex:
        return self._role

    def exactness(self) -> "ConstraintExactness":
        return self._exactness


class FunctionCall(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], call_vertex: FunctionCallVertex,
                 arguments: List[ConceptVertex], assigned: List[ConceptVertex]):
        super().__init__(constraint, answer_index)
        self._call_vertex = call_vertex
        self._arguments = arguments
        self._assigned = assigned

    def is_function_call(self) -> bool:
        return True

    def as_function_call(self):
        return self

    def call_vertex(self) -> str:
        return self._call_vertex

    def arguments(self) -> List[ConceptVertex]:
        return self._arguments

    def assigned(self) -> List[ConceptVertex]:
        return self._assigned


class Expression(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], expr: ExpressionVertex,
                 arguments: List[ConceptVertex], assigned: ConceptVertex):
        super().__init__(constraint, answer_index)
        self._expr = expr
        self._arguments = arguments
        self._assigned = assigned

    def is_expression(self) -> bool:
        return True

    def as_expression(self):
        return self

    def expression_vertex(self) -> ExpressionVertex:
        return self._expr

    def arguments(self) -> List[ConceptVertex]:
        return self._arguments

    def assigned(self) -> ConceptVertex:
        return self._assigned


class Is(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], lhs: ConceptVertex, rhs: ConceptVertex):
        super().__init__(constraint, answer_index)
        self._lhs = lhs
        self._rhs = rhs

    def is_is(self) -> bool:
        return True

    def as_is(self):
        return self

    def lhs(self) -> ConceptVertex:
        return self._lhs

    def rhs(self) -> ConceptVertex:
        return self._rhs


class Iid(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], variable: ConceptVertex, iid_value: str):
        super().__init__(constraint, answer_index)
        self._variable = variable
        self._iid = iid_value

    def is_iid(self) -> bool:
        return True

    def as_iid(self):
        return self

    def variable(self) -> ConceptVertex:
        return self._variable

    def iid(self) -> str:
        return self._iid


class Comparison(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], lhs: ConceptVertex, rhs: ConceptVertex, comparator):
        super().__init__(constraint, answer_index)
        self._lhs = lhs
        self._rhs = rhs
        self._comparator = comparator

    def is_comparison(self) -> bool:
        return True

    def as_comparison(self):
        return self

    def lhs(self) -> ConceptVertex:
        return self._lhs

    def rhs(self) -> ConceptVertex:
        return self._rhs

    def comparator(self) -> "Comparator":
        return self._comparator


class Kind(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], kind_enum, type_: ConceptVertex):
        super().__init__(constraint, answer_index)
        self._kind = kind_enum
        self._type = type_

    def is_kind_of(self) -> bool:
        return True

    def as_kind(self):
        return self

    def kind(self) -> "typedb.common.enums.Kind":
        return self._kind

    def type(self) -> ConceptVertex:
        return self._type


class Label(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], variable: ConceptVertex, label_value: str):
        super().__init__(constraint, answer_index)
        self._variable = variable
        self._label = label_value

    def is_label(self) -> bool:
        return True

    def as_label(self):
        return self

    def variable(self) -> ConceptVertex:
        return self._variable

    def label(self) -> str:
        return self._label


class Value(DataConstraint):
    def __init__(self, constraint: Constraint, answer_index: Optional[int], attribute_type: ConceptVertex, value_type: str):
        super().__init__(constraint, answer_index)
        self._attribute_type = attribute_type
        self._value_type = value_type

    def is_value(self) -> bool:
        return True

    def as_value(self):
        return self

    def attribute_type(self) -> ConceptVertex:
        return self._attribute_type

    def value_type(self) -> str:
        return self._value_type
