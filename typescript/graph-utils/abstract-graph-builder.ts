import { ConstraintVertexAny } from "@typedb/driver-http";
import { StructuredAnswer, DataConstraintAny, DataVertex,
    DataConstraintIsa, DataConstraintIsaExact, DataConstraintHas, DataConstraintLinks,
    DataConstraintSub, DataConstraintSubExact, DataConstraintOwns, DataConstraintRelates, DataConstraintPlays,
    DataConstraintExpression, DataConstraintFunction, DataConstraintKind,
    DataConstraintComparison, DataConstraintIs, DataConstraintIid, DataConstraintLabel, DataConstraintValue,
} from "./structured-answers";

/**
 * Abstract base class for building a graph from structured TypeDB answers.
 * Extend this class and implement the abstract methods to handle each constraint type.
 * Call `build(answers)` to process a set of structured answers.
 */
export abstract class AbstractGraphBuilder {

    build(answers: StructuredAnswer[]): void {
        answers.forEach((answer, answerIndex) => {
            answer.constraints.forEach(constraint => {
                this.putConstraint(answerIndex, constraint);
            });
        });
    }

    private putConstraint(answerIndex: number, constraint: DataConstraintAny): void {
        switch (constraint.tag) {
            case "isa": {
                this.isa(answerIndex, constraint);
                break;
            }
            case "isa!": {
                this.isaExact(answerIndex, constraint);
                break;
            }
            case "has": {
                this.has(answerIndex, constraint);
                break;
            }
            case "links": {
                this.links(answerIndex, constraint);
                break;
            }
            case "sub": {
                this.sub(answerIndex, constraint);
                break;
            }
            case "sub!": {
                this.subExact(answerIndex, constraint);
                break;
            }
            case "owns": {
                this.owns(answerIndex, constraint);
                break;
            }
            case "relates": {
                this.relates(answerIndex, constraint);
                break;
            }
            case "plays": {
                this.plays(answerIndex, constraint);
                break;
            }
            case "expression": {
                this.expression(answerIndex, constraint);
                break;
            }
            case "function": {
                this.function(answerIndex, constraint);
                break;
            }
            case "kind": {
                this.kind(answerIndex, constraint);
                break;
            }
            case "comparison": {
                this.comparison(answerIndex, constraint);
                break;
            }
            case "is": {
                this.is(answerIndex, constraint);
                break;
            }
            case "iid": {
                this.iid(answerIndex, constraint);
                break;
            }
            case "label": {
                this.label(answerIndex, constraint);
                break;
            }
            case "value": {
                this.value(answerIndex, constraint);
                break;
            }
        }
    }

    // Vertices
    abstract vertex(answerIndex: number, vertex: DataVertex, queryVertex: ConstraintVertexAny): void;

    // Edges
    abstract isa(answerIndex: number, constraint: DataConstraintIsa): void;
    abstract isaExact(answerIndex: number, constraint: DataConstraintIsaExact): void;
    abstract has(answerIndex: number, constraint: DataConstraintHas): void;
    abstract links(answerIndex: number, constraint: DataConstraintLinks): void;
    abstract sub(answerIndex: number, constraint: DataConstraintSub): void;
    abstract subExact(answerIndex: number, constraint: DataConstraintSubExact): void;
    abstract owns(answerIndex: number, constraint: DataConstraintOwns): void;
    abstract relates(answerIndex: number, constraint: DataConstraintRelates): void;
    abstract plays(answerIndex: number, constraint: DataConstraintPlays): void;
    abstract expression(answerIndex: number, constraint: DataConstraintExpression): void;
    abstract function(answerIndex: number, constraint: DataConstraintFunction): void;
    abstract kind(answerIndex: number, constraint: DataConstraintKind): void;
    abstract comparison(answerIndex: number, constraint: DataConstraintComparison): void;
    abstract is(answerIndex: number, constraint: DataConstraintIs): void;
    abstract iid(answerIndex: number, constraint: DataConstraintIid): void;
    abstract label(answerIndex: number, constraint: DataConstraintLabel): void;
    abstract value(answerIndex: number, constraint: DataConstraintValue): void;
}
