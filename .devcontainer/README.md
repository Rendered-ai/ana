# VSCode Remote Containers
VSCode Remote Containers are used to simplify the process of setting up an environment to build and run ana in using Docker Containers. To learn more visit [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers).

## Installation
To install Remote Containers, perform the following steps:
1. [Install Docker](https://docs.docker.com/get-docker/)
2. [Download VSCode](https://code.visualstudio.com/download)
3. Open VSCode, select the Extensions button on the left.
4. Search for Remote Containers, select it and click install.

## Running in a remote container.
To run in a remote container, perform the following steps:
1. In VSCode, open your repository folder so .devcontainers is at the top-level.
2. Press F1 (or CTLR + SHIFT + P) and type "Remote Containers: Rebuild and Reopen in Container"
3. If this is your first time using it, it will take a minute to download and build the docker container.
4. After it is complete, open a Terminal. This will place you in the container:
```bash
(anatools) anadev@XXX:/workspaces/ana$ 
```
5. From there you can run ana, for example:
```bash
blender --background --python ana/ana.py -- --channel example --graph ana/channels/example/graphs/example_test.yml
```

## Additional Information
The following describes what each of the files are used for:
| File | Description |
|-|-|
| ana_cpu_blender2.90_Dockerfile | This is the orignial Dockerfile used for the CPU base image, it includes Ubuntu, Blender 2.90 and miniconda. |
| ana_gpu_blender2.90_Dockerfile | This is the orignial Dockerfile used for the GPU base image, it includes CUDA 11.1, Blender 2.90 and miniconda. |
| devcontainer.json | This file defines different settings to use with the Remote Containers extension. |
| Dockerfile | This Dockerfile is used to add additional libraries to the Dev Container image. |
| Dockerfile.deploy | This Dockerfile is used when building the channel for deploying to the Rendered.ai Platform. |
| startContainer.sh | This script is executed after the container is brought up, it installs ana and anatools for the user. |
