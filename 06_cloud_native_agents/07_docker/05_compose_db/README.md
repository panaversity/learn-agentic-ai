# Docker Compose with Database Service

Notes: We are using code of previous steps but have **removed** the requirement of sslmode in the main.py file:

```
  engine = create_engine(
      connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)
```

All we have included .env file, you do not have to create a new one.

## How to validate your compose file

In order to validate your compose.yaml file give the following command (docker compose config renders the actual data model to be applied on the Docker Engine. It resolves variables in the Compose file, and expands short-notation into the canonical format):

```
  docker compose config
  
```

**Example: Python and PostgreSQL with Network**

This example demonstrates a Compose file with a Python service and a PostgreSQL service connected by a custom network named "my-api-net":

Details

https://hub.docker.com/_/postgres

https://github.com/docker-library/docs/blob/master/postgres/README.md


```yaml
version: "3.9"

name: myapi

services:
  api:
    build:
      context: ./todo
      dockerfile: Dockerfile.dev
    depends_on:
        - postgres_db
    ports:
      - "8000:8000"  # Expose container port 8000 to host port 8000  
    networks:
      - my-api-net
  postgres_db:
    image: postgres:latest  # Use the official PostgreSQL image
    restart: always
    container_name: PostgresCont
    environment:
        - POSTGRES_USER=ziakhan
        - POSTGRES_PASSWORD=my_password
        - POSTGRES_DB=mydatabase
    ports:
        - '5433:5432'
    volumes:
        - postgres_db:/var/lib/postgresql/data
    networks:
      - my-api-net

volumes:
  postgres_db:
    driver: local

networks:
  my-api-net:  # Define the custom network

```

**Explanation:**

 **Here's a detailed explanation of the Docker Compose file:**

**File Structure:**

- **Version:** `3.9` specifies the Compose file format for compatibility.
- **Project Name:** `myapi` labels the project for organization.

**Services:**

- **api:**
    - **Build:**
        - `context: ./todo`: Instructs Compose to build the image from the `./todo` directory.
        - `dockerfile: Dockerfile.dev`: Specifies the Dockerfile named `Dockerfile.dev` for building instructions.
    - **Depends_on:** `postgres_db`: Ensures the database starts before this service.
    - **Ports:** `8000:8000`: Maps container port 8000 to host port 8000 for accessibility.
    - **Networks:** `my-api-net`: Connects the service to the designated network.

- **postgres_db:**
    - **Image:** `postgres:latest`: Uses the official PostgreSQL image for the database.
    - **Restart:** `always`: Automatically restarts the container if it crashes.
    - **Container_name:** `PostgresCont`: Assigns a friendly name to the container for identification.
    - **Environment:** Sets database credentials and configuration:
        - `POSTGRES_USER=ziakhan`: Database username.
        - `POSTGRES_PASSWORD=my_password`: Database password.
        - `POSTGRES_DB=mydatabase`: Name of the database to create.
    - **Ports:** `5433:5432`: Exposes container port 5432 (PostgreSQL's default) to host port 5433 for access.
    - **Volumes:** `postgres_db:/var/lib/postgresql/data`: Persistently stores database data in a volume named `postgres_db`.
    - **Networks:** `my-api-net`: Connects to the custom network.

**Volumes:**

- **postgres_db:** Creates a named volume with the local driver for database data persistence.

**Networks:**

- **my-api-net:** Defines a custom isolated network for communication between services.

**Summary:**

This Compose file defines a two-service application:

1. An API service, built from a Dockerfile and exposed on port 8000.
2. A PostgreSQL database service, using a ready-made image with specific configuration and exposed on port 5433.

Both services are connected to a shared network for seamless communication. The database data is preserved using a persistent volume.


**Running the application:**

With this Compose file saved as `compose.yml` , you can use the following commands to manage your application:

* `docker compose up -d`: This builds the images (if needed) and starts both containers in detached mode (background). You can check it by going open: http://0.0.0.0:8000/ in browser.
* `docker compose stop`: This stops both containers.
* `docker compose down`: This stops and removes both containers, as well as volumes associated with them.

## Connection String (added to the .env file)

Here's the connection string you can use to connect to the Postgres database from another container running in the same Docker network:


```
postgresql://ziakhan:my_password@PostgresCont:5432/mydatabase
```

Let's break down the connection string components:

* `postgresql://`: This specifies the database driver to be used (in this case, PostgreSQL).
* `ziakhan:my_password`: This defines the username and password for connecting to the database. Replace `my_password` with your actual Postgres user's password.
* `@PostgresCont`: This indicates the hostname or IP address of the Postgres container. By default, Docker links container names to hostnames within the Docker network. If your Postgres container is named differently (e.g., `my-postgres`), replace `PostgresCont` with the actual name.
* `:5432`: This specifies the port on which the Postgres server is listening. The default port for Postgres is 5432, but you can change it if your container configuration uses a non-standard port.
* `/mydatabase`: This defines the name of the specific database you want to connect to within the Postgres instance.

**Important Note:**

* Replace `mydatabase` with the actual name of the database you want to connect to.
* Ensure proper password storage is implemented for production environments. Avoid hardcoding the password in the connection string. Consider environment variables or secrets management solutions.

**Additional Considerations:**

* **Network Connectivity:** Verify that both containers are connected to the same Docker network to ensure proper communication.
* **Custom Ports:** If you've mapped the Postgres container's port to a different host port during container creation using `-p`, update the connection string's port number accordingly (e.g., `:5433` if mapped to host port 5433).

By following these guidelines and using the provided connection string format, you should be able to connect to your Postgres database from another container within your Docker environment.

## Install pgAdmin to connect to the Database

pgAdmin is the most popular and feature rich Open Source administration and development platform for PostgreSQL, the most advanced Open Source database in the world.

Download and Install pgAdmin 4:

https://www.pgadmin.org/download/

Connect to our PostgresSQL Container:

Host name/address: localhost

Post: 5433 (note it is not the default 5432)

Maintaince database: mydatabase

Username: ziakhan

Password: my_password

## Assignment

Create a seprate database container for testing in compose file. You dont need to even use a volume for test database since we don't care to persist test data between runs. Once you have created the test database and updated the .env file, run the tests.  


