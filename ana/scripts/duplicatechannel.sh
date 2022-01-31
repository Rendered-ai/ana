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
  echo "Duplicates the example channel to the channel name specified."
  echo "Options:"
  echo "-h    Show Help Menu"
  echo "-c    The name of the channel to create."
  echo
}

while getopts ":hc:" options; do
    case ${options} in
        h)          usage
                    exit;;
        c)          channel=${OPTARG};;
        \?)         echo "Invalid option."
                    usage
                    exit;;
    esac
done


# get the arguments, ensure channel name was given and channel exists
if [[ ! -n $channel ]]; then 
  echo "Please provide the channel name: .duplicatechannel.sh -c <channel>"
  exit 1
fi

if [ ! -d "../channels/example/" ]; then 
  echo "No example channel directory found at ana/channels/example/."
  exit 1
fi

# duplicate the directory
cp -a ../channels/example ../channels/$channel
