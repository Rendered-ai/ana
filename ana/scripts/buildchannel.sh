#!/bin/bash
# Copyright 2019-2022 DADoES, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the root directory in the "LICENSE" file or at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
set -e
usage(){
  echo "Builds a docker image for the specified channel that can be deployed to the Rendered.AI Engine."
  echo "Options:"
  echo "-h    Show Help Menu"
  echo "-c    The name of the channel to build the docker image for."
  echo "-d    Flag to build the data directory into the docker image or not."
  echo
}

while getopts ":hdc:" options; do
    case ${options} in
        h)          usage
                    exit;;
        c)          channel=${OPTARG};;
        d)          data=1;;
        \?)         echo "Invalid option."
                    usage
                    exit;;
    esac
done


# get the arguments, ensure channel name was given and channel exists
if [[ ! -v channel ]]; then 
  echo "Please provide the channel name: .buildchannel.sh -c <channel>"
  exit 1
fi
if [ ! -d "../channels/$channel/" ]; then 
  echo "No $channel channel directory found at ana/channels/."
  exit 1
fi

# make sure all deckard nodes are in channel config
python validate_configs.py \
  --channel_config ../channels/$channel/config/channel.yml \
  --deckard_config ../channels/$channel/config/deckard.yml
echo "Configuration files validated."

# Create the new Dockerfile used for deployment
echo "Building docker image for $channel channel..."
rm -f .Dockerfile
cat ../../.devcontainer/Dockerfile >> .Dockerfile
echo $'\n' >> .Dockerfile
cat ../../.devcontainer/Dockerfile.deploy >> .Dockerfile

# Create the build directory, add all necessary files/folder to the tar
mkdir -p .build
if [[ -v data ]]; then
  echo $'\n\n# add data directory to docker image \nCOPY data/ /data' >> .Dockerfile
  tar cfh .build/$channel.tar.gz \
    ../ana.py \
    ../__init__.py \
    ../../setup.py \
    ../../requirements.txt \
    ../channels/$channel \
    ../packages/ \
    ../data/ \
    .Dockerfile
else
  tar cfh .build/$channel.tar.gz \
    ../ana.py \
    ../__init__.py \
    ../../setup.py \
    ../../requirements.txt \
    ../channels/$channel \
    ../packages/ \
    .Dockerfile
fi

# Build the docker and cleanup
cat .build/$channel.tar.gz | docker build - -t $channel -f .Dockerfile
rm -rf .build/ .Dockerfile
