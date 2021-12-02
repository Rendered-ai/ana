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
from ana.packages.common.lib.node import Node
from ana.packages.common.lib.ana_object import AnaObject
from ana.packages.common.lib.generator import get_blendfile_generator
import ana.packages.common.lib.context as ctx
import logging

logger = logging.getLogger(__name__)

COLORS = {
    'Violet': (0.4196, 0.1412, 0.7020, 1),  # HSV: 270, 80, 70
    'Indigo': (0.1412, 0.1412, 0.7020, 1),  # HSV: 240, 80, 70
    'Blue':   (0.1412, 0.1412, 0.7020, 1),    # HSV: 210, 80, 70
    'Green':  (0.1412, 0.7020, 0.1412, 1),   # HSV: 120, 80, 70
    'Yellow': (0.7020, 0.7020, 0.1412, 1),  # HSV: 60, 80, 70
    'Orange': (0.7020, 0.4196, 0.1412, 1),  # HSV: 30, 80, 70
    'Red':    (0.7020, 0.1412, 0.1412, 1),     # HSV: 0, 80, 70
    'Black':  (0.0, 0.0, 0.0, 1),
    'White':  (1.0, 1.0, 1.0, 1),
}


class ExampleChannelObject(AnaObject):
    """
    A class to represent the Example Channel AnaObjects.
    Add a 'color' method for the objects of interest.
    """

    def color(self, color_type=None):
        pass


class BubblesObject(ExampleChannelObject):
    """
    A class to represent the Bubbles AnaObject with a color method specific to the shader nodes of the blender file.
    """

    def color(self, color_type=None):
        # Change the bubbles bottle RGB Node
        try:
            if color_type == '<random>':
                # ctx.random just np.random and retains the seed used for reproducibility
                color_type = ctx.random.choice([c for c in COLORS.keys()])
                while color_type in ['White', 'Black']:
                    color_type = ctx.random.choice([c for c in COLORS.keys()])

            mat = [m for m in self.root.material_slots if 'BubbleBottle' in m.name][0]
            # print([n.name for n in mat.material.node_tree.nodes])
            rgb_node = mat.material.node_tree.nodes['RGB']
            rgb_node.outputs[0].default_value = COLORS[color_type]
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise


class YoyoObject(ExampleChannelObject):
    """
    A class to represent the Yoyo AnaObject with a color method specific to the shader nodes of the blender file.
    """

    def color(self, color_type=None):
        # Change the YoYo specific RGB Node
        try:
            if color_type == '<random>':
                color_type = ctx.random.choice([c for c in COLORS.keys()])
                while color_type in ['White', 'Black']:
                    color_type = ctx.random.choice([c for c in COLORS.keys()])

            obj = self.root
            mat = obj.material_slots[0]  # there is only one material in the Yoyo
            rgb_node = mat.material.node_tree.nodes['RGB']
            rgb_node.outputs[0].default_value = COLORS[color_type]
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise


class SkateboardObject(ExampleChannelObject):
    """
    A class to represent the Skateboard AnaObject with a color method specific to the shader nodes of the blender file.
    """

    def color(self, color_type=None):
        # Change the Skateboard specific RGB Node
        try:
            if color_type == '<random>':
                color_type = ctx.random.choice([c for c in COLORS.keys()])

            # Script in Blender: bpy.data.materials["Skateboard_Board"].node_tree.nodes["RGB"].outputs[0].default_value=...
            mat = [m for m in self.root.material_slots if 'Skateboard_Board' in m.name][0]
            rgb_node = mat.material.node_tree.nodes['RGB']
            rgb_node.outputs[0].default_value = COLORS[color_type]
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise


class PlayDohObject(ExampleChannelObject):
    """
    A class to represent the PlayDoh AnaObject with a color method specific to the shader nodes of the blender file.
    """

    def color(self, color_type=None):
        # Change the RGB Node for the Play-Doh lid
        try:
            if color_type == '<random>':
                color_type = ctx.random.choice([c for c in COLORS.keys()])
                while color_type in ['Yellow', 'Orange']:
                    color_type = ctx.random.choice([c for c in COLORS.keys()])

            # Script in Blender: bpy.data.materials["RenDoh"].node_tree.nodes["RGB.004"].outputs[0].default_value = ...
            mat = [m for m in self.root.material_slots if 'RenDoh' in m.name][0]
            rgb_node = mat.material.node_tree.nodes['RGB.004']
            rgb_node.outputs[0].default_value = COLORS[color_type]
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise


class BubblesNode(Node):
    """
    A class to represent the Bubbles node, a node that instantiates a generator for the Bubbles object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Bubbles Bottle Generator": get_blendfile_generator("example", BubblesObject, "BubbleBottle")}


class YoyoNode(Node):
    """
    A class to represent the Yoyo node, a node that instantiates a generator for the Yoyo object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Yoyo Generator": get_blendfile_generator("example", YoyoObject, "YoYo")}


class SkateboardNode(Node):
    """
    A class to represent the Skateboard node, a node that instantiates a generator for the Skateboard object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Skateboard Generator": get_blendfile_generator("example", SkateboardObject, "Skateboard")}


class PlayDohNode(Node):
    """
    A class to represent the PlayDoh node, a node that instantiates a generator for the PlayDough object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Play Dough Generator": get_blendfile_generator("example", PlayDohObject, "PlayDough")}


class RubikNode(Node):
    """
    A class to represent the Rubik node, a node that instantiates a generator for the Cube object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Rubik's Cube Generator": get_blendfile_generator("example", ExampleChannelObject, "Cube")}


class MixedRubikNode(Node):
    """
    A class to represent the MixedRubik node, a node that instantiates a generator for the Mix Cube object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))
        return {"Mixed Cube Generator": get_blendfile_generator("example", ExampleChannelObject, "Mix Cube")}


class ContainerNode(Node):
    """
    A class to represent the Container node, a node that instantiates a generator for the a container object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        try:
            # get node inputs
            box_type = self.inputs["Container Type"][0]
            if box_type == "<random>":
                # select a random container
                select_list = [portdef["select"] for portdef in self.schema["inputs"] if
                               portdef.get('name') == "Container Type"][0]
                select_list.remove("<random>")
                box_type = ctx.random.choice(select_list)
                while box_type in ['Tall Basket', 'Short Basket']:
                    box_type = ctx.random.choice(select_list)
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise

        return {"Container Generator": get_blendfile_generator("example", AnaObject, box_type)}


class FloorNode(Node):
    """
    A class to represent the Floor node, a node that instantiates a generator for the a floor object.
    """

    def exec(self):
        logger.info("Executing {}".format(self.name))

        try:
            floor_type = self.inputs["Floor Type"][0]
            if floor_type == "<random>":
                # select a random floor
                select_list = [portdef["select"] for portdef in self.schema["inputs"] if
                               portdef.get('name') == "Floor Type"][0]
                select_list.remove("<random>")
                floor_type = ctx.random.choice(select_list)
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise

        return {"Floor Generator": get_blendfile_generator("example", AnaObject, floor_type)}
