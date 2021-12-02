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
import importlib
import logging
import ana.packages.common.lib.context as ctx

logger = logging.getLogger(__name__)

def create_node(name, alias):
    """Factory method for node class """

    try:
        module = ctx.channel.classes[alias]["module"]
    except KeyError:
        logger.critical("No module defined for node '%s' in channel definition file", alias)
        sys.exit(1)
    try:
        class_name = ctx.channel.classes[alias]["class"]
    except KeyError:
        logger.critical("No class defined for node '%s' in channel definition file", alias)
        sys.exit(1)

    # import the class
    try:
        node_class = getattr(importlib.import_module(module), class_name)
    except ModuleNotFoundError:
        logger.critical("Can't import class '%s', module '%s' not found", class_name, module)
        sys.exit(1)
    except AttributeError:
        logger.critical("Can't import node '%s', class '%s' not found", alias, class_name)
        sys.exit(1)

    # instantiate the node
    node = node_class(name, alias)

    return node

# base class for all nodes
class Node:
    """Base class for all nodes"""
    def __init__(self, name, alias):

        logger.info("Creating node '%s', class = '%s'", name, self.__class__.__name__)

        self.name = name
        self.alias = alias
        self.properties = {}  # deprecated
        self.inputs = {}
        self.inlinks = {}
        self.outlinks = {}
        self.schema = ctx.channel.schemas[alias]
        self.input_types = ["values", "links"]
        # self.version =

    def configure(self, config):
        """Configure node"""

        logger.info("Configuring node '%s', class = '%s'", self.name, self.__class__.__name__)

        #
        # This function configures inputs and inlinks as follows:
        #
        #   self.inputs = {
        #        "inport1": [val1, val2, val3,...],
        #        ...
        #   }
        #
        #   self.inlinks: {
        #       "inport1": [(src_node1, src_port1), ...],
        #       ...
        #   }
        #
        # The interpreter will configure outlinks as follows:
        #
        #   self.outlinks: {
        #       "outport1": [(dst_node1, dst_port1), ...],
        #   }

        logger.debug("SCHEMA: %s", self.schema)

        # get set of all schema inputs and their defaults
        schema_input_set = set()
        input_defaults = {}
        if self.schema["inputs"] is not None:
            for port_dict in self.schema["inputs"]:
                schema_input_set.add(port_dict["name"])
                if "default" in port_dict:
                    input_defaults[port_dict["name"]] = port_dict.get("default")

        for key, value in config.get("values", {}).items():
            if key not in schema_input_set:
                logger.error("Input port '%s' is not defined in schema for class '%s'", key, type(self).__name__)
                sys.exit(1)

            if key not in self.inputs:
                self.inputs[key] = []
            self.inputs[key].append(value)

        for key, value in config.get("links", {}).items():
            # {nodeName: [{sourceNode: <src_node>, outputPort: <out>}]}
            if key not in self.inlinks:
                self.inlinks[key] = []
            for link in value:
                src_node = link['sourceNode']
                src_port = link['outputPort']
                if src_node == self.name:
                    logger.error("Node '%s' class '%s' port '%s' is connected to the same node",
                                  self.name, self.__class__.__name__, src_port)
                    sys.exit(1)

                self.inlinks[key].append((src_node, src_port))

            logger.debug("INPUTS: %s", self.inputs)

        # if a port doesn't have an input or inlink then use the default
        check_for_defaults = list(schema_input_set - (set(self.inputs.keys()) | set(self.inlinks.keys())))
        for port in check_for_defaults:
            if port in input_defaults.keys():
                self.inputs[port] = [input_defaults[port]]

        # make sure all inputs defined in the schema have either an input or inlink
        unresolveable_ports = list(schema_input_set - (set(self.inputs.keys()) | set(self.inlinks.keys())))
        if len(unresolveable_ports) > 0:
            errorString = "The following ports for node '{}' class '{}' cannot be resolved: ".format(
                self.name, self.__class__.__name__)
            errorString += ', '.join(unresolveable_ports)
            logger.error(errorString)
            sys.exit(1)

    def configure_v0(self, config):
        """Configure node"""

        logger.info("Configuring node '%s', class = '%s'", self.name, self.__class__.__name__)

        #
        # This function configures inputs and inlinks as follows:
        #
        #   self.inputs = {
        #        "inport1": [val1, val2, val3,...],
        #        ...
        #   }
        #
        #   self.inlinks: {
        #       "inport1": [(src_node1, src_port1), ...],
        #       ...
        #   }
        #
        # The interpreter will configure outlinks as follows:
        #
        #   self.outlinks: {
        #       "outport1": [(dst_node1, dst_port1), ...],
        #   }

        logger.debug("SCHEMA: %s", self.schema)

        # get set of all schema inputs and their defaults
        schema_input_set = set()
        input_defaults = {}
        if self.schema["inputs"] is not None:
            for port_dict in self.schema["inputs"]:
                schema_input_set.add(port_dict["name"])
                if "default" in port_dict:
                    input_defaults[port_dict["name"]] = port_dict.get("default")

        if config.get("inputs") is not None:
            for key, value in config["inputs"].items():
                if key not in schema_input_set:
                    logger.error("Input port '%s' is not defined in schema for class '%s'", key, type(self).__name__)
                    sys.exit(1)
                # "in1": {...}
                if isinstance(value, dict):
                    key1, value1 = next(iter(value.items()))
                    # "in1": {"$link": ["src_node1", "src_port1"]}
                    if key1 == "$link" and isinstance(value1, list) and len(value1) == 2:
                        # inlinks["in1"][0] = ("src_node1", "src_port1")
                        src_node = value1[0]
                        src_port = value1[1]
                        if src_node == self.name:
                            logger.error("Node '%s' class '%s' port '%s' is connected to the same node",
                                          self.name, self.__class__.__name__, src_port)
                            sys.exit(1)
                        if key not in self.inlinks:
                            self.inlinks[key] = []
                        self.inlinks[key].append((src_node, src_port))
                    # "in1": {"$list": [elem1, elem2, ...]}
                    elif key1 == "$list" and isinstance(value1, list):
                        for elem in value1:
                            # "in1": {"$list": [... {"key2": "value2"}, ...]}
                            if isinstance(elem, dict):
                                key2, value2 = next(iter(elem.items()))
                                # "in1": {"$list": [... {"$link": ["src_node1", "src_port1"]}, ...]}
                                if key2 == "$link" and isinstance(value2, list) and len(value2) == 2:
                                    # inlinks["in1"][n] = ("src_node1", "src_port1")
                                    src_node = value2[0]
                                    src_port = value2[1]
                                    if src_node == self.name:
                                        logger.error("Node '%s' class '%s' port '%s' is connected to the same node",
                                                    self.name, self.__class__.__name__, src_port)
                                        sys.exit(1)
                                    if key not in self.inlinks:
                                        self.inlinks[key] = []
                                    self.inlinks[key].append((src_node, src_port))
                                else:
                                    if key not in self.inputs:
                                        self.inputs[key] = []
                                    self.inputs[key].append(value1)
                            else:
                                if key not in self.inputs:
                                    self.inputs[key] = []
                                self.inputs[key].append(elem)
                    else:
                        if key not in self.inputs:
                            self.inputs[key] = []
                        self.inputs[key].append(value)
                else:
                    if key not in self.inputs:
                        self.inputs[key] = []
                    self.inputs[key].append(value)
            logger.debug("INPUTS: %s", self.inputs)

        # if a port doesn't have an input or inlink then use the default
        check_for_defaults = list(schema_input_set - (set(self.inputs.keys()) | set(self.inlinks.keys())))
        for port in check_for_defaults:
            if port in input_defaults.keys():
                self.inputs[port] = [input_defaults[port]]

        # make sure all inputs defined in the schema have either an input or inlink
        unresolveable_ports = list(schema_input_set - (set(self.inputs.keys()) | set(self.inlinks.keys())))
        if len(unresolveable_ports) > 0:
            errorString = "The following ports for node '{}' class '{}' cannot be resolved: ".format(
                self.name, self.__class__.__name__)
            errorString += ', '.join(unresolveable_ports)
            logger.error(errorString)
            sys.exit(1)

    def exec(self):
        """Execute Node"""
        return {}