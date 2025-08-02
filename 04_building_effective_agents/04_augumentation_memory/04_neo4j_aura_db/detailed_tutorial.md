# Building Knowledge Graphs with Neo4j AuraDB: A Comprehensive Tutorial

Neo4j AuraDB is Neo4j’s fully managed cloud graph database service. It provides a reliable, secure, and automated platform for building graph-based applications without worrying about database administration. In this tutorial, we will walk through the entire process of building a simple **knowledge graph** (using a social network example) on Neo4j AuraDB. We’ll cover everything from setting up your AuraDB instance, to querying it with the Cypher graph query language (using **Cypher 25**, Neo4j’s latest query language version), and interacting via Python code. This guide is beginner-friendly and includes step-by-step instructions, code examples (in Jupyter Notebook style), and best practices for developing a knowledge graph.

## 1. Setting Up Neo4j AuraDB

Before we can build our knowledge graph, we need to create a Neo4j AuraDB instance and connect to it.

### 1.1 Creating a Neo4j AuraDB Account and Instance

**Sign Up for AuraDB:** If you don’t have an AuraDB account, start by navigating to the Neo4j Aura console at **console.neo4j.io** and create an account (you can sign up with an email or Google account). The Aura console is the web interface where you manage your Neo4j databases (instances).

**Create a New AuraDB Instance:** Once logged in to the Aura console, create a new database instance (Aura calls each database an "instance"). For a beginner project, you can choose the free tier:

1. Click **“New Instance”** in the Aura console.
2. Select **“Create Free Instance”** (if prompted). AuraDB Free provides a fully managed Neo4j instance at no cost.
3. Provide a name for your instance (e.g., “MyKnowledgeGraph”), and choose the **Neo4j version** (use the latest available, Neo4j 5.x, which supports Cypher 25).
4. Aura will create the instance. **Copy and save the auto-generated username and password** for the instance when prompted (you can download the credentials as a TXT file). *You will need these credentials to connect to the database!*
5. Confirm the creation by checking the acknowledgement box and clicking **Continue**.

**Note:** You can only have one free instance per account, and AuraDB Free instances have some limitations (e.g. max \~200k nodes and \~400k relationships). Free instances are paused automatically after 72 hours of inactivity to save resources, and if left paused for over 30 days they are deleted (all data is lost). Be sure to resume activity or upgrade if you plan to keep your data longer-term.

### 1.2 Connecting to Your AuraDB Instance

Once your AuraDB instance is running (status should show as **Active** in the console), you can connect to it in a few ways:

* **Neo4j AuraDB “Workspace” (Web Interface):** On the Aura console, click the **“Open”** button next to your instance. This launches Neo4j Workspace in your browser, which combines the Neo4j Browser query interface and other tools. Enter the database **username and password** you saved earlier when prompted, and click **Connect**. The Workspace lets you run Cypher queries in your browser and visualize the graph, which is great for interactive exploration.

* **Connection URI:** In the Aura console’s instance details, you will see a **Connection URI** (under instance status). It will look something like:

  ```
  neo4j+s://<your-instance-id>.databases.neo4j.io
  ```

  This is a **Bolt protocol URI** (the `neo4j+s://` scheme indicates a secure connection to Neo4j). You can use this URI along with your credentials to connect via Neo4j Desktop, Cypher Shell, or programming languages. For example:

  * **Neo4j Desktop:** Copy the URI, open Neo4j Desktop, and add a new Remote Graph connection using that URI. Enter the username/password when prompted and connect.
  * **Cypher Shell (CLI):** Install the Neo4j Cypher Shell tool, then run a command:

    ```bash
    cypher-shell -a <bolt-uri> -u <username> -p <password>
    ```

    For Aura, that would be: `cypher-shell -a neo4j+s://... -u neo4j -p <yourPassword>`. Once connected, you can run Cypher commands in the shell.

In this tutorial, we will primarily focus on using the **Neo4j Python Driver** to connect and run queries from a Python environment, since our goal is to integrate Cypher and Python.

### 1.3 Instance Management Basics (Pause, Resume, Delete)

Neo4j AuraDB provides a few instance management actions accessible from the Aura console (via the “...’’ menu or buttons on your instance card):

* **Pause/Resume:** For paid tiers (Professional/Enterprise), you can manually pause an instance to suspend computation (billing is reduced while paused) and resume it later. *AuraDB Free instances cannot be manually paused* – they auto-pause after 72h inactivity as mentioned.
* **Clone:** You can clone an instance to create a copy of your database (useful for creating a development vs. production copy, testing upgrades, etc.). Cloning can be done to a new instance or overwrite an existing one (be careful – cloning into an existing instance will replace its data).
* **Delete:** If you no longer need an instance, you can delete it (trashcan icon in console). You’ll be asked to confirm by typing the instance name, and then **Destroy** it. *Warning:* This is irreversible – all data is lost once an instance is deleted.

For this tutorial, a pause or delete might not be needed until you finish experimenting. Just be aware of these actions as you manage your AuraDB instance.

## 2. Introduction to Cypher and the Graph Data Model

Before building our knowledge graph, let’s quickly introduce **Cypher**, the query language we’ll use to create and query data in Neo4j, and the underlying graph data model concepts.

**Cypher Query Language:** Cypher is Neo4j’s declarative query language for graphs. It is often described as “SQL for graphs” – if you’re familiar with SQL, Cypher’s syntax and structure will feel somewhat similar, but it's optimized for traversing and matching patterns in graph data. Cypher uses a very intuitive ASCII-art syntax to represent graph patterns. For example, a pattern `(a:Person)-[:KNOWS]->(b:Person)` visually depicts two nodes of label `Person` with a relationship `KNOWS` going from `a` to `b`. The language is designed to be easy to read and write, almost like describing relationships in natural English.

**Graph Data Model:** In Neo4j (and graph databases in general), data is stored as a network of **nodes** and **relationships**:

* **Nodes:** Nodes represent entities or objects (like a person, place, thing, concept, etc.). Nodes can have one or more **labels** to categorize their type. For example, a node representing a person might have the label `Person`, and a company might have label `Company`. Labels in Neo4j act like tags or schema types that group nodes, helping to optimize queries and make the data model clear. Each node can also have **properties** – key-value pairs storing information (like `name`, `age`, etc.).
* **Relationships:** Relationships connect two nodes and represent the relationship or association between them (for example, `:FRIENDS_WITH`, `:WORKS_FOR`, `:LIKES`). A relationship always has a **type** (a name, conventionally written in all-caps) and a direction (source -> target). You can think of relationship types as verbs that link node entities (which are like nouns). In Cypher syntax, relationships are depicted with `-[]->` arrows between nodes. For instance, `(p:Person)-[:FRIENDS_WITH]->(q:Person)` means p “FRIENDS\_WITH” q (p is friends with q). Every relationship must have a direction when stored, but you can query without specifying direction if needed (an undirected match will find relationships in either direction). Relationships can also hold properties (e.g., a `FRIENDS_WITH` relationship could have a property `since: 2015` to indicate when the friendship began).
* **Properties:** Both nodes and relationships can have properties. These are like attributes — for example, a `Person` node might have properties `name="Alice"` and `age=30`, while a `FRIENDS_WITH` relationship might have `since="2015"`. Properties are specified in Cypher using curly braces `{...}`. For example: `(:Person {name: "Alice", age: 30})` creates a Person node with those properties.

&#x20;*Visual representation of a simple knowledge graph example. Here, a Person node "Sally" is connected to a Technology node "Graphs" by a **LIKES** relationship, to another Person "John" by an **IS\_FRIENDS\_WITH** relationship, and to a Company node "Neo4j" by a **WORKS\_FOR** relationship. Each arrow’s label indicates the relationship type.*

In the above figure, we have an example graph with four nodes and three relationships (this is similar to an example from Neo4j’s tutorial guides). If we describe it in words: *"Sally likes Graphs, Sally is friends with John, and Sally works for Neo4j."* We could represent that in Cypher (conceptually) as:

```cypher
(:Person {name:"Sally"})-[:LIKES]->(:Technology {type:"Graphs"}),
(:Person {name:"Sally"})-[:IS_FRIENDS_WITH]->(:Person {name:"John"}),
(:Person {name:"Sally"})-[:WORKS_FOR]->(:Company {name:"Neo4j"})
```

Each `()` is a node (with label and properties), and each `[:TYPE]` is a relationship. Notice how this pattern syntax closely mirrors the natural language description of the facts – Cypher makes it easy to express connections in data.

**Cypher 25:** Neo4j continually updates Cypher with new features. “Cypher 25” refers to the latest version of the Cypher language (as of Neo4j 5.x and the year 2025). Your AuraDB instance is always kept up-to-date, so you have access to the newest Cypher features by default. (If needed, you can even enforce that a query uses Cypher 25 by prepending `CYPHER 25` at the start of your query, but this usually isn’t required when using the default database settings on Neo4j 5+.)

### 2.1 Data Modeling for Our Example (Social Network Graph)

In our tutorial, we will use a **social network** style data model for the knowledge graph:

* We will create nodes with label **`Person`** to represent individuals in the social network. Each Person node will have at least a `name` property (and potentially other properties like age, etc., which we can add later).
* We will connect Person nodes with **`KNOWS`** relationships to indicate friendships or acquaintances. For example, if Alice knows (is friends with) Bob, we will have `(Alice)-[:KNOWS]->(Bob)` in the graph.
* To enrich the graph, we can also introduce other node types and relationships. For instance, we might have `Interest` nodes (like topics or hobbies) and relationships like `(:Person)-[:LIKES]->(:Interest)`. Or company nodes with `(:Person)-[:WORKS_FOR]->(:Company)`. These mirror the kinds of relationships we saw with Sally in the example (liking “Graphs” and working for “Neo4j”). For simplicity, our initial focus will be on people and the KNOWS relationships between them, but you can expand a knowledge graph by adding more entity types and relationship types as needed.

**Why a Graph?** A social network is naturally modeled as a graph: people are connected to other people (forming a network of friendships). Graph databases excel at this because you can easily query for patterns like “friends of friends” or common connections. We will see examples of such queries in the next section.

## 3. Inserting Data: Building the Knowledge Graph

With our AuraDB instance running and an understanding of the model, it’s time to insert some data. We will demonstrate two ways to create data: (a) using Cypher statements directly (e.g. via the Neo4j browser), and (b) using the Neo4j Python driver in code. In practice, you might use either or both (for example, quick manual insertions via the browser, and bulk or dynamic insertions via an application script).

### 3.1 Creating Nodes and Relationships with Cypher (Neo4j Browser)

If you open your AuraDB instance in the Neo4j browser (Workspace) interface, you can run Cypher commands to insert data. Let’s create a small set of Person nodes and KNOWS relationships for our social network:

```cypher
// Create two Person nodes, Alice and David, and a KNOWS relationship between them
CREATE (alice:Person {name: "Alice", age: 25});
CREATE (david:Person {name: "David", age: 24});
CREATE (alice)-[:KNOWS]->(david);
```

The above three `CREATE` commands will add two nodes labeled `Person` (with name and age properties) and a relationship `KNOWS` from Alice to David. In Neo4j Browser, you can highlight all three lines and run them together, or run one at a time. After running, the browser will typically display a visual graph of what was created. You should see two circles (nodes) labeled “Person” with their name properties, and an arrow labeled “KNOWS” from Alice to David.

**Important:** In Cypher, semicolons are optional when running one query at a time in the browser. If you put multiple commands together as shown above, the browser will treat it as a single script. You could also combine node creation and relationship creation in a single Cypher statement using variables, for example:

```cypher
CREATE (alice:Person {name: "Alice", age: 25})-[:KNOWS]->(david:Person {name: "David", age: 24});
```

This one-liner does the same as the earlier three lines, by creating the pattern of two connected nodes in one go. Both approaches are fine; use whichever is clearer to you.

*Best Practice:* Usually, you’ll want some unique identifier for nodes (rather than names alone) to avoid duplicates. For learning purposes, we just use the `name` property. In a real app, you might enforce uniqueness with a constraint (e.g., ensure `Person.name` is unique) so you don’t accidentally create two “Alice” nodes. For example, you could run `CREATE CONSTRAINT FOR (p:Person) REQUIRE p.name IS UNIQUE` to make the database reject any new Person with a name that already exists. (Creating a uniqueness constraint also automatically indexes that property for fast lookup.)

### 3.2 Using the Neo4j Python Driver to Create Data

Now let’s do the same thing through Python code. This is useful if you want to build your knowledge graph programmatically (for example, loading data from an external source or building an app). We’ll use Neo4j’s official Python driver, which supports connecting to AuraDB.

**Install the Neo4j Python Driver:** If you haven’t installed it yet, you can install it via pip:

```bash
pip install neo4j
```



The driver allows your Python code to connect to the database via the Bolt protocol. Let’s write a Python snippet to connect to our Aura instance and create some data. Make sure to replace `<URI>`, `<username>`, and `<password>` with your AuraDB instance’s Bolt URI and credentials:

```python
from neo4j import GraphDatabase

# Connection details for AuraDB - replace with your instance URI and credentials
URI = "neo4j+s://<your-instance-id>.databases.neo4j.io"  # AuraDB Bolt URL (secure)
AUTH = ("neo4j", "<your-password>")  # ("username", "password"), username is typically 'neo4j' for AuraDB

# Connect to the database (the driver will establish a session to AuraDB)
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()  # optional, checks if connection is successful

    # Create two Person nodes and a KNOWS relationship between them using Cypher
    summary = driver.execute_query(
        """
        CREATE (a:Person {name: $name})
        CREATE (b:Person {name: $friendName})
        CREATE (a)-[:KNOWS]->(b)
        """,
        name="Alice", friendName="David", 
        database_="neo4j"  # target the default database
    ).summary()
    print(f"Created {summary.counters.nodes_created} nodes in {summary.result_available_after} ms.")
```

In the code above, we used the Aura connection URI (with `neo4j+s://`) and the credentials. We then used `driver.execute_query(...)` to run a multi-statement Cypher command that creates an `Alice` (Person) node, a `David` (Person) node, and a `KNOWS` relationship from Alice to David. The `$name` and `$friendName` in the Cypher string are **parameters** – we pass actual values for them (`"Alice"` and `"David"`) via the `execute_query` arguments. Using parameters is good practice (avoids hardcoding values and helps prevent injection issues). The driver returns a result summary which we used to print how many nodes were created and how long it took.

When you run this code in a Jupyter notebook or script, it should output something like:

```
Created 2 nodes in 123 ms.
```

(indicating the two Person nodes were created successfully, in some amount of time).

**Note:** AuraDB’s default database name is **neo4j**, which we specified with `database_="neo4j"`. If you omit the database, the driver will use the default automatically. Aura Free/Professional currently only allow one database per instance (no multi-database support), so “neo4j” is the one you use.

Now we have inserted the same data (Alice knows David) via Python. You can verify this by querying the database (in code or in Neo4j browser) or by looking at the Neo4j Aura console metrics.

## 4. Querying the Knowledge Graph with Cypher

With data in our graph (however minimal so far), we can start querying it to get insights. Cypher queries in Neo4j typically use the `MATCH` clause to describe patterns to search for in the graph, much like a SELECT in SQL (but for graph patterns), and a `RETURN` clause to output the results.

Let’s perform some read queries on our social network data. We will show how to do it in the Neo4j Browser and via the Python driver.

### 4.1 Querying in Neo4j Browser (Cypher Examples)

Suppose we want to find all people in our database and their friends. We can use a pattern match for Person nodes and outgoing KNOWS relationships. In the Neo4j browser, try:

```cypher
MATCH (p:Person)-[:KNOWS]->(friend:Person)
RETURN p.name AS person, friend.name AS knows_friend;
```

This query will find all instances of a pattern where a `Person` node `p` has a `KNOWS` relationship to another `Person` node `friend`. It returns the names of the person and their friend. In our small example, the result should list “Alice” in the `person` column and “David” in the `knows_friend` column (since Alice knows David). If we had more data (say, if David knew someone else, those would appear too).

A few things to note in this Cypher query:

* We used `(p:Person)` to match nodes with the label Person and bound them to the variable `p`. Similarly, `friend:Person` for the friend nodes.
* The pattern `(p:Person)-[:KNOWS]->(friend:Person)` has a directed arrow `->`, meaning we only find “p KNOWS friend” in that direction. In social networks, you might consider KNOWS to be symmetric (friendship both ways). If our data stored only one direction, we could also query ignoring direction by using a non-directional match `(p:Person)-[:KNOWS]-(friend:Person)`, which would find relationships in either direction. Just be aware that an undirected match finds both directions (and could return two mirror results, one for each direction, unless you structure the query to avoid duplicates).
* We used `RETURN p.name AS person, friend.name AS knows_friend` to output the names with more readable column aliases. The `AS` keyword renames the returned columns.

If you run the above in the browser, you’ll get a table of results and you can also switch to the “Graph” view to visualize the matching subgraph.

Let’s extend our data a bit to demonstrate more queries (you can run these in the browser):

```cypher
// Add another person and relationships
CREATE (bob:Person {name: "Bob", age: 28});
CREATE (alice)-[:KNOWS]->(bob);
CREATE (bob)-[:KNOWS]->(david);
```

Now we have added a third person, Bob. Alice knows Bob, and Bob knows David (so Bob acts as a connection between Alice and David as well).

Some query examples to try:

* **Find all people that Alice knows (direct friends of Alice):**

  ```cypher
  MATCH (:Person {name:"Alice"})-[:KNOWS]->(friend:Person)
  RETURN friend.name AS AliceFriend;
  ```

  This matches any Person with name "Alice" and finds their outgoing KNOWS connections. It should return Bob and David as Alice’s friends (after the above data insertions). In our small dataset, Alice knows Bob and David.

* **Friends of friends:** Who does Alice’s friends know? (This can reveal second-degree connections.)

  ```cypher
  MATCH (alice:Person {name:"Alice"})-[:KNOWS]->(friend:Person)-[:KNOWS]->(fof:Person)
  RETURN friend.name AS AliceFriend, fof.name AS FriendOfFriend;
  ```

  This looks for a path of length 2: Alice -> friend -> fof. With our data, Alice -> Bob -> David fits this pattern. The query would return a row with AliceFriend = Bob and FriendOfFriend = David. This indicates Alice’s friend Bob knows David (who is a friend-of-friend to Alice).

* **Mutual friends between two people:** For example, do Alice and David share any mutual friend?

  ```cypher
  MATCH (a:Person {name:"Alice"})-[:KNOWS]->(x:Person)<-[:KNOWS]-(d:Person {name:"David"})
  RETURN x.name AS MutualFriend;
  ```

  This finds any Person `x` that Alice knows and David knows. In our case, Alice knows Bob and David knows Bob (through Bob -> David relationship we added), but note *our data as entered has Bob -> David, not David -> Bob*. If we treat KNOWS as undirected friendship, we might need to also create the inverse relation or query undirected. The above query as written looks for Alice -> x and David -> x (outgoing from both). If we instead interpret Bob knows David as David knows Bob as well, we could either create the reverse or adjust the query to not depend on direction for one of the hops. For demonstration, if we had made KNOWS reciprocal (added `CREATE (david)-[:KNOWS]->(bob)` too), then Bob would appear as a mutual friend of Alice and David.

These queries illustrate how Cypher can express network traversals in a very straightforward way.

### 4.2 Querying via Python Driver

Now, let’s perform queries using the Python driver, continuing from our earlier code. We’ll reuse the `driver` connection to run a `MATCH` query and retrieve results in Python:

```python
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    # Query: find all Person names who know someone (have an outgoing KNOWS)
    records, summary, keys = driver.execute_query(
        """
        MATCH (p:Person)-[:KNOWS]->(:Person)
        RETURN p.name AS name
        """,
        database_="neo4j"
    )
    for record in records:
        print(record.data())  # each record is a dict of the returned values
    print(f"The query '{summary.query}' returned {len(records)} records in {summary.result_available_after} ms.")
```

In this code, we use `driver.execute_query` to run a MATCH that finds all people who have a KNOWS relationship to another person. We then iterate over the `records` (which are Python mappings for each result row) and print them. We also print a summary line.

Given our current dataset, this query `MATCH (p:Person)-[:KNOWS]->(:Person)` will find persons who know at least one other person. That should include Alice (because she knows Bob and David) and Bob (because he knows David). David knows no one (in the data as directed), so David would not appear in this result. If you run the code after inserting Bob as above, you might see output like:

```
{'name': 'Alice'}
{'name': 'Bob'}
The query 'MATCH (p:Person)-[:KNOWS]->(:Person) RETURN p.name AS name' returned 2 records in 5 ms.
```

This indicates Alice and Bob each have outgoing KNOWS relationships in our graph. The summary also shows how many records and how fast the query was.

We could also parameterize queries in Python just as we did for the CREATE. For example:

```python
name_to_find = "Alice"
records, _, _ = driver.execute_query(
    "MATCH (p:Person {name: $name})-[:KNOWS]->(friend:Person) RETURN friend.name AS friend",
    name=name_to_find, database_="neo4j"
)
for record in records:
    print(f'{name_to_find} knows {record["friend"]}')
```

This would output Alice’s friends (using a parameter for the name filter).

**Working with Query Results:** The Neo4j Python driver returns results that you can manipulate in code. In the above example, `record.data()` gives a dictionary of the row, but you can also access values by key (`record["friend"]`) or by position. The `summary` object can provide metadata (like the query text, counters for how many nodes/relationships created, time taken, etc.). For example, after a write query, `summary.counters.nodes_created` told us how many nodes were created.

### 4.3 Updating and Deleting Data

For completeness, let's mention how to update or delete elements in your graph:

* **Updating properties:** You can use the `SET` clause in Cypher to update a node or relationship’s properties. For example, to update Alice’s age:

  ```cypher
  MATCH (p:Person {name: "Alice"})
  SET p.age = 26;
  ```

  This finds Alice and sets (or adds) her `age` property to 26. In Python, you could run a similar query with `execute_query` or use a session transaction.
* **Deleting nodes/relationships:** To delete something, you use the `DELETE` clause. However, Neo4j will not allow you to delete a node if it still has relationships (to prevent leaving “dangling” relations). You must either delete the relationships first or use `DETACH DELETE` to remove a node along with all its relationships. For example, to delete Bob entirely:

  ```cypher
  MATCH (p:Person {name: "Bob"})
  DETACH DELETE p;
  ```

  This will remove Bob and any KNOWS relationships connected to Bob in one go.

Be cautious with deletes if you have a lot of data or interconnected nodes, as `DETACH DELETE` can remove large subgraphs.

## 5. Summary and Next Steps

We have successfully created a small knowledge graph on Neo4j AuraDB, representing a social network, and demonstrated how to query it using Cypher (both in the Neo4j Browser and through a Python application). We covered setting up the AuraDB instance, connecting to it securely, and using Cypher’s pattern-matching to insert and retrieve data. You should now have the foundation to model your own domain as a graph and explore it using Cypher queries.

**Recap of key points:**

* Neo4j AuraDB provides a convenient cloud-hosted Neo4j database (with a free tier) that you can set up in minutes.
* The graph data model uses nodes, relationships, and properties to store information in a highly connected way, which is ideal for knowledge graphs and social networks.
* Cypher is a powerful, declarative query language for graphs. We used Cypher 25 (the latest version) which has an ASCII-art syntax to easily express graph patterns. We practiced basic Cypher CRUD operations: `CREATE` nodes/relationships, `MATCH` patterns to read data, and we discussed `SET` and `DELETE` for updates.
* We connected to Neo4j from Python using the official driver. We showed how to run queries programmatically, leveraging parameters and retrieving results in Python data structures. This allows integration of the graph database with applications, analytics, or notebooks.

**Where to go from here?** With these basics in hand, you can expand your knowledge graph with more data and more complex queries. Neo4j has many advanced features like indexing (to speed up lookups), constraints (to enforce data integrity), full-text search, and graph algorithms for analytics – all of which can be applied as your project grows. You can manage these in AuraDB just like on a local Neo4j.

For learning more about Cypher and Neo4j development, here are some great resources:

* **Neo4j Cypher “Fundamentals” Course:** Neo4j offers an interactive online course on GraphAcademy called *Cypher Fundamentals*, which teaches Cypher querying in about one hour and gives you a free sandbox to practice. This is highly recommended to solidify your understanding of the query language.
* **Neo4j Documentation and Guides:** The official Neo4j documentation has a Getting Started guide for Cypher and many examples. There’s also a Cypher Refcard (cheat sheet) and a full Cypher manual if you need to look up specific syntax or functions.
* **Neo4j Python Driver Manual:** We touched on the basics, but the driver manual provides more examples (like using explicit sessions, transactions, error handling, etc.). As you build applications, those patterns become important.
* **Community & Support:** The Neo4j community forum and Stack Overflow are active places to ask questions. Neo4j’s AuraDB service also has a status page and support if you run into issues.

We hope this tutorial gave you a clear, comprehensive start to building knowledge graphs with Neo4j AuraDB, Cypher, and Python. Happy graph hacking!

**Sources:** The information and examples above were based on Neo4j’s official documentation and tutorials, including the AuraDB documentation, the Cypher manual and getting-started guide, and the Neo4j Python driver manual for code snippets. 
