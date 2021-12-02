#!/bin/bash

# install ana in the Blender environment
echo -n "Installing ana..."
conda activate blender && \
pip install -e . > ./.devcontainer/startContainer.log
echo "done."

# install anatools in the anatools environment
echo -n "Installing anatools..."
conda activate anatools && \
pip install anatools >> ./.devcontainer/startContainer.log
echo "done."

# expose the docker socket
sudo chmod 777 /var/run/docker.sock 
docker logout public.ecr.aws