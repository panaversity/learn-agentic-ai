# Developing inside a Container

We will edit the code we develop in the last step. 
This tutorial walks you through running Visual Studio Code in a Docker container using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

https://code.visualstudio.com/docs/devcontainers/tutorial


<img alt="Architecture Containers" src="./architecture-containers.png" width="500px"></img>

The Dev Containers extension supports two primary operating models:

* You can attach to a running container to inspect it.
    
    https://code.visualstudio.com/docs/devcontainers/attach-container

* You can use a container as your full-time development environment
    
    https://code.visualstudio.com/docs/devcontainers/containers

## Attach to a Docker container

<img alt="Attach Container" src="./cmd1.png" width="1000px"></img>

<img alt="Attach Container" src="./attach-container.png" width="500px"></img>

To attach to a Docker container, either select Dev Containers: Attach to Running Container... from the Command Palette (F1) or use the Remote Explorer in the Activity Bar and from the Containers view, select the Attach to Container inline action on the container you want to connect to.

## Developing inside a Container

System requirements

* You can use Docker with the Dev Containers extension in a few ways, including:

    * Docker installed locally.
    * Docker installed on a remote environment.
    * Other Docker compliant CLIs, installed locally or remotely.
        * While other CLIs may work, they are not officially supported.

## Video Tutorials

https://www.youtube.com/watch?v=h32qw986-tI

https://www.youtube.com/watch?v=7475K6UNLSA
