# Neo4j

https://neo4j.com/docs/getting-started/

[Course: Neo4j Fundamentals](https://graphacademy.neo4j.com/courses/neo4j-fundamentals/)

[Neo4j GQL conformance](https://neo4j.com/docs/cypher-manual/current/appendix/gql-conformance/)

Attend Conference on November 7, 2024

https://neo4j.com/nodes2024/agenda/

Courses:

https://graphacademy.neo4j.com/courses/neo4j-fundamentals/

https://graphacademy.neo4j.com/courses/cypher-fundamentals/

## Cypher Query Language for Graph Database

https://neo4j.com/docs/cypher-manual/current/introduction/

Neo4j is transitioning its Cypher query language to be fully compliant with the new GQL (Graph Query Language) standard. Here’s a breakdown of what this means:

1. **GQL Standardization**: GQL has recently become an ISO standard, marking a significant milestone for graph databases¹. This standardization aims to unify various graph query languages, much like SQL did for relational databases.

2. **Cypher's Evolution**: Cypher, originally developed by Neo4j, has been a leading property graph query language. With the advent of GQL, Neo4j is evolving Cypher to align with GQL standards¹². This means that Cypher will incorporate GQL's features and improvements while maintaining its core syntax and functionality.

3. **Smooth Transition**: Neo4j is committed to making this transition as seamless as possible for its users. Instead of introducing a completely new language, Neo4j will adapt Cypher to be GQL-compliant¹. This approach ensures that existing Cypher queries will continue to work, but with added benefits from GQL's enhancements.

4. **Benefits of GQL**: GQL builds on Cypher’s strengths and introduces improvements to better align with SQL and ensure long-term viability. This includes more robust query capabilities and better integration with other database systems¹².

In summary, Neo4j's adoption of GQL means that Cypher will become even more powerful and standardized, benefiting from the collective advancements in graph query languages. If you have any specific questions about this transition, feel free to ask!

Source: Conversation with Copilot, 10/7/2024
(1) GQL is Here: Your Cypher Queries in a GQL World - Neo4j Graph Data Platform. https://neo4j.com/blog/cypher-gql-world/.
(2) openCypher Will Pave the Road to GQL for Cypher Implementers. https://neo4j.com/blog/opencypher-gql-cypher-implementation/.
(3) Cypher developed database. GQL becomes an international standard .... https://community.neo4j.com/t/cypher-developed-database-gql-becomes-an-international-standard-whether-cypher-automatically-switches-to-gql-whether-database-needs-to-be-redeveloped-with-gql/61668.
(4) GQL: The ISO Standard for Graphs Has Arrived. https://neo4j.com/blog/cypher-path-gql/.


## Important Note:

For us the most important thing is the support of Graph Schema's in the database like this example:

### Creating a Graph
To create a new graph, you can define the graph schema and then instantiate it. For example:

```gql
CREATE GRAPH TYPE socialNetworkSchema (
  Person (name STRING, age INT),
  Friend (since DATE)
);

CREATE GRAPH socialNetwork OF TYPE socialNetworkSchema;
```ok