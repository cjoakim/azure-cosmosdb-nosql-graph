# azure-cosmosdb-nosql-graph

A demonstration of how to use the **Cosmos DB NoSQL API for Graph Workoads**.

The code implementation in this repo is in **Python** but the 
concepts and design are language-neutral.

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

## Sample Documents

A dataset is provided in this GitHub repo, see file **data/python_libs.zip**.
Unzip the file so that file **data/python_libs.json** resides in the same
directory.  This file contains ~10k documents relating to Python
libraries at https://pypi.org/.  This dataset forms a nice graph as
libraries have zero-to-many dependencies on other libraries.

The following is the document for the python library named "flask".
The **"id"** value is the **unique** library name, and the **"pk"** value 
(container partition key) is the first letter of the name.
This partition key value was chosen for demonstration purposes only,
so as to have a non-trivial number (~26) of logical partitions.

```
{
    "doctype": "library",
    "name": "flask",
    "id": "flask",
    "pk": "f",
    "dependencies": [
        {
            "id": "asgiref",
            "pk": "a",
            "doctype": "library"
        },
        {
            "id": "blinker",
            "pk": "b",
            "doctype": "library"
        },
        {
            "id": "click",
            "pk": "c",
            "doctype": "library"
        },
        {
            "id": "importlib_metadata",
            "pk": "i",
            "doctype": "library"
        },
        {
            "id": "itsdangerous",
            "pk": "i",
            "doctype": "library"
        },
        {
            "id": "jinja2",
            "pk": "j",
            "doctype": "library"
        },
        {
            "id": "python_dotenv",
            "pk": "p",
            "doctype": "library"
        },
        {
            "id": "werkzeug",
            "pk": "w",
            "doctype": "library"
        }
    ],
    "package_url": "https://pypi.org/project/Flask/",
    "summary": "a simple framework for building complex web applications.",
    "kwds": "flask wsgi _wsgi python pip",
    "version": "3.0.0",
    "release_count": 57,
    "developers": [
        "contact@palletsprojects.com"
    ],
    "_rid": "YuM7AMfcPP7hDAAAAAAAAA==",
    "_self": "dbs/YuM7AA==/colls/YuM7AMfcPP4=/docs/YuM7AMfcPP7hDAAAAAAAAA==/",
    "_etag": "\"4c01985f-0000-0300-0000-6752fa400000\"",
    "_attachments": "attachments/",
    "_ts": 1733491264
}
```

Array attribute **dependencies** contains the list of libraries
that flask uses, or depends on.  In a **LPG (Labeled Property Graph)**
graph database these dependency **relationships** would be implemented
as separate **edges** that connect the **vertices**.

However, in this Cosmos DB design, the edges are embedded into the
source vertex as an array.  The edges contain the id and partition key
"coordinates" of the target vertex that enable them to be read efficiently
with Cosmos DB **print-reads** when traversing the graph.

Thus, this example document implements the above Cosmos DB NoSQL
graph best-practice of "folding" the outgoing edges into the source
vertex as an array of edges.

In your application, you may wish to augment the edge objects with
attributes per your query patterns.

The following is the document for the **jinja2*** python library,
which flask depends on.  Notice how the dependencies do not
include flask.  This is because flask is an incoming edge, not an
outgoing edge.

```
{
    "doctype": "library",
    "name": "jinja2",
    "id": "jinja2",
    "pk": "j",
    "dependencies": [
        {
            "id": "babel",
            "pk": "b",
            "doctype": "library"
        },
        {
            "id": "markupsafe",
            "pk": "m",
            "doctype": "library"
        }
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
    "_rid": "YuM7AMfcPP6eEAAAAAAAAA==",
    "_self": "dbs/YuM7AA==/colls/YuM7AMfcPP4=/docs/YuM7AMfcPP6eEAAAAAAAAA==/",
    "_etag": "\"4c011664-0000-0300-0000-6752fa530000\"",
    "_attachments": "attachments/",
    "_ts": 1733491283
}
```

A variant of this design is to embed both the outgoing and incoming
edges within a vertex document for bi-directional traversals.

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

- A text editor such as Visual Studio Code
  - See https://code.visualstudio.com/

- Environment Variables pointing to your Cosmos DB NoSQL Account
  - The list of environment variables is shown below
  - See file **dotenv_example** in the python directory for sample values
  - Alternatively, edit the **.env** file in the python directory
      - Copy file to dotenv_example to .env, then edit .env
      - See https://pypi.org/project/python-dotenv/

```
    COSMOSDB_NOSQL_AUTH_MECHANISM
    COSMOSDB_NOSQL_URI
    COSMOSDB_NOSQL_KEY
    COSMOSDB_NOSQL_DB
    COSMOSDB_NOSQL_CONTAINER
    LOG_LEVEL
```

---

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

### Provision and Configure Cosmos DB

- Create a NoSQL account
- Create a database named **graph**
- Create a container in the database also named **graph**
  - Specify the partition key value /pk
  - 4000 Request Units, autoscale, is adequate for this example
- Also create a container in the database also named **test**
  - Specify the partition key value /pk
  - 4000 Request Units, autoscale, is adequate
- Set the above environment variables to point to your account, database, and container

### Run the main.py program to see its' command-line options

```
> .\venv\Scripts\Activate.ps1

> python main.py

Usage:
    python main.py print_defined_environment_variables
    python main.py test_cosmos_service <dbname> <cname> <optional-flags>
    python main.py test_cosmos_service graph test
    python main.py test_cosmos_service graph test --bulk-load
    python main.py load_python_libraries_graph <dbname> <cname> <max_docs>
    python main.py load_python_libraries_graph graph graph 999999 --bulk-load
    python main.py count_documents <dbname> <cname>
    python main.py point_read <dbname> <cname> <doc_id> <pk>
    python main.py point_read graph graph flask f
    python main.py query <dbname> <cname>
    python main.py query graph graph
    python main.py traverse_dependencies <dbname> <cname> <libname> <depth>
    python main.py traverse_dependencies graph graph flask 1
    python main.py traverse_dependencies graph graph flask 3
Options:
  -h --help     Show this screen.
  --version     Show version.
```

This output is intended for copy-and-paste use.

### Check access to Cosmos DB with Python

To check connectivity, before you load the graph container,
execute the following commands, in the python\ directory, 
which will do various CRUD operations to the **test** container.

```
> .\venv\Scripts\Activate.ps1

> python main.py print_defined_environment_variables
```

If the displayed environment variables look correct, per your
Cosmos DB account, then run the following.
If not, then correct your environment variables.

```
> python main.py test_cosmos_service graph test --bulk-load
```

You'll see some verbose output.  Then see your Cosmos DB account
in Azure Portal and verify that several documents are present
in the test container.

### Bulk Load the Libraries dataset 

Run the following command from the python\ directory:

```
> python main.py load_python_libraries_graph graph graph 999999 --bulk-load
```

### Execute Queries and Traversals

Finally, now that the data is loaded into your Cosmos DB container,
we can query and traverse it with the following examples.


