import {Concept, ConstraintVertexAny} from "@typedb/driver-http";
import { MultiGraph } from "graphology";
import {
    AbstractGraphBuilder,
    DataConstraintIsa, DataConstraintIsaExact, DataConstraintHas, DataConstraintLinks,
    DataConstraintSub, DataConstraintSubExact, DataConstraintOwns, DataConstraintRelates,
    DataConstraintPlays, DataConstraintExpression, DataConstraintFunction,
    DataConstraintKind, DataConstraintComparison, DataConstraintIs, DataConstraintIid,
    DataConstraintLabel, DataConstraintValue, VertexUnavailable,
} from "@typedb/graph-utils";

export type VertexExpression = { tag: "expression", kind: "expression", repr: string, answerIndex: number, vertex_map_key: string };
export type VertexFunction = { tag: "functionCall", kind: "functionCall", repr: string, answerIndex: number, vertex_map_key: string };
export type DataVertexSpecial = VertexUnavailable | VertexFunction | VertexExpression;

type DataVertex = Concept | DataVertexSpecial;


const VERTEX_COLORS: Record<string, string> = {
    entity: "#5DA5DA",
    relation: "#FAA43A",
    attribute: "#60BD68",
    entityType: "#5DA5DA",
    relationType: "#FAA43A",
    attributeType: "#60BD68",
    roleType: "#B276B2",
    value: "#DECF3F",
    unavailable: "#999999",
    expression: "#F17CB0",
    functionCall: "#F15854",
};

function vertexLabel(vertex: DataVertex): string {
    switch (vertex.kind) {
        case "entity": return vertex.type.label;
        case "relation": return vertex.type.label;
        case "attribute": return `${vertex.type.label}: ${vertex.value}`;
        case "entityType":
        case "relationType":
        case "attributeType":
        case "roleType":
            return vertex.label;
        case "value": return `${vertex.value}`;
        case "unavailable": return `?${vertex.variable}`;
        case "expression": return vertex.repr;
        case "functionCall": return vertex.repr;
    }
}

function vertexMapKey(vertex: DataVertex): string {
    switch (vertex.kind) {
        case "attribute": return `${vertex.type.label}:${vertex.value}`;
        case "entity":
        case "relation": return vertex.iid;
        case "attributeType":
        case "entityType":
        case "relationType":
        case "roleType": return vertex.label;
        case "value": return `${vertex.valueType}:${vertex.value}`;
        case "expression":
        case "functionCall": return vertex.vertex_map_key;
        case "unavailable": return `unavailable[${vertex.variable}][${vertex.answerIndex}]`;
    }
}

export class SigmaConverter extends AbstractGraphBuilder {
    constructor(public readonly graph: MultiGraph) {
        super()
    }

    private addVertex(vertex: DataVertex): string {
        const key = vertexMapKey(vertex);
        if (vertex.kind !== "unavailable" && !this.graph.hasNode(key)) {
            this.graph.addNode(key, {
                label: vertexLabel(vertex),
                color: VERTEX_COLORS[vertex.kind] || "#999",
                size: vertex.kind === "roleType" ? 5 : 10,
                x: Math.random(),
                y: Math.random(),
            });
        }
        return key;
    }

    private addEdge(label: string, from: DataVertex, to: DataVertex) {
        if (from.kind === "unavailable" || to.kind === "unavailable") return;
        const fromKey = this.addVertex(from);
        const toKey = this.addVertex(to);
        const edgeKey = `${fromKey}:${toKey}:${label}`;
        if (!this.graph.hasDirectedEdge(edgeKey)) {
            const type = this.graph.hasDirectedEdge(fromKey, toKey) ? "curved" : "arrow";
            this.graph.addDirectedEdgeWithKey(edgeKey, fromKey, toKey, {
                label,
                color: "#999",
                size: 2,
                type,
            });
        }
    }

    vertex(_answerIndex: number, vertex: DataVertex, _queryVertex: ConstraintVertexAny): void {
        this.addVertex(vertex);
    }

    isa(_answerIndex: number, c: DataConstraintIsa): void {
        if (c.queryConstraint.type.tag == "variable") {
            // We ignore `isa <label>` edges to reduce noise
            this.addEdge("isa", c.instance, c.type);
        }
    }

    isaExact(_answerIndex: number, c: DataConstraintIsaExact): void {
        this.addEdge("isa!", c.instance, c.type);
    }

    has(_answerIndex: number, c: DataConstraintHas): void {
        this.addEdge("has", c.owner, c.attribute);
    }

    links(_answerIndex: number, c: DataConstraintLinks): void {
        const label = c.role.kind === "roleType" ? c.role.label.split(":").at(-1)! : "?";
        this.addEdge(label, c.relation, c.player);
    }

    sub(_answerIndex: number, c: DataConstraintSub): void {
        this.addEdge("sub", c.subtype, c.supertype);
    }

    subExact(_answerIndex: number, c: DataConstraintSubExact): void {
        this.addEdge("sub!", c.subtype, c.supertype);
    }

    owns(_answerIndex: number, c: DataConstraintOwns): void {
        this.addEdge("owns", c.owner, c.attribute);
    }

    relates(_answerIndex: number, c: DataConstraintRelates): void {
        this.addEdge("relates", c.relation, c.role);
    }

    plays(_answerIndex: number, c: DataConstraintPlays): void {
        this.addEdge("plays", c.player, c.role);
    }

    expression(answerIndex: number, c: DataConstraintExpression): void {
        const exprVertex: VertexExpression = {
            tag: "expression", kind: "expression", repr: c.text,
            answerIndex, vertex_map_key: `expr(${c.arguments.map(v => vertexMapKey(v)).join(",")})`,
        };
        this.addEdge("=", exprVertex, c.assigned);
        c.arguments.forEach(arg => {
            this.addEdge("arg", arg, exprVertex);
        });
    }

    function(answerIndex: number, c: DataConstraintFunction): void {
        const fnVertex: VertexFunction = {
            tag: "functionCall", kind: "functionCall", repr: c.name,
            answerIndex, vertex_map_key: `fn:${c.name}(${c.arguments.map(v => vertexMapKey(v)).join(",")})`,
        };
        c.assigned.forEach(assigned => {
            this.addEdge("=", fnVertex, assigned);
        });
        c.arguments.forEach(arg => {
            this.addEdge("arg", arg, fnVertex);
        });
    }

    kind(_answerIndex: number, c: DataConstraintKind): void {
        this.addVertex(c.type);
    }

    comparison(_answerIndex: number, c: DataConstraintComparison): void {
        this.addEdge(c.comparator, c.lhs, c.rhs);
    }

    is(_answerIndex: number, c: DataConstraintIs): void {
        this.addEdge("is", c.lhs, c.rhs);
    }

    iid(_answerIndex: number, c: DataConstraintIid): void {
        this.addVertex(c.concept);
    }

    label(_answerIndex: number, c: DataConstraintLabel): void {
        this.addVertex(c.type);
    }

    value(_answerIndex: number, c: DataConstraintValue): void {
        this.addVertex(c.attributeType);
    }
}
