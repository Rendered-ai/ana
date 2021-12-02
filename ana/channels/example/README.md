# Ana Channel
This directory includes files that define a channel, graphs to run on a channel and mappings for annotations. This guide will describe what each of the files is for in this directory.

## Config
The channel config directory is used to define the channel and how it appears on the Rendered.ai Platform when deployed.
| File | Description |
|-|-|
| channel.yml | This file defines what nodes are included in the channel and where they can be found. |
| deckard.yml | This file defines what the channel nodes will look like in the Graph Editor page of the Rendered.ai Platform, for example what category the node is found under and what color is assigned to the node. |

## Graphs
The channel graphs directory is where we store graphs for the channel. The files in this directory are used when call Ana locally with the --graph parameter. The graphs define what nodes are run and how they are connected together.

## Lib
The channel lib directory contains a setup.py and postprocess.py file that are executed before or after the nodes in the graph is executed. This is helpful when you need to setup libraries or assets, for example the render settings for Blender.

## Mappings
Mapping files are used for the annotations microservice to convert channel-specific classes to ML-oriented categories. These mappings can be selected from a drop-down menu when creating a new annotation for a dataset. An example of this may be to have classes of objects that are different vehicles (Make A Model A, Make A Model B) and wanting them to be a single annotation category called "Vehicles". Using the mapping file you can specify categories, supercategories, etc for each object type in the channel.

## Tests
The tests folder is used to store pytests for the channel. These pytests can be used to verify that a channel is working and notify the developers of any issues and calculate node coverage with test graphs. The tests can be used during the deployment process of a channel to verify the channel is working as expected on the Platform.
