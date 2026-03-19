import { describe, it, before } from "node:test";
import assert from "node:assert/strict";
import {
    TypeDBHttpDriver,
    isOkResponse,
    ConceptRowsQueryResponse,
    QueryResponse,
    ApiResponse,
} from "@typedb/driver-http";
import { buildStructuredAnswers } from "@typedb/graph-utils";
import { SigmaConverter } from "../sigmajs-converter";
import { MultiGraph } from "graphology";

const DB_ADDRESS = "http://127.0.0.1:8000";
const DB_CREDENTIALS = { username: "admin", password: "password" };
const DB_NAME = "typedb-graph-tutorial-ts";

function createDriver(): TypeDBHttpDriver {
    return new TypeDBHttpDriver({
        ...DB_CREDENTIALS,
        addresses: [DB_ADDRESS],
    });
}

async function setup(driver: TypeDBHttpDriver, schema: string, data: string) {
    // Delete if exists
    const dbsResp = await driver.getDatabases();
    if (isOkResponse(dbsResp)) {
        if (dbsResp.ok.databases.some(db => db.name === DB_NAME)) {
            await driver.deleteDatabase(DB_NAME);
        }
    }

    // Create database
    const createResp = await driver.createDatabase(DB_NAME);
    assert(isOkResponse(createResp), "Failed to create database");

    // Load schema
    const schemaResp = await driver.oneShotQuery(schema, true, DB_NAME, "schema");
    assert(isOkResponse(schemaResp), `Failed to load schema: ${JSON.stringify(schemaResp)}`);

    // Load data
    const dataResp = await driver.oneShotQuery(data, true, DB_NAME, "write");
    assert(isOkResponse(dataResp), `Failed to load data: ${JSON.stringify(dataResp)}`);
}

async function runQuery(driver: TypeDBHttpDriver, query: string): Promise<ConceptRowsQueryResponse> {
    const resp: ApiResponse<QueryResponse> = await driver.oneShotQuery(
        query, false, DB_NAME, "read",
        undefined,
        { includeQueryStructure: true },
    );
    assert(isOkResponse(resp), `Query failed: ${JSON.stringify(resp)}`);
    const body = resp.ok;
    assert.equal(body.answerType, "conceptRows", "Expected conceptRows answer type");
    return body as ConceptRowsQueryResponse;
}

function buildGraph(response: ConceptRowsQueryResponse): MultiGraph {
    const structuredAnswers = buildStructuredAnswers(response);
    const graph = new MultiGraph();
    new SigmaConverter(graph).build(structuredAnswers);
    return graph;
}

describe("friendships", () => {
    const driver = createDriver();

    const SCHEMA = `
    define
      attribute name value string;
      relation friendship, relates friend @card(2);
      entity person, plays friendship:friend, owns name @key;
    `;

    const DATA = `
    insert
      $john isa person, has name "John";
      $james isa person, has name "James";
      $jeff isa person, has name "Jeff";
      $f12 isa friendship, links (friend: $john, friend: $james);
      $f23 isa friendship, links (friend: $james, friend: $jeff);
      $f31 isa friendship, links (friend: $jeff, friend: $john);
    `;

    const QUERY = `
    match
      $f isa friendship, links (friend: $p1, friend: $p2);
      $p1 has name $n1;
      $p2 has name $n2;
      $n1 < $n2;
    `;

    before(async () => {
        await setup(driver, SCHEMA, DATA);
    });

    it("returns 3 answers", async () => {
        const response = await runQuery(driver, QUERY);
        assert.equal(response.answers.length, 3, "TypeDB answer count mismatch");
    });

    it("has query structure", async () => {
        const response = await runQuery(driver, QUERY);
        assert(response.query != null, "TypeDB no query structure");
    });
    it("builds graph with 9 nodes and 11 edges", async () => {
        const response = await runQuery(driver, QUERY);
        const graph = buildGraph(response);
        assert.equal(graph.order, 9, "node count mismatch");
        assert.equal(graph.size, 11, "edge count mismatch");
    });
});

describe("expression_disjunction", () => {
    const driver = createDriver();

    const QUERY = `
    match
      { let $y = 3; } or { let $y = 5; };
      { let $x = 2 + $y; } or { let $x = 2 * $y; };
    `;

    it("returns 4 answers", async () => {
        const response = await runQuery(driver, QUERY);
        assert.equal(response.answers.length, 4, "TypeDB answer count mismatch");
    });

    it("has query structure", async () => {
        const response = await runQuery(driver, QUERY);
        assert(response.query != null, "TypeDB no query structure");
    });

    it("builds graph with 11 nodes and 10 edges", async () => {
        const response = await runQuery(driver, QUERY);
        const graph = buildGraph(response);

        // 2 + 4 expression nodes, 4 values for x + 2 values for y (value 5 is shared)
        assert.equal(graph.order, 11, "node count mismatch");
        assert.equal(graph.size, 10, "edge count mismatch");
    });
});
