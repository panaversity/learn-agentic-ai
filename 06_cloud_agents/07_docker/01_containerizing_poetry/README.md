# Containerizing a Poetry Project

We will take the project created in step09_create_project and containerize it. 

First lets run it without a container:

    poetry run python test_poetry/main.py


[Read Chapters 8 our Text Book: Docker Deep Dive by Nigel Poulton 2023 Edition](https://www.amazon.com/Docker-Deep-Dive-Nigel-Poulton/dp/1916585256)

## Class Videos

Now you have no excuse not to become a Cloud Native AI expert:

Cloud Native AI Class Videos

Poetry Class 1:

https://www.youtube.com/watch?v=g9u-H628jXg&t=4s


API Class 2:

https://www.youtube.com/watch?v=ckXDNS2iRiY&t=6s


Docker Basics Class 3:

https://www.youtube.com/watch?v=eRbtrOIIP3k


Docker class 4:

https://www.youtube.com/watch?v=94KPnrkjB5I


Docker class 5:

https://www.youtube.com/watch?v=Ip2aOBemFU8



Dev Containers Class 6:


https://www.youtube.com/watch?v=h32qw986-tI


Help Desk Session: How to Use Dev Containers and Error Resolution


https://www.youtube.com/watch?v=7475K6UNLSA

## Multiple Dockerfile

https://www.divio.com/blog/guide-using-multiple-dockerfiles/

https://stackoverflow.com/questions/27409761/docker-multiple-dockerfiles-in-project




## Building Python Dockerfiles with Poetry

This tutorial guides you through creating Dockerfiles for Python projects using Poetry, covering both development and production scenarios.


**Base Image:**

We'll use `python:3.12-slim` as the base image for both examples.

**1. Development Dockerfile:**

This Dockerfile incorporates installing Poetry using `pipx` for development purposes:

```dockerfile
FROM python:3.12-slim


ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.2
  
# System deps:
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# Install dependencies with Poetry
COPY pyproject.toml ./
RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "main.py"]
```

**Explanation:**

1. **Base Image:** Inherits from the `python:3.12` image.
2. **ARG and ENV:**
    https://vsupalov.com/docker-arg-env-variable-guide/
3. **Install Peotry using curl**
    
4. **Workdir:** Sets the working directory to `/app`.

5. **Install Dependencies (Poetry):**
    * Copies `pyproject.toml`.
    * Installs dependencies using `poetry install`.
6. **Copy Project Files:** Copies all project files to the working directory.
7. **Command:** Sets the command to run `poetry run python main.py`, which executes the main Python script with Poetry's virtual environment activated.


**Checking to see if Docker is running:**

```bash
docker version
```

**Building the Image:**

```bash
docker build -f Dockerfile.dev -t my-dev-image .
```

**Check Images:**

```bash
docker images
```

**Verify the config:**

```bash
docker inspect my-dev-image
```

**Running the Container:**

https://docs.docker.com/engine/reference/run/

```bash
docker run --name dev-cont1 -it my-dev-image
```

**List Running Containers**

```bash
docker ps
```


**Running the Container and start a Bash shell:**

```bash
docker run -it my-dev-image /bin/bash
```

**Opening the command line in the container:**

```bash
docker exec -it my-dev-image bash
```


This approach ensures Poetry is available in the development container for managing dependencies while keeping the production Dockerfile focused on efficiency.


**2. Production Dockerfile (Multi-Stage Build):**

This Dockerfile focuses on optimization and efficiency for production environments:

```dockerfile
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# Stage 2: Production image
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/lib/python3.12/site-packages .
COPY . .

ENTRYPOINT ["python", "main.py"]
```

**Explanation:**

1. **Stage 1:**
    * Inherits from `python:3.12-slim`.
    * Sets working directory to `/app`.
    * Copies `pyproject.toml`.
    * Disables automatic virtual environment creation by Poetry.
    * Installs dependencies excluding development packages using `poetry install --no-dev`.
2. **Stage 2:**
    * Inherits from the same base image.
    * Sets working directory to `/app`.
    * Copies only the installed dependencies from the builder stage using `COPY --from=builder /app/lib/python3.12/site-packages .`. This significantly reduces the image size.
    * Copies the rest of the project files.
    * Sets the entry point to directly execute `python main.py`.

**Building the Image:**

```bash
docker build -f Dockerfile.prod -t my-prod-image --target prod .
```

**Running the Container:**

```bash
docker run -it my-prod-image
```

**Benefits:**

* **Smaller Image Size:** By copying only dependencies in the second stage, the image size remains minimal.
* **Faster Builds:** Subsequent builds only rebuild the first stage if dependencies change, leading to faster builds.
* **No Poetry in Runtime:** Poetry is not required in the final image, reducing the overall footprint.

**Additional Notes:**

* You can customize the commands and configurations based on your project's specific needs.
* Consider using `.dockerignore` to exclude unnecessary files from the build process.
* Explore advanced Docker features like environment variables and volumes for further customization.

Remember to choose the appropriate Dockerfile based on your use case, balancing development convenience with production efficiency.

## Project for You: Optimization for Production

You will now learn from this Tutorial and try to further optimize the production build:

https://medium.com/@albertazzir/blazing-fast-python-docker-builds-with-poetry-a78a66f5aed0

Note: BuildKit is the default builder for users on Docker Desktop, and Docker Engine as of version 23.0 and above therefore no need to add this in our Dockerfile as mentioned in this tutorial.


## References

## What Are Multi-Stage Docker Builds?

**Multi-stage builds** are a powerful feature in Docker that allow you to create more efficient and smaller container images. They are particularly useful when optimizing Dockerfiles while keeping them readable and maintainable.

In a nutshell, multi-stage builds involve using multiple `FROM` statements in your Dockerfile. Each `FROM` instruction defines a new stage in the build process. You can selectively copy artifacts from one stage to another, leaving behind anything you don't need in the final image.



### How Do Multi-Stage Builds Work?

https://devguide.dev/blog/how-to-create-multi-stage-dockerfile

### What is BuildKit

BuildKit is an improved backend to replace the legacy builder. BuildKit is the default builder for users on Docker Desktop, and Docker Engine as of version 23.0.




