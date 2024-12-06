# azure-cosmosdb-nosql-graph

A demonstration of how to use the **Cosmos DB NoSQL API for Graph Workoads**.

The code implementation in this repo is in **Python**, but the concepts
are language-neutral.

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

## Sample Documents

A dataset is provided in this GitHub repo, see file **data/python_libs.zip**.
Unzip the file so that file **data/python_libs.json** resides in the same
directory.  This file contains ~10k documents relating to Python
libraries at https://pypi.org/.  This dataset forms a nice graph as
libraries have zero-to-many dependencies on other libraries.

The following is the document for the python library named "flask".
The "id" value is the **unique** library name, and the "pk" value 
(container partition key) is the first letter of the name.

This partition key value was chosen for demonstration purposes only,
so as to have ~26 logical partitions.  The partition key
this was set in the load program; it's not in the python_libs.json
file.

```
{
    "name": "flask",
    "id": "flask",
    "pk": "f",
    "dependency_ids": [
        "asgiref",
        "blinker",
        "click",
        "importlib_metadata",
        "itsdangerous",
        "jinja2",
        "python_dotenv",
        "werkzeug"
    ],
    "package_url": "https://pypi.org/project/Flask/",
    "summary": "a simple framework for building complex web applications.",
    "kwds": "flask wsgi _wsgi python pip",
    "version": "3.0.0",
    "release_count": 57,
    "developers": [
        "contact@palletsprojects.com"
    ],
    "_rid": "YuM7AKoikvrhDAAAAAAAAA==",
    "_self": "dbs/YuM7AA==/colls/YuM7AKoikvo=/docs/YuM7AKoikvrhDAAAAAAAAA==/",
    "_etag": "\"0700eb52-0000-0300-0000-6752e4c10000\"",
    "_attachments": "attachments/",
    "_ts": 1733485761
}
```

Array attribute **dependency_ids** contains the list of libraries
that flask uses, or depends on.  In a **LPG (Labeled Property Graph)**
graph database these dependency **relationships** would be implemented
as **edges** that connect the **vertices**.  In this example **flask**, 
**click**, and **jinja2** are vertices, or entities in the graph.

Thus, this example document implements the above Cosmos DB NoSQL
graph best-practice of "folding" the outgoing edges into the source vertex
as an array of edges.

The following is the document for the **jinja2*** python library,
which flask depends on.  Notice how the dependency_ids do not
include flask.  This is because flask is an incoming edge, not an
outgoing edge.

```
{
    "name": "jinja2",
    "id": "jinja2",
    "pk": "j",
    "dependency_ids": [
        "babel",
        "markupsafe"
    ],
    "package_url": "https://pypi.org/project/Jinja2/",
    "summary": "a very fast and expressive template engine.",
    "kwds": "jinja jinja2 templates templating template",
    "version": "3.1.2",
    "release_count": 48,
    "developers": [
        "armin.ronacher@active-4.com",
        "armin_ronacher",
        "contact@palletsprojects.com",
        "pallets"
    ],
    "_rid": "YuM7AKoikvqeEAAAAAAAAA==",
    "_self": "dbs/YuM7AA==/colls/YuM7AKoikvo=/docs/YuM7AKoikvqeEAAAAAAAAA==/",
    "_etag": "\"0700e256-0000-0300-0000-6752e4d50000\"",
    "_attachments": "attachments/",
    "_ts": 1733485781
}
```

Lastly, note that the Cosmos DB documents contain several system-generated
attribute names that begin with an underscore.  **_ts** is the epoch timestamp
of the last modification, and **_etag** is a version value used in 
Optimistic Concurrency Control (OCC).

---

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