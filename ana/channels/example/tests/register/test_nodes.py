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

"""
Node coverage tests for use with call_pytest.
"""
import pytest
import warnings
import yaml
import ana.packages.common.lib.context as ctx
import subprocess
import os

dirpath = os.path.dirname(os.path.realpath(__file__))
channel = dirpath.split('/')[-3]
ctx.initialize(channel_name=channel)
dataDir = os.environ.get('DATA_ROOT', '/data')
anaExec = os.path.join(os.environ.get('ANA_ROOT', '/ana'), 'ana/ana.py')
graphDir = os.path.join(os.environ.get('ANA_ROOT', '/ana'), 'ana/channels/{}/graphs/'.format(ctx.channel.name))


def interpGraph(graphId):
    # Test the execution of nodes in a graph, keep track of test coverage
    # Load a graph and call Ana Interp
    graphFilePath = graphDir + "{}.yml".format(graphId)
    subprocessArgs = ["blender",
                      "--background", "--python", anaExec, "--",
                      "--channel", ctx.channel.name, "--graph", graphFilePath, "--data", dataDir]
    completedProcess = subprocess.run(subprocessArgs, capture_output=True, check=True, text=True)

    if 'Error' in completedProcess.stderr:
        pytest.fail(completedProcess.stderr)

    # updated nodesTested
    with open(graphFilePath, "r") as f:
        graph = yaml.safe_load(f)

    graphFormatVersion = graph.get("version", 0.0)
    if graphFormatVersion == 0.0:
        pytest.nodesTested.update(set([node['class'] for node in graph['nodes'].values()]))
    else:
        pytest.nodesTested.update(set([node['nodeClass'] for node in graph['nodes'].values()]))


def test_simple_graph():
    warnings.warn(dirpath)
    warnings.warn(channel)
    interpGraph("example_test")


def test_coverage():
    # Warn the user when some nodes are not tested of the universe of node (channels.yml)
    channelNodeNames = set([name for name in ctx.channel.schemas.keys()])
    untestedNodes = channelNodeNames.difference(pytest.nodesTested)
    warningString = '\n{} Total Nodes: '.format(len(channelNodeNames))
    if untestedNodes:
        warningString += '\n\t*** {} Nodes not tested by Ana interpreter execution...'.format(len(untestedNodes))
        for n in untestedNodes:
            warningString += '\n\t\t"{}"'.format(n)
    else:
        warningString += '\n\t*** All Nodes passed execution by the Ana interpreter.'
    warnings.warn(warningString)


def test_value_inputs():
    # Warn the user when a node's input does not have a default value.
    warningString='\nThe following node inputs do not have a default value...'
    foundInputWithoutDefault = False
    for alias, schema in ctx.channel.schemas.items():
        if schema['inputs']:
            inputs_no_defaults = [inputDict['name'] for inputDict in schema['inputs'] if not inputDict.get('default')]
            for i in inputs_no_defaults:
                foundInputWithoutDefault = True
                warningString += '\n\t"{}": "{}"'.format(alias, i)
    if foundInputWithoutDefault:
        warnings.warn(warningString)

