## Neo4j AuraDB: Fully Managed Cloud Graph Database

https://neo4j.com/product/auradb/

https://neo4j.com/docs/cypher-manual/current/introduction/cypher-aura/

[Cheat Sheet](https://neo4j.com/docs/cypher-cheat-sheet/5/aura-dbe/)

[Tutorial](https://medium.com/@nebulagraph/understanding-gql-an-comprehensive-overview-of-the-standard-graph-query-language-927db394d3f3)

[Discovering Neo4j AuraDB Free](https://www.youtube.com/watch?v=QOu5VAsCAoA)

[Watch: Neo4j User Guides - Discovering Neo4j AuraDB Free](https://www.youtube.com/watch?v=gV_rdZw5bDs)

[Pricing](https://neo4j.com/pricing/)

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

### **Neo4j AuraDB Tutorial: A Step-by-Step Guide**

Neo4j AuraDB is a fully managed cloud-based graph database service powered by Neo4j. It allows users to deploy graph databases without worrying about infrastructure management. This tutorial will walk you through the process of setting up Neo4j AuraDB, connecting to it using Neo4j Desktop or Neo4j Browser, and running basic Cypher queries to interact with the graph data.

---

### **Step 1: Sign Up for Neo4j AuraDB**

1. **Go to the Neo4j AuraDB website**: Open your browser and visit [Neo4j Aura](https://neo4j.com/aura/).

2. **Create an Account**: If you don't have an account, click on "Get Started Free" to create an account. You can sign up using your email or through your Google account.

3. **Log In**: After creating an account, log in to your Neo4j AuraDB dashboard.

---

### **Step 2: Create a Neo4j AuraDB Instance**

Once logged in, you can create your Neo4j AuraDB instance:

1. **Create a New Database**:
   - On the Neo4j AuraDB dashboard, click on the **“+ New Database”** button.
   
2. **Configure the Database**:
   - **Select Aura Free Tier**: Choose the free tier option if you're just exploring or running small projects.
   - **Database Name**: Enter a name for your database (e.g., `MyGraphDB`).
   - **Region**: Choose a region close to you for better performance.
   - **Password**: Set a secure password for your database. Make sure to store this password safely as you'll need it to connect to the database.
   
3. **Launch the Database**: Click on the "Create" button to launch your database. It may take a few moments for Neo4j AuraDB to set up your instance.

---

### **Step 3: Access Your AuraDB Database**

After creating the database, you will be taken to the database overview page. Here’s how to access your database:

1. **Get the Connection Details**:
   - In the database overview section, you will see connection details such as the **Bolt URL** (for connecting via the Neo4j driver) and **password**.
   - Copy the **Bolt URL** and store it for future use.

2. **Open Neo4j Browser**:
   - You can either use the **Neo4j Browser** hosted by Aura (click "Open with Neo4j Browser") or connect using **Neo4j Desktop** if you prefer working locally.
   
3. **Connect to Your Database**:
   - If you are using the hosted Neo4j Browser, you will be automatically connected.
   - For Neo4j Desktop, open it and click on **Add Connection**. Enter the **Bolt URL**, your database name, username (`neo4j` by default), and the password you created earlier. Then, click **Connect**.

---

### **Step 4: Load Sample Data into Your Neo4j AuraDB**

Before we dive into querying, let's load some sample data into your AuraDB instance.

1. **Use Cypher to Load Data**:
   - In Neo4j, data is queried and inserted using **Cypher**, a query language for graphs.
   - Here is an example of Cypher code that creates nodes representing people and relationships between them:

   ```cypher
   // Create Person Nodes
   CREATE (alice:Person {name: "Alice", age: 30}),
          (bob:Person {name: "Bob", age: 35}),
          (carol:Person {name: "Carol", age: 25}),
          (dave:Person {name: "Dave", age: 40});

   // Create Relationships between them
   CREATE (alice)-[:FRIENDS_WITH]->(bob),
          (bob)-[:FRIENDS_WITH]->(carol),
          (carol)-[:FRIENDS_WITH]->(dave),
          (dave)-[:FRIENDS_WITH]->(alice);
   ```

2. **Run the Query**: 
   - Paste the Cypher query into the query editor in the Neo4j Browser and click the **play button** to execute it.
   - Neo4j will create a simple graph with four nodes (people) and relationships between them.

---

### **Step 5: Query Your Graph Using Cypher**

Now that we’ve created nodes and relationships, let's run some **Cypher queries** to interact with the graph.

#### **1. Retrieve All Nodes in the Graph**
```cypher
MATCH (n) RETURN n;
```
This query retrieves all nodes in your graph. You will see a visual representation of the nodes (circles) and their relationships (arrows) in the Neo4j Browser.

#### **2. Find Friends of a Specific Person**
```cypher
MATCH (p:Person {name: "Alice"})-[:FRIENDS_WITH]->(friends)
RETURN p, friends;
```
This query finds all the friends of "Alice." The `MATCH` clause looks for the node labeled `Person` with the name "Alice" and retrieves nodes connected by the `FRIENDS_WITH` relationship.

#### **3. Filter Based on Node Properties**
```cypher
MATCH (p:Person)
WHERE p.age > 30
RETURN p.name, p.age;
```
This query retrieves the names and ages of people who are older than 30. The `WHERE` clause is used to filter based on the `age` property of the nodes.

#### **4. Count the Number of Friends**
```cypher
MATCH (p:Person)-[:FRIENDS_WITH]->(friends)
RETURN p.name, count(friends) AS num_friends;
```
This query counts the number of friends each person has by returning the `p.name` and the number of `FRIENDS_WITH` relationships for each person.

#### **5. Add a New Person and Relationship**
```cypher
CREATE (eve:Person {name: "Eve", age: 28}),
       (alice)-[:FRIENDS_WITH]->(eve);
```
This query creates a new person named "Eve" and establishes a `FRIENDS_WITH` relationship between "Alice" and "Eve."

---

### **Step 6: Importing Data from CSV**

Neo4j allows you to import data from external sources like CSV files. Here’s how you can load data from a CSV into your AuraDB instance.

1. **Sample CSV File**:
   Prepare a CSV file with the following structure (e.g., `people.csv`):

   ```csv
   name,age
   Alice,30
   Bob,35
   Carol,25
   Dave,40
   Eve,28
   ```

2. **Load CSV Data Using Cypher**:
   If your CSV is hosted online (e.g., on GitHub or an AWS S3 bucket), you can load it directly into Neo4j.

   ```cypher
   LOAD CSV WITH HEADERS FROM 'https://your-csv-url.com/people.csv' AS row
   CREATE (:Person {name: row.name, age: toInteger(row.age)});
   ```

3. **Run the Query**: 
   This will create nodes labeled `Person` with properties `name` and `age`, as defined in the CSV file.

---

### **Step 7: Securing Your Neo4j AuraDB Instance**

It’s essential to keep your database secure, especially when it's cloud-hosted.

1. **Update Passwords**:
   - Always use strong, unique passwords for your AuraDB instance.
   
2. **Enable SSL**:
   - Neo4j AuraDB uses SSL for secure connections, and it’s enabled by default. Ensure you maintain this setting for secure communications with your database.

---

### **Step 8: Monitoring and Scaling Your Database**

Neo4j AuraDB provides monitoring tools to keep track of performance:

1. **Monitor Performance**:
   - The AuraDB dashboard includes basic metrics like CPU usage and query performance. Regularly check these metrics to ensure your database is running optimally.
   
2. **Scaling Your Instance**:
   - If your database grows in size or query complexity, consider upgrading to a paid tier that provides more resources like memory, storage, and enhanced performance.

---

### **Conclusion**

Neo4j AuraDB makes it easy to get started with graph databases without worrying about infrastructure. This tutorial covered everything from signing up for an account to loading and querying data using Cypher. With this knowledge, you can explore more advanced features like data import/export, scaling, and using graph algorithms for deeper insights.

Graph databases like Neo4j are ideal for applications involving complex relationships, such as social networks, recommendation engines, fraud detection, and more. Enjoy exploring the possibilities!