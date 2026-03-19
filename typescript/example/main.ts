export { TypeDBHttpDriver, isOkResponse, ConceptRowsQueryResponse } from "@typedb/driver-http";

import {ConceptRowsQueryResponse } from "@typedb/driver-http";
import { buildStructuredAnswers, StructuredAnswer } from "@typedb/graph-utils";
import { SigmaConverter } from "./sigmajs-converter";
import { MultiGraph } from "graphology";
import Sigma from "sigma";
import forceAtlas2 from "graphology-layout-forceatlas2";

export function initialise(graphContainer: HTMLElement): SigmaJSExample {
    return new SigmaJSExample(graphContainer);
}

export class SigmaJSExample {
    private readonly sigma: Sigma;

    constructor(graphContainer: HTMLElement) {
        this.sigma = new Sigma(new MultiGraph(), graphContainer, {
            renderEdgeLabels: true,
        });
    }

    public buildStructuredAnswers(response: ConceptRowsQueryResponse) {
        return buildStructuredAnswers(response);
    }

    public updateGraph(structuredAnswers: StructuredAnswer[]) {
        const graph = new MultiGraph();
        // In this case, the graph gets updated by build.
        new SigmaConverter(graph).build(structuredAnswers);
        const settings = forceAtlas2.inferSettings(graph);
        forceAtlas2.assign(graph, { iterations: 50, settings });
        this.sigma.setGraph(graph);
        // this.sigma.refresh();
    }
}
