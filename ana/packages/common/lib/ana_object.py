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
from abc import ABC
import logging
import bpy
from ana.packages.common.lib.search_utils import find_root
import ana.packages.common.lib.bbox as annotations

logger = logging.getLogger(__name__)


class AnaObject(ABC):
    """ Base class for Ana objects """

    next_instance = 1

    def __init__(self, object_type):

        # instance number
        self.instance = AnaObject.next_instance
        AnaObject.next_instance += 1
        # object type
        self.object_type = object_type
        # loaded flag is set to true after the object has been loaded into the current scene
        self.loaded = False
        # pointer to bpy.data.collections["collectionName"] where collectionName is the collection containing the object
        self.collection = None # set in loader
        # pointer to bpy.data.objects["objectName"] where objectName is the name of the root object
        self.root = None # set in loader
        # does this object appear in the rendered image? This will be set in the annotation module
        self.rendered = False
        # modifier metadata
        self.modifiers = []
        # object of interest - set when adding object to scene
        self.ooi = False
        # location of mask file for scene rendered with only this object
        self.solo_mask_id = ''
        # object specific configuration
        self.config = {}

    def __key(self):
        # the key for hashing and equality comparison
        return (self.instance,)

    def __hash__(self):
        # make the object hashable so we can use it as a dictionary key
        return hash(self.__key())

    def load(self, **kwargs):
        """
        Default loader - Load the object from a file

        If you override this method in your subclass you must do all of the following
            - create the object hierarchy with a single root object
            - create the object collection
            - link all objects to the collection
            - link the collection to the current scene
            - set self.collection = the collection datablock
            - set self.root = the root object datablock
            - set self.loaded = True
       """
        if self.loaded:
            # only load the object once
            return

        blender_file = kwargs.pop("blender_file")
        # load the collection
        with bpy.data.libraries.load(filepath="//" + blender_file, link=False) as (_, dt):
            dt.collections = [self.object_type]
        self.collection = dt.collections[0]
        
        # link collection to the current scene
        bpy.context.scene.collection.children.link(self.collection)

        # find the root object
        self.root = find_root(self.collection)
        self.loaded = True

        # save object config if it was provided
        if "config" in kwargs:
            self.config = kwargs.pop("config")


    def dump_metadata(self):
        """
        Convert object to a JSON serializable representation.
        Sub classes add metadata by implementing the dump_metadata method as follows:
            def dump_metadata(self):
                meta = super().dump_metadata()
                return {**meta, "subclass-attribute": subclass-value, ...}
        """
        metadata = {
            "id": self.instance,
            "type": self.object_type
        }

        if len(self.modifiers) > 0:
            metadata["modifiers"] = self.modifiers
        
        return metadata

    def dump_annotations(self, calculate_obstruction=False):
        """ Generate annotations for the object. """
        if not self.ooi:
            return
        seg, bbox = annotations.compute_polygons(self)
        if seg is None or bbox is None:
            self.rendered = False
            return
        bbox3d = annotations.compute_bbox3d(self)
        centroid, distance = annotations.compute_centroid(self)
        truncated = annotations.truncated(self, bbox)
        if calculate_obstruction:
            obstruction = annotations.compute_obstruction(self)
        else:
            obstruction = None
        size = annotations.compute_size(self)
        rotation = annotations.compute_rotation(self)
        annotation = {
            'id':           self.instance,
            'bbox':         bbox,
            'segmentation': seg,
            'bbox3d':       bbox3d,
            'centroid':     centroid,
            'distance':     distance,
            'truncated':    truncated,
            'size':         size,
            'rotation':     rotation,
            'obstruction':  obstruction}
        return annotation

    def find_object(self, qname):
        """
        Recursively search the object hierarchy for a child object where
        qname is a list of object base names from the original hierarchy.

        For example, given this object hierarchy in the original blender file:

        Aircraft
          Left_Wing
            Flap
          Right_Wing
            Flap.001

        To find the right wing flap in a loaded instance of this object you
        would do the following, assuming "aircraft" is the AnaObject instance.

        obj = aircraft.find_object(["Right_Wing", "Flap"])

        IMPORTANT CAVEAT:

        This will not work if an object in the hierarchy has two children with
        the same base name, e.g.

        Aircraft
          Left_Wing
            Flap
            Flap.001
          Right_Wing
            Flap.002
            Flap.003

        To solve this problem you need to modify the original file to follow the
        "no two children with the same base name" rule

        """
        
        # start at the root
        obj = self.root
        # find objects below the root
        for level, name in enumerate(qname):
            found_child = False
            # if exact match not found then the object was renamed when loaded
            for child in obj.children:
                if child.name.startswith(name):
                    found_child = True
                    obj = child
                    break
            if not found_child:
                # no child matched qname at this level
                logger.critical("Ana object '%s' does not contain '%s'", self.root.name, " ".join(qname[:level+1]))
                sys.exit(1)
        # if all levels matched then we found the object
        return obj
