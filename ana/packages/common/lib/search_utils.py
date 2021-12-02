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
import logging
import bpy

logger = logging.getLogger(__name__)


def get_child_objects(model):
    """Return a list of all children of an object"""

    children = []
    for child in model.children:
        children.append(child)
    return children


def find_object(model, qname):
    """
    Search an object hierarchy for a qualified object name. Return a pointer to the object. 
    Example:

        find_object(
            bpy.data.objects["Boeing_E3.003"],
            ["Boeing_E3", "rotodome"]
        )

        will return the "rotodome.003" object in the "Boeing_E3.003" hierarchy.

    """
    
    if not model.name.startswith(qname[0]):
        # top object in model doesn't match qname
        logger.critical("Top object in model '%s' is not named %s", model.name, qname[0])
        sys.exit(1)
    else:
        obj = model
        # find subsequent qnames
        for level in range(1, len(qname)):
            children = get_child_objects(obj)
            found_child = False
            for child in children:
                if child.name.startswith(qname[level]):
                    found_child = True
                    obj = child
                    break
            if not found_child:
                # no child matched qname at this level
                logger.critical("Model '%s' does not contain an object named '%s'", model.name, ".".join(qname[:level+1]))
                sys.exit(1)
    # if all levels matched then we found the object
    return obj

def find_mesh(model, qname, mesh_prefix):
    """Find a mesh that is attached to a qualified object name"""

    # find the object by its qualified name
    obj = find_object(model, qname)

    # check if any meshes matching the prefix are associated with the target object
    mesh_found = None
    for mesh in bpy.data.meshes:
        if mesh.name.startswith(mesh_prefix):
            if obj.data == mesh:
                mesh_found = mesh

    # either no mesh matched the prefix or none of the matching meshes were associated with the object
    if not mesh_found:
        logger.critical("Object '%s' does not have mesh '%s'", " ".join(qname), mesh_prefix)
        sys.exit(1)

    return mesh_found

def find_material(material_name):
    """Find material by name"""

    for mat in bpy.data.materials:
        if mat.name == material_name:
            return mat

    # couldn't find a material with that name
    logger.critical("Couldn't find material named '%s'", material_name)
    sys.exit(1)

def find_root(collection):
    """Find the root object in a collection"""

    # find the object that has no parent
    children = []
    all_objects = list(collection.all_objects)
    for parent in all_objects:
        children.extend(list(parent.children))
    roots = list(set(all_objects) - set(children))

    # there should only be one root
    if len(roots) == 0:
        logger.critical("No root found in collection '%s'", collection.name)
        sys.exit(1)
    elif len(roots) > 1:
        logger.critical("Multiple roots found in collection '%s'", collection.name)
        sys.exit(1)

    return roots[0]
