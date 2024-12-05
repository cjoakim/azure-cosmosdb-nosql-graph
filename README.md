# azure-cosmosdb-nosql-graph

A demonstration of how to use the **Cosmos DB NoSQL API for Graph Workoads**.

The code implementation in this repo is in **Python**, but the concepts
are langage-neutral.

# Graph Workload Best Practices with the Cosmos DB NoSQL API

- Minimize the number of Cosmos DB containers; it's not relational
- Generally use a Single Container Design
- Store dissimilar documents in the same container
  - Differentiate these with a 'doctype' attribute or similar attribute
  - For example: 'order', 'line_item', 'delivery' for an eCommerce app
- Group related documents in the same logical partition for efficiency/costs
- Use the "Aggregation Pipeline" pattern instead of a graph query syntax
  - Each stage of the pipeline uses the results of the previous stage
  - Implement your pipelines as separate Python/Java/C# classes
    - Instances of these classes execute the pipeline
    - See class "PythonDependencyGraph" (file xxx) in this repo
  - This logic can use fast and efficient Cosmos DB point-reads
  - See https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
- Converting from a LPG "Vertices and Edges" model
  - "Fold" the edges into the source vertex as an array of edges
- Use materialized view documents to optimize common queries
  - This "materializes" complex query results into a cached document for reuse

## Requirements for using this code

- Laptop/workstation with the git program
  - See https://git-scm.com/

- Laptop/workstation with stardard Python 3
  - Not Python 2
  - Not a packaged version like Conda 
  - See https://www.python.org/downloads/

- Azure Subscription with Cosmos DB NoSQL Account

- Environment Variables pointing to your Cosmos DB NoSQL Account
  - Alternatively, edit the **.env** file in the python directory
  - See https://pypi.org/project/python-dotenv/
  - See file dotenv_example in the python directory of this repo

- A text editor such as Visual Studio Code
  - See https://code.visualstudio.com/

```

```


## Quick Start

Execute the following commands in Windows 11 PowerShell,
or the equivalent in macOS or Linux Terminal.

```
> cd xxx               # where xxx is some parent directory on your computer

> git clone https://github.com/cjoakim/azure-cosmosdb-nosql-graph.git

> cd azure-cosmosdb-nosql-graph

> cd data              # then unzip the python_libs.zip file

> cd ..

> cd python            # you'll spend most of your time in this directory

> .\venv.ps1           # create the python virtual environment

> .\venv\Scripts\Activate.ps1   # activate the python virtual environment

> pip list             # list the libraries in your python virtual environment
                       # The output should be verbose and look like the following:

Package            Version
------------------ -----------
aiohappyeyeballs   2.4.4
aiohttp            3.11.9
aiosignal          1.3.1
attrs              24.2.0
azure-core         1.32.0
azure-cosmos       4.9.0
azure-identity     1.19.0
black              24.10.0
...                          # many lines of output omitted here
urllib3            2.2.3
wheel              0.45.1
yarl               1.18.3


```