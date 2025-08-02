# Neo4j AuraDB

https://neo4j.com/docs/aura/

## Create an Account and Instance

https://neo4j.com/docs/aura/getting-started/create-account/

https://neo4j.com/docs/aura/getting-started/create-instance/

## Connect to a Instance

https://neo4j.com/docs/aura/getting-started/connect-instance/ 


## Instance Actions

https://neo4j.com/docs/aura/managing-instances/instance-actions/


## Develop

https://neo4j.com/docs/aura/managing-instances/develop/


## Getting Started with Cyper

https://neo4j.com/docs/getting-started/cypher/ 


## Cypher Fundamentals Course: Learn Cypher in One Hour

https://graphacademy.neo4j.com/courses/cypher-fundamentals/

## Neo4j Python Driver Manual

It has example code:

https://neo4j.com/docs/api/python-driver/current/


https://neo4j.com/docs/python-manual/current/


## Cypher 25 Cheat Sheet

https://neo4j.com/docs/cypher-cheat-sheet/25/all/ 

## Cypher 25 Manual

https://neo4j.com/docs/cypher-manual/25/introduction/ 


This tutorial will guide you through building a knowledge graph from the ground up using **Neo4j AuraDB**, the cloud-based graph database service. We will use the **Cypher** query language to model and query our data, and **Python** to programmatically interact with our database.

-----

## 1\. What is a Knowledge Graph?

A knowledge graph is a way to store data as a network of entities and the relationships between them. Instead of tables with rows and columns, you have **nodes** (the entities) and **relationships** (the connections). This model is incredibly flexible and powerful for representing complex, interconnected data, such as social networks, supply chains, or biological systems.

**Neo4j** is the leading graph database platform, and **AuraDB** is its fully managed cloud service, which handles the setup, maintenance, and scaling of the database for you.

-----

## 2\. Setting Up Your Neo4j AuraDB Instance

First, you'll need to create a free Neo4j AuraDB account and spin up a new database instance.

### Create an Account

1.  Go to the [Neo4j Aura registration page](https://www.google.com/search?q=https://neo4j.com/cloud/aura-db-registration/).
2.  Sign up using your email and a password or by linking your Google or GitHub account.
3.  Follow the on-screen instructions to verify your account.

### Create an Instance

Once your account is created, you'll be prompted to create a new AuraDB instance.

1.  You will be prompted to create a new instance. Select the **Free** tier, which is more than sufficient for this tutorial.
2.  Choose a cloud provider and region that is geographically close to you for lower latency.
3.  Your instance will be created automatically. You will be given a password that is required to connect to the database. **Store this password securely**, as it will not be shown again. You can find your connection URI and username on the instance's credentials page.

-----

## 3\. Connecting to Your Instance

You can interact with your AuraDB instance in several ways.

### Using the Neo4j Browser

The simplest way to connect is through the web-based Neo4j Browser.

1.  From your AuraDB console, click the **"Open"** button next to your instance.
2.  A new tab will open with the Neo4j Browser.
3.  Use the username (`neo4j`) and the password you saved earlier to connect.

The browser provides an interactive environment where you can execute Cypher queries and visualize the results as a graph.

### Connecting with Python

To build applications, you'll connect programmatically using a driver. We'll use the official Neo4j Python driver.

First, install the driver using pip:

```bash
pip install neo4j
```

Next, use the credentials from your AuraDB instance page to establish a connection. Your connection URI will look something like `neo4j+s://xxxxxx.databases.neo4j.io`.

Here’s a simple Python script to test your connection:

```python
from neo4j import GraphDatabase

# Replace with your instance's URI, username, and password
URI = "neo4j+s://your-aura-instance-uri.databases.neo4j.io"
AUTH = ("neo4j", "your-password")

def check_connection(driver):
    """Checks if the connection to the database is successful."""
    try:
        driver.verify_connectivity()
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        check_connection(driver)
```

Run this script. If you see "Connection successful\!", you're ready to start building.

-----

## 4\. Introduction to Cypher: The Language of Graphs

**Cypher** is a declarative query language designed for graphs. It uses ASCII art patterns to represent nodes and relationships, making it intuitive to read and write.

### Basic Cypher Syntax

  * **Nodes** are represented with parentheses: `()`
  * **Relationships** are represented with arrows: `-[]->` or `<-[]-`
  * **Labels** define the type of a node: `(:Person)`
  * **Relationship types** define the type of a connection: `-[:ACTED_IN]->`
  * **Properties** are key-value pairs stored on nodes and relationships: `(p:Person {name: 'Tom Hanks'})`

### Core Cypher Clauses

  * **`CREATE`**: Creates nodes and relationships.
  * **`MATCH`**: Searches for patterns in the graph.
  * **`MERGE`**: A combination of `MATCH` and `CREATE`. It will find an existing pattern or create it if it doesn't exist. This is very useful for avoiding duplicate data.
  * **`RETURN`**: Specifies what data to return from a query.
  * **`SET`**: Modifies properties on nodes and relationships.
  * **`DELETE`**: Deletes nodes and relationships.

-----

## 5\. Building a Movie Knowledge Graph

Let's build a simple knowledge graph of movies and actors.

### Step 1: Create a `Movie` Node

Let's add the movie *The Matrix*. A movie has a `title` and a `released` year.

Execute this in the Neo4j Browser or via your Python script:

```cypher
CREATE (m:Movie {title: 'The Matrix', released: 1999})
```

### Step 2: Create `Person` Nodes

Now, let's add the actors.

```cypher
CREATE (p1:Person {name: 'Keanu Reeves'})
CREATE (p2:Person {name: 'Carrie-Anne Moss'})
CREATE (p3:Person {name: 'Laurence Fishburne'})
```

### Step 3: Create Relationships

The real power of a graph comes from its relationships. Let's connect the actors to the movie with an `ACTED_IN` relationship.

```cypher
MATCH (p:Person {name: 'Keanu Reeves'}), (m:Movie {title: 'The Matrix'})
CREATE (p)-[:ACTED_IN]->(m)

MATCH (p:Person {name: 'Carrie-Anne Moss'}), (m:Movie {title: 'The Matrix'})
CREATE (p)-[:ACTED_IN]->(m)

MATCH (p:Person {name: 'Laurence Fishburne'}), (m:Movie {title: 'The Matrix'})
CREATE (p)-[:ACTED_IN]->(m)
```

### Step 4: Querying the Graph

Now that we have data, we can ask questions.

**Query: Who acted in *The Matrix*?**

```cypher
MATCH (p:Person)-[:ACTED_IN]->(m:Movie {title: 'The Matrix'})
RETURN p.name
```

**Query: What movies has Keanu Reeves acted in?**

```cypher
MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie)
RETURN m.title
```

-----

## 6\. Building the Knowledge Graph with Python

Let's automate the process of loading data into our knowledge graph using Python. We'll create a script that adds movies and their actors from a predefined list.

Here is a complete Python script that connects to your AuraDB instance, clears any existing data, and populates it with a small dataset.

```python
from neo4j import GraphDatabase

# --- Connection Details ---
# Replace with your instance's URI, username, and password
URI = "neo4j+s://your-aura-instance-uri.databases.neo4j.io"
AUTH = ("neo4j", "your-password")

# --- Sample Data ---
movie_data = [
    {
        "title": "The Matrix", "released": 1999,
        "actors": ["Keanu Reeves", "Carrie-Anne Moss", "Laurence Fishburne"]
    },
    {
        "title": "The Matrix Reloaded", "released": 2003,
        "actors": ["Keanu Reeves", "Carrie-Anne Moss", "Laurence Fishburne"]
    },
    {
        "title": "John Wick", "released": 2014,
        "actors": ["Keanu Reeves", "Michael Nyqvist", "Alfie Allen"]
    }
]

def add_movies(driver, movies):
    """Adds movie and actor data to the graph."""
    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing data.")

        for movie in movies:
            # Using MERGE to avoid creating duplicate movies
            session.run("""
                MERGE (m:Movie {title: $title})
                SET m.released = $released
            """, title=movie['title'], released=movie['released'])

            for actor_name in movie['actors']:
                # MERGE for actors and the relationship
                session.run("""
                    MATCH (m:Movie {title: $title})
                    MERGE (p:Person {name: $name})
                    MERGE (p)-[:ACTED_IN]->(m)
                """, title=movie['title'], name=actor_name)
        print("Data loaded successfully.")

def find_keanu_movies(driver):
    """Finds all movies Keanu Reeves acted in."""
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person {name: 'Keanu Reeves'})-[:ACTED_IN]->(m:Movie)
            RETURN m.title AS movie_title
        """)
        print("\nMovies starring Keanu Reeves:")
        for record in result:
            print(f"- {record['movie_title']}")

if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print("Connected to Neo4j AuraDB.")

        add_movies(driver, movie_data)
        find_keanu_movies(driver)
```

**To run this script:**

1.  Replace the placeholder `URI` and `AUTH` details with your own.
2.  Save the code as a Python file (e.g., `build_kg.py`).
3.  Run it from your terminal: `python build_kg.py`.

You will see output confirming the connection, data clearing, loading, and the final query result listing Keanu Reeves' movies.

-----

## 7\. Managing Your AuraDB Instance

The AuraDB console provides simple actions for managing your instance:

  * **Pause**: If you're not using your instance, you can pause it to conserve resources (on paid tiers). Free instances are automatically paused after a period of inactivity.
  * **Resume**: Reactivate a paused instance.
  * **Delete**: Permanently delete your instance and all its data.

These actions are available from the instance list in your Neo4j Aura console.

-----

## 8\. Further Learning

This tutorial covers the basics, but the world of knowledge graphs is vast. To deepen your understanding, explore these resources:

  * **Cypher Fundamentals Course**: A free, one-hour course from Neo4j GraphAcademy: [graphacademy.neo4j.com/courses/cypher-fundamentals](https://graphacademy.neo4j.com/courses/cypher-fundamentals/)
  * **Neo4j Python Driver Manual**: In-depth documentation for the Python driver: [neo4j.com/docs/python-manual/current/](https://neo4j.com/docs/python-manual/current/)
  * **Cypher Cheat Sheet**: A quick reference for all Cypher clauses and functions: [neo4j.com/docs/cypher-cheat-sheet/25/all/](https://neo4j.com/docs/cypher-cheat-sheet/25/all/)
  * **Official AuraDB Documentation**: For detailed information on all AuraDB features: [neo4j.com/docs/aura/](https://neo4j.com/docs/aura/)

By following this guide, you have successfully set up a Neo4j AuraDB instance, modeled a domain using a graph structure, and used both Cypher and Python to build and query your first knowledge graph. Happy graphing\! 





 