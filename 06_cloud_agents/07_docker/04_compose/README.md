# Docker Compose

Docker Compose is a tool specifically designed to simplify the development and management of applications that consist of multiple Docker containers. Here's a breakdown of what it does and why it's useful:

**Functionality:**

* **Define services in a YAML file:**  Compose allows you to define the different services (containers) that make up your application in a single YAML file. This file specifies things like the image to use for each container, any environment variables, ports to expose, and how the containers should link together.

* **Start, stop, and manage services with a single command:**  Once you've defined your services in the YAML file, you can use Docker Compose commands to easily manage them. For instance, with a single command you can start up all the containers required for your application, stop them all, or rebuild them.

* **Streamlined development experience:**  By using Compose, you can set up a consistent development environment with all the dependencies your application needs. This makes it easier for developers to work on the project and ensures everyone has the same environment.

* **Simplified collaboration:**  The Compose YAML file acts as a clear and shareable definition of your application's infrastructure. This makes it easier for teams to collaborate on development and deployment.

**Benefits:**

* **Reduced complexity:**  Managing multiple containers can get complicated. Compose streamlines this process by allowing you to define and manage everything in one place.

* **Improved development workflow:**  Compose makes it faster and easier to get started with development and iterate on your application.

* **Enhanced collaboration:**  The shareable Compose file makes it easier for developers and operations teams to work together.

## Installing Docker Compose

You already have installed Docker Desktop it includes Docker Engine, Docker CLI, and Docker Compose all in one package. Docker Desktop is available for Windows, macOS, and Linux.

Use the following command to check which version is installed:

    docker compose version

## Docker Compose File

A Docker Compose file, written in YAML format, is the heart of defining and managing multi-container applications with Docker. It specifies the configuration for each container service that makes up your application. Here's a breakdown with an example using Python and PostgreSQL:

**Structure of a Docker Compose File:**

A typical Compose file consists of service definitions. Each service represents a single container, and you define its properties like:

* **image:** The Docker image to use for the container (e.g., `python:3.11`).
* **ports:** Maps ports on the container to ports on the host machine (e.g., `8000:8000`).


**Example: Python**

This example demonstrates a Compose file with a single Python FastAPI service:

```yaml
version: "3.9"

name: myapi

services:
  api:
    build:
      context: ./todo
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"  # Expose container port 8000 to host port 8000  

```

**Explanation:**

* **version:** This specifies the Docker Compose file version (here, version 3.9).
* **services:** This section defines only one service:
    * `api`: This builds a container image from the todo directory with Dockerfile.dev file. It exposes port 8000.
    

**Running the application:**


With this Compose file saved as `compose.yml`, you can use the following commands to manage your application:

Do not forget to add .env file with database credentials before building and running the api.

* `docker compose up -d`: This builds the images (if needed) and starts the container in detached mode (background). You can check it by going open: http://0.0.0.0:8000/ in browser.
* `docker compose stop`: This stops the container.
* `docker compose down`: This stops and removes the container.

Note:

The flag `-d` in the command `docker-compose up -d` instructs Docker Compose to run the containers in **detached mode**. Here's what that means:

* **Normal vs. Detached Mode:**
  * By default, the `docker-compose up` command starts the defined services in the foreground. This means the terminal window you run the command from stays open and displays logs from the running containers.
  * With the `-d` flag, Docker Compose starts the containers in the background. This allows the terminal window to be closed, and the containers continue to run independently.

* **Benefits of Detached Mode:**
  * Frees up your terminal window for other tasks.
  * Useful for long-running services that don't require constant interaction.

* **Viewing Logs for Detached Containers:**
   * To view logs from detached containers, use `docker-compose logs` followed by the service name(s).

In summary, the `-d` flag allows you to run Docker Compose services in the background, keeping your terminal free and the containers operational even after the window is closed.

## YAML Crash Course for Docker Compose

Docker Compose uses YAML (YAML Ain't Markup Language) to define your multi-container application. YAML is a human-readable data serialization language, similar to JSON, but with a focus on readability. Here's a breakdown to get you started with YAML in Docker Compose:

**Basic Structure:**

A YAML file is a collection of key-value pairs. Indentation is crucial for defining the structure. More indented elements are nested under the parent element. Here's an example:

```yaml
name: John Doe
age: 30
address:
  street: 123 Main St
  city: Anytown
```

In this example, "name," "age," and "address" are keys. "John Doe," "30," and the nested structure define the values.

**Data Types:**

YAML supports various data types, including:

* **Scalars:** Strings (e.g., "hello"), numbers (e.g., 42), booleans (e.g., true, false)
* **Lists:** Ordered collections of items, enclosed in square brackets `[]` (e.g., ["apple", "banana"])
* **Mappings:** Unordered collections of key-value pairs, enclosed in curly braces `{}` (e.g., {name: "Alice", age: 25})


**Tips and Best Practices:**

* Use proper indentation for readability.
* Use comments (`#`) to explain sections of your YAML file.
* Leverage online YAML validators to check your syntax.
* Refer to the official Docker Compose documentation for a complete list of available options: 

https://docs.docker.com/compose/compose-file/compose-file-v3/

By understanding YAML basics, you'll be well-equipped to write clear and effective Docker Compose files to manage your multi-container applications.

