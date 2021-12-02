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
# import sys
import logging
import gc
import ana.packages.common.lib.context as ctx
from ana.packages.common.lib.node import create_node

logger = logging.getLogger(__name__)

def interp(graph):
    """Interpret a graph"""
    graphFormatVersion = graph.get("version", 0.0)

    # channel setup
    ctx.channel.setup()

    # create and configure nodes
    nodes = {}
    for name, node_config in sorted(graph["nodes"].items()):
        if graphFormatVersion == 0.0:
            nodes[name] = create_node(name, node_config["class"])
            nodes[name].configure_v0(node_config)
        else:
            nodes[name] = create_node(name, node_config["nodeClass"])
            nodes[name].configure(node_config)

    # append outlinks to nodes
    for dst_node in nodes:
        for dst_port in nodes[dst_node].inlinks:
            for link in nodes[dst_node].inlinks[dst_port]:
                src_node, src_port = link
                if src_node in nodes.keys():
                    schema_output_set = set()
                    for port_dict in nodes[src_node].schema["outputs"]:
                        schema_output_set.add(port_dict["name"])
                    if src_port not in schema_output_set:
                        logger.error(
                            "Node '%s' class '%s' input '%s' is linked to node '%s' class '%s' on undefined port '%s'",
                            dst_node, nodes[dst_node].__class__.__name__, dst_port,
                            src_node, nodes[src_port].__class__.__name__, src_port)
                        sys.exit(1)
                    if src_port not in nodes[src_node].outlinks.keys():
                        nodes[src_node].outlinks[src_port] = []
                    nodes[src_node].outlinks[src_port].append((dst_node, dst_port))
                else:
                    logger.error(
                        "Node '%s' class '%s' input '%s' is linked to undefined node '%s'",
                        dst_node, nodes[dst_node].__class__.__name__, dst_port, src_node)
                    sys.exit(1)

    # execute nodes
    while len(nodes) > 0:
        node_executed = None
        for name, node in nodes.items():
            # if all input links have been resolved then execute this node
            if len(node.inlinks.keys()) == 0:
                logger.info("Executing node '%s' class '%s'", name, node.__class__.__name__)
                outputs = node.exec()
                # verify the actual node output matches the schema outputs
                # TODO: After people clean up their returns, make this throw an exception.
                schema_output_set = set()
                for port_dict in node.schema["outputs"]:
                    schema_output_set.add(port_dict["name"])
                if set(outputs.keys()) != schema_output_set:
                    logger.error("Output returned by node '%s' class '%s' doesn't match output defined in schema",
                                node.name, node.__class__.__name__)
                # resolve output links
                for src_port in node.outlinks:
                    for outlink in node.outlinks[src_port]:
                        dst_node, dst_port = outlink
                        # append value to input of destination node/port
                        if dst_port not in nodes[dst_node].inputs.keys():
                            nodes[dst_node].inputs[dst_port] = []
                        nodes[dst_node].inputs[dst_port].append(outputs[src_port])
                        # remove inlink from destination node/port
                        try:
                            nodes[dst_node].inlinks[dst_port].remove((name, src_port))
                            # if there are no more inlinks on the destination port then delete it
                            if len(nodes[dst_node].inlinks[dst_port]) == 0:
                                del nodes[dst_node].inlinks[dst_port]
                        except ValueError:
                            # this is a coding error
                            logger.critical(
                                "Node '%s' class '%s' is missing link '[%s, %s]'",
                                dst_node, nodes[dst_node].__class__.__name__, name, src_port)
                            sys.exit(1)
                node_executed = node
                break

        # delete the node we executed
        if node_executed:
            del nodes[node_executed.name]
        else:
            # this is either a coding error or a cycle in the graph
            errorString = "Graph execution failed; graph may be cyclic. The following links could not be resolved: "
            linkDescriptions = []
            for name in nodes:
                for port in nodes[name].inlinks:
                    for inlink in nodes[name].inlinks[port]:
                        linkDescriptions.append("Node '%s' class '%s' input '%s' link '[%s, %s]'",
                                                name, nodes[name].__class__.__name__, port, inlink[0], inlink[1])
            errorString += ', '.join(linkDescriptions)
            logger.error(errorString)
            sys.exit(1)

    # channel post processing
    ctx.channel.post_process()

    gc.collect()