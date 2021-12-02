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
import os
import logging
import importlib
import importlib.util
import yaml

logger = logging.getLogger(__name__)

class Channel:
    """ Channel class """
    def __init__(self, root_dir, base_dir, channel_name):

        self.name = channel_name
        self.channel_config_file = os.path.join(base_dir, "channels", channel_name, "config", "channel.yml")
        self.deckard_config_file = os.path.join(base_dir, "channels", channel_name, "config", "deckard.yml")

        # read channel configuration
        try:
            with open(self.channel_config_file, "r") as f:
                channel_config = yaml.safe_load(f)
        except FileNotFoundError:
            logger.critical("Channel configuration error - 'channel.yml' file not found")
            sys.exit(1)
        except yaml.scanner.ScannerError:
            logger.critical("Channel configuration error - error parsing file 'channel.yml'")
            sys.exit(1)

        # load class definitions and schemas
        self.classes = {}
        self.schemas = {}
        package_names = []
        for alias, channel_node_def in channel_config["nodes"].items():
            module = channel_node_def["module"]
            klass = channel_node_def["class"]
            self.classes[alias] = {
                "module": module,
                "class": klass
            }
            package_names.append(module.split(".")[2])

            schema_file = os.path.abspath(os.path.join(root_dir, *module.split(".")) + ".yml")
            
            # load the original schema
            try:
                with open(schema_file, "r") as f:
                    schema_module = yaml.safe_load(f)
                    schema = schema_module["schemas"][klass]
                    modified_schema = schema.copy()
            except yaml.scanner.ScannerError:
                logger.critical("Schema error for class '%s' - YAML scanner error", klass)
                sys.exit(1)

            # override node inputs
            if channel_node_def.get("inputs") is not None:
                for port, override in channel_node_def["inputs"].items():
                    # find port in schema
                    found = False
                    for num, schema_port_def in enumerate(schema["inputs"]):
                        if schema_port_def["name"] == port:
                            # override the definition
                            modified_schema["inputs"][num] = {"name": port, **override}
                            found = True
                            break
                    if not found:
                        logging.error("Input port '%s' not found in schema file '%s'", port, schema_file)
                        sys.exit(1)
            
            # override node outputs
            if channel_node_def.get("outputs") is not None:
                for port, override in channel_node_def["outputs"].items():
                    # find port in schema
                    found = False
                    for num, schema_port_def in enumerate(schema["outputs"]):
                        if schema_port_def["name"] == port:
                            # override the definition
                            modified_schema["outputs"][num] = {"name": port, **override}
                            found = True
                            break
                    if not found:
                        logging.error("Output port '%s' not found in schema file '%s'", port, schema_file)
                        sys.exit(1)

            # save updated schema
            self.schemas[alias] = modified_schema

        # get unique package names
        package_names = list(set(package_names))

        # load package configurations and merge overrides
        self.packages = {}
        self.package_config_files = {}
        for package_name in package_names:
            try:
                self.package_config_files[package_name] = os.path.join(base_dir, "packages", package_name, "config", "package.yml")
                with open(self.package_config_files[package_name], "r") as f:
                    self.packages[package_name] = yaml.safe_load(f)
                    if channel_config.get("packages") is not None and channel_config["packages"].get(package_name) is not None:
                        for key, value in channel_config["packages"][package_name].items():
                            self.packages[package_name][key] = value
            except FileNotFoundError:
                logger.critical("Package configuration error - 'package.yml' file not found for package '%s'", package_name)
                sys.exit(1)
            except yaml.scanner.ScannerError:
                logger.critical("Package configuration error - error parsing file 'package.yml' for package '%s'", package_name)
                sys.exit(1)

    def setup(self):
        """ Load and execute the channel-specific setup function """
        module = "ana.channels.{}.lib.setup".format(self.name)
        if importlib.util.find_spec(module):
            setup = getattr(importlib.import_module(module), "setup")
            setup()

    def post_process(self):
        """ Load and execute the channel-specific post process function """
        module = "ana.channels.{}.lib.post_process".format(self.name)
        if importlib.util.find_spec(module):
            post_process = getattr(importlib.import_module(module), "post_process")
            post_process()
