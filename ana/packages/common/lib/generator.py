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
from abc import ABC, abstractmethod
import json
import os
import copy
import numpy as np
import ana
import ana.packages.common.lib.context as ctx
from ana.packages.common.lib.ana_object import AnaObject

def get_blendfile_generator(package, object_class, object_type):
    """
    Helper function that creates a generator from an object
    definition in the package.yml file
    """
    rel_path = ctx.packages[package]["objects"][object_type]["filename"]
    blender_file = ana.get_volume_path(package, rel_path)
    generator = ObjectGenerator(
        object_class,
        object_type,
        blender_file=blender_file,
        config=ctx.packages[package]["objects"][object_type])
    return generator

class Generator(ABC):
    """
    Base class for generators and modifiers
    """
    next_id = 0
    # all generators indexed by id
    generators = {}
    def __init__(self, children=None, **kwargs):
        self.id = Generator.next_id
        Generator.generators[self.id] = self
        Generator.next_id += 1
        if children is None:
            self.children = []
        else:
            self.children = children
        self.kwargs = kwargs
        self.weight = 1

    @abstractmethod
    def exec(self, *args, **kwargs):
        pass

    def clone(self):
        """
        Clone a generator. The clone has no children.
        """
        the_clone = copy.copy(self)

        the_clone.id = Generator.next_id
        Generator.generators[the_clone.id] = the_clone
        Generator.next_id += 1
        the_clone.children = []
        return the_clone

    def select_child(self):
        """ Select a weighted random child """
        weights = []
        for child in self.children:
            weights.append(child.weight)
        weights = np.array(weights)
        selected = ctx.random.choice(self.children, p=weights/sum(weights))
        return selected

class ObjectGenerator(Generator):
    """
    Object Generator
    """
    def __init__(self, object_class, object_type, **kwargs):
        """ Note: kwargs are for the loader """
        super().__init__(children=[], **kwargs)
        self.object_class = object_class
        self.object_type = object_type

    def exec(self, *args, **kwargs):
        """ Return a new instance of the specified object """
        # instantiate the object class
        obj = self.object_class(self.object_type)
        # load the object into the scene
        obj.load(**self.kwargs)
        # return the object
        return obj

    def __repr__(self):
        return json.dumps({
            "class": self.__class__.__name__,
            "id": self.id,
            "object_class": self.object_class.__name__,
            "object_type": self.object_type,
            "kwargs": self.kwargs
        })

class ObjectModifier(Generator):
    """
    Object Modifier
    """
    def __init__(self, method, children, **kwargs):
        """ Note: kwargs are for the modifier method """
        super().__init__(children=children, **kwargs)
        self.method = method

    def exec(self, *args, **kwargs):
        """ Execute modifier method on object """
        child = self.select_child()
        # recursively execute until we get an object
        if not isinstance(child, AnaObject):
            child = child.exec(*args, **kwargs)
        # execute modifier method
        getattr(child, self.method)(**self.kwargs)
        return child

    def __repr__(self):
        return json.dumps({
            "class": self.__class__.__name__,
            "id": self.id,
            "method": self.method,
            "kwargs": self.kwargs
        })

class CreateBranchGenerator(Generator):
    """
    A generator that connects branches together
    """
    def __init__(self, children, **kwargs):
        super().__init__(children=children, **kwargs)

    def exec(self, *args, **kwargs):
        """ Select a child and execute it """
        child = self.select_child()
        result = child.exec(*args, **kwargs)
        return result

    def __repr__(self):
        return json.dumps({
            "class": self.__class__.__name__,
            "id": self.id
        })

class PathList(list):
    """
    A list of paths. Each path is a list of generator id's from root to leaf
    """
    def __init__(self, paths=None):
        if paths is None:
            super().__init__([])
        else:
            super().__init__(paths)

    def to_tree(self):
        """
        Convert a PathList into an executable tree
        """
        # clone the generators
        new_generators = {}
        id_map = {}
        new_children = {}
        for path in self:
            for gen_id in path:
                if gen_id not in new_generators:
                    clone = Generator.generators[gen_id].clone()
                    new_generators[gen_id] = clone
                    id_map[gen_id] = clone.id
                    new_children[clone.id] = []
        # create a map of the children
        for path in self:
            if len(path) > 1:
                for i in range(len(path[:-1])):
                    clone_id = id_map[path[i]]
                    clone_child_id = id_map[path[i+1]]
                    if clone_child_id not in new_children[clone_id]:
                        new_children[clone_id].append(Generator.generators[clone_child_id])
        # update the children of the clones
        for key, value in new_children.items():
            Generator.generators[key].children = value

        tree = Generator.generators[id_map[self[0][0]]]
        return tree

def _get_all_leaves(tree, leaf_class=ObjectGenerator, leaves=None):
    """
    Helper function that gets a list of all leaves in the tree. The list may include
    dupes because it follows every possible path
    """
    if leaves is None:
        leaves = []
    if isinstance(tree, leaf_class):
        leaves.append(tree)
        return leaves
    else:
        for child in tree.children:
            leaves = _get_all_leaves(child, leaf_class, leaves)
        return leaves

def get_unique_leaves(tree, leaf_class=ObjectGenerator):
    """
    Get list of all unique leaves in the tree.
    """
    leaves_with_dupes = _get_all_leaves(tree, leaf_class=leaf_class)
    ids = []
    leaves = []
    for leaf in leaves_with_dupes:
        if leaf.id not in ids:
            ids.append(leaf.id)
            leaves.append(leaf)
    return leaves

def _get_single_pathlist(tree, leaf_class=ObjectGenerator):
    """
    Helper function that follows a random path to a leaf.
    Returns a PathList with a single path
    """
    path = PathList([[]])
    while not isinstance(tree, leaf_class):
        path[0].append(tree.id)
        tree = tree.select_child()
    path[0].append(tree.id)
    return path

def create_single_path(tree, leaf_class=ObjectGenerator):
    """
    Create an exectuable single path to a weighted random leaf.
    """
    return _get_single_pathlist(tree, leaf_class=ObjectGenerator).to_tree()

def _get_all_paths(tree, leaf_class=ObjectGenerator, paths=None, current_depth=0):
    """
    Helper function that creates a list of all paths in the tree
    Returns a Pathlist with one entry per path
    """
    if paths is None:
        paths = PathList([[]])
    current_depth += 1
    paths[-1].append(tree.id)
    if isinstance(tree, leaf_class):
        # if we are at a leaf then we're done with this path
        return paths
    else:
        # otherwise continue down the left-most path until we hit a leaf
        paths = _get_all_paths(tree.children[0], leaf_class, paths, current_depth)
        if len(tree.children) > 1:
            # if there are more children then create new path
            for child in tree.children[1:]:
                paths.append(paths[-1][:current_depth])
                paths = _get_all_paths(child, leaf_class, paths, current_depth)
        return paths

def create_multi_path(tree, leaf_class=ObjectGenerator):
    """
    Create an executable multi path to a weighted random leaf. Path includes all
    possible routes to the leaf.
    """
    # generate a pathlist
    single_path = _get_single_pathlist(tree, leaf_class)
    # get the leaf
    leaf_id = single_path[0][-1]
    # generate all possible paths
    all_paths = _get_all_paths(tree, leaf_class)
    # save all paths that end at the leaf
    paths_to_leaf = PathList()
    for path in all_paths:
        if path[-1] == leaf_id:
            paths_to_leaf.append(path)
    # convert back to a tree
    return paths_to_leaf.to_tree()

if __name__ == "__main__":
    # test
    import os
    from ana.packages.satrgb.nodes.snow_modifier import SnowPlugin
    from ana.packages.satrgb.nodes.color_variation_modifier import ColorVariationPlugin
    from ana.packages.satrgb.lib.custom_encoder import CustomEncoder

    class TestObject1(AnaObject, SnowPlugin, ColorVariationPlugin):
        pass
    class TestObject2(AnaObject, SnowPlugin, ColorVariationPlugin):
        pass

    # use the satrgb channel for testing
    ctx.initialize("satrgb")

    # create a generator for the test
    obj_gen1 = ObjectGenerator(
        object_class=TestObject1,
        object_type="Army_Truck",
        blender_file=os.path.join(ctx.data, "packages/satrgb/models/afv/Army_Truck.blend"))

    # create a generator for the truck object
    obj_gen2 = ObjectGenerator(
        object_class=TestObject2,
        object_type="Army_Truck",
        blender_file=os.path.join(ctx.data, "packages/satrgb/models/afv/Army_Truck.blend"))

    # vary color
    blue = ObjectModifier(
        method=ColorVariationPlugin.color_variation_plugin.__name__,
        children=[obj_gen1, obj_gen2],
        rgba_values=[128, 0, 0, 1.0],
        color_range=10,
        mix_percent=0.1)

    # vary color
    green = ObjectModifier(
        method=ColorVariationPlugin.color_variation_plugin.__name__,
        children=[obj_gen1, obj_gen2],
        rgba_values=[0, 128, 0, 1.0],
        color_range=10,
        mix_percent=0.1)

    # add snow
    snow_gen = ObjectModifier(
        method=SnowPlugin.snow_plugin.__name__,
        children=[blue, green],
        coverage=0.25)

    path = create_multi_path(snow_gen)
    print(json.dumps(path.exec(), cls=CustomEncoder, indent=4))
    print(json.dumps(path.exec(), cls=CustomEncoder, indent=4))
    print(json.dumps(path.exec(), cls=CustomEncoder, indent=4))
    print(json.dumps(path.exec(), cls=CustomEncoder, indent=4))