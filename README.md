# azure-cosmosdb-nosql-graph

A demonstration of how to use the **Cosmos DB NoSQL API for Graph Workoads**.

The code implementation in this repo is in **Python** but the 
concepts and design are language-neutral.

A **Node.js/TypeScript** implementation may be added at a later date.

---

## Graph Workload Best Practices with the Cosmos DB NoSQL API

- Minimize the number of Cosmos DB containers; it's not a relational database
- Generally use a Single Container Design for the graph
- Store dissimilar documents in the same container
  - Differentiate these with a 'doctype' attribute or similar attribute
  - For example: 'order', 'line_item', 'delivery' for an eCommerce app
- Group related documents in the same logical partition for efficiency/costs
- Use the "Aggregation Pipeline" pattern instead of a graph query syntax
  - Each stage of the pipeline uses the results of the previous stage
  - Implement your pipelines as separate Python/Java/C# classes
    - Instances of these classes execute the pipeline
    - See example class "DependencyGraph" (file python/src/dao/dependency_graph.py)
  - This logic can use fast and efficient Cosmos DB point-reads
  - See https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
- Converting from a LPG "Vertices and Edges" model
  - "Fold" the outgoing edges into the source vertex as an array of edges
  - Include the id and partition key "coordinates" of the associated vertex
- Use materialized view documents to optimize common queries
  - This "materializes" complex query results into a cached document for reuse

---

## Example Graphs

- [Python Libraries](README_PYLIBRARIES.md)
  - This uses the [CosmosAIGraph dataset](https://github.com/AzureCosmosDB/CosmosAIGraph)
- [IoT Devices](README_DEVICES.md)
