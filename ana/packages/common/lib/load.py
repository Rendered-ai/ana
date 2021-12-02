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
A collection of utility functions that load assets from existing blender files 
"""
import bpy
from ana.packages.common.lib.search_utils import find_root

def load_model(blender_file_name, collection_name):
    '''
    Load a model. Assumes the model is in a collection and there
    is a single parent object for the model.
    Returns a pointer to the parent object.
    '''

    # load the collection
    new_collection = load_collection(blender_file_name, collection_name)
    
    # link it to the current scene
    bpy.context.scene.collection.children.link(new_collection)

    # find the root of the collection - there should only be one
    root = find_root(new_collection)

    return root

def load_collection(blender_file_name, collection_name):
    '''
    Load a collection.
    Returns a pointer to the collection.
    '''

    # load collection
    with bpy.data.libraries.load(filepath="//" + blender_file_name, link=False) as (_, dt):
        dt.collections = [collection_name]

    return dt.collections[0]

def load_material(blender_file_name, material_name):
    """
    Load a material from a blender file.
    Returns a pointer to the material.
    """

    with bpy.data.libraries.load(filepath="//" + blender_file_name, link=False) as (_, dt):
        dt.materials = [material_name]
    return dt.materials[0]


def load_text(blender_file_name, text_name):
    """
    Load a text from a blender file.
    Returns a pointer to the text file.
    """

    with bpy.data.libraries.load(filepath="//" + blender_file_name, link=False) as (_, dt):
        dt.texts = [text_name]
    return dt.texts[0]