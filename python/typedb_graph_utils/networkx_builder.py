from abc import ABC
from networkx import MultiDiGraph
from typing import Dict

from typedb.analyze import Pipeline
from typedb.common.enums import ConstraintExactness

from .converter import TypeDBAnswerConverter
from .data_constraint import (
    Isa, Has, Links, Is, Iid,
    Sub, Owns, Relates, Plays, Label, Kind, Value,
    Expression, FunctionCall, Comparison,
    ConceptVertex, NamedRoleVertex,
)


class NetworkXBuilder(TypeDBAnswerConverter[MultiDiGraph]):

    def __init__(self, pipeline: Pipeline):
        super().__init__(pipeline)
        self.graph = MultiDiGraph()

    def finish(self) -> MultiDiGraph:
        return self.graph

    def add_isa(self, isa: Isa):
        if isa.instance() is None or isa.type() is None or isa.pipeline_constraint.type().is_label():
            return
        edge_type = "isa!" if isa.exactness() == ConstraintExactness.Exact else "isa"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(isa.instance(), isa.type(), edge_attributes)

    def add_has(self, has: Has):
        if has.owner() is None or has.attribute() is None:
            return
        edge_type = "has!" if has.exactness() == ConstraintExactness.Exact else "has"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(has.owner(), has.attribute(), edge_attributes)

    def add_links(self, links: Links):
        if links.relation() is None or links.player() is None:
            return
        if isinstance(links.role(), ConceptVertex):
            role_label = links.role().concept.get_label()
        elif isinstance(links.role(), NamedRoleVertex):
            role_label = links.role().name()
        else:
            role_label = None
        edge_type = f"{role_label}"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(links.relation(), links.player(), edge_attributes)

    def add_sub(self, sub: Sub):
        if sub.subtype() is None or sub.supertype() is None:
            return
        edge_type = "sub!" if sub.exactness() == ConstraintExactness.Exact else "sub"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(sub.subtype(), sub.supertype(), edge_attributes)

    def add_owns(self, owns: Owns):
        if owns.owner() is None or owns.attribute() is None:
            return
        edge_type = "owns!" if owns.exactness() == ConstraintExactness.Exact else "owns"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(owns.owner(), owns.attribute(), edge_attributes)

    def add_relates(self, relates: Relates):
        if relates.relation() is None or relates.role() is None:
            return
        edge_type = "relates!" if relates.exactness() == ConstraintExactness.Exact else "relates"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(relates.relation(), relates.role(), edge_attributes)

    def add_plays(self, plays: Plays):
        if plays.player() is None or plays.role() is None:
            return
        edge_type = "plays!" if plays.exactness() == ConstraintExactness.Exact else "plays"
        edge_attributes = {"label": edge_type}
        self._may_add_edge(plays.player(), plays.role(), edge_attributes)

    def add_kind(self, kind: Kind):
        pass

    def add_label(self, label: Label):
        pass

    def add_value(self, value: Value):
        pass

    def add_expression(self, expr: Expression):
        if expr.assigned() is None or 0 == len(expr.arguments()) is None:
            return
        # Assigned edge:
        assigned_var_name = self.pipeline.get_variable_name(expr.pipeline_constraint.assigned().as_variable())
        assign_edge_attrs = {"label": f"assign[{assigned_var_name}]", "var": assigned_var_name}
        self._may_add_edge(expr.expression_vertex(), expr.assigned(), assign_edge_attrs)

        for (arg, arg_var) in zip(expr.arguments(), expr.pipeline_constraint.arguments()):
            arg_var_name = self.pipeline.get_variable_name(arg_var.as_variable())
            arg_edge_attributes = {"label": f"arg[{arg_var_name}]", "var": arg_var_name}
            self._may_add_edge(arg, expr.expression_vertex(), arg_edge_attributes)

    def add_function_call(self, fc: FunctionCall):
        # We refrain from drawing
        if 0 == len(fc.assigned()) is None or 0 == len(fc.arguments()) is None:
            return
        # Assigned edge:
        for (assigned, assigned_var) in zip(fc.assigned(), fc.pipeline_constraint.assigned()):
            assigned_var_name = self.pipeline.get_variable_name(assigned_var.as_variable())
            assign_edge_attrs = {"label": f"assign[{assigned_var_name}]", "var": assigned_var_name}
            self._may_add_edge(fc.call_vertex(), assigned, assign_edge_attrs)

        for (arg, arg_var) in zip(fc.arguments(), fc.pipeline_constraint.arguments()):
            arg_var_name = self.pipeline.get_variable_name(arg_var.as_variable())
            arg_edge_attributes = {"label": f"arg[{arg_var_name}]", "var": arg_var_name}
            self._may_add_edge(arg, fc.call_vertex(), arg_edge_attributes)

    def add_is(self, is_c: Is):
        pass

    def add_iid(self, iid: Iid):
        pass

    def add_comparison(self, comp: Comparison):
        pass  # We prefer not to

    # Helpers
    def _may_add_node(self, node):
        if not self.graph.has_node(node):
            self.graph.add_node(node)

    def _may_add_edge(self, u, v, attributes: Dict[str, str]):
        if not self.graph.has_edge(u, v):
            self._may_add_node(u)
            self._may_add_node(v)
            self.graph.add_edge(u, v, **attributes)
