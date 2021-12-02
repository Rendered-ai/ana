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
import sys
import argparse
import yaml

if __name__ == "__main__":
    '''
    This script is called by the buildchannel.sh script. It
    compares channel.yml with deckard.yml and verifies that
    nodes in one are also in the other.
    '''

    # parse commmand line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--channel_config', required=True)
    parser.add_argument('--deckard_config', required=True)
    args = parser.parse_args()

    with open(args.channel_config, "r") as f:
        channel_config = yaml.safe_load(f)
    
    channel_nodes = channel_config["nodes"].keys()
    channel_nodes = set(channel_nodes)

    with open(args.deckard_config, "r") as f:
        deckard_config = yaml.safe_load(f)

    deckard_nodes = []
    for cat_config in deckard_config["add_node_menu"]:
        for subcat_config in cat_config["subcategories"]:
            deckard_nodes.extend(subcat_config["nodes"])

    deckard_nodes = set(deckard_nodes)

    not_in_deckard = list(channel_nodes - deckard_nodes)

    for node in not_in_deckard:
        print(f"WARNING - node '{node}' is in channel.yml but not in deckard.yml")

    not_in_channel = list(deckard_nodes - channel_nodes)

    exit_code = 0
    for node in not_in_channel:
        print(f"ERROR - node '{node}' is in deckard.yml but not in channel.yml")
        exit_code = 1

    if exit_code == 1:
        print("Invalid configuration")

    sys.exit(exit_code)
    