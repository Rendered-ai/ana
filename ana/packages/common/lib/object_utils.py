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
import bpy

def create_plane(width, height):
    """
    Create a plane of size width x height located at the origin.

    Note:
        This is preferrable to bpy.ops.mesh.primitive_plane_add
        because it doesn't automatically add the plane to
        a collection.
    """

    # define dimensions
    verts = [
        (-width/2.0, -height/2.0, 0),
        (width/2.0, -height/2.0, 0),
        (width/2.0, height/2.0, 0),
        (-width/2.0, height/2.0, 0)
    ]
    faces = [(0, 1, 2, 3)]
    
    # create mesh
    mesh = bpy.data.meshes.new("plane")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)

    # add UV layer
    mesh.uv_layers.new()

    # create the plane
    plane = bpy.data.objects.new("plane", mesh)
    plane.location = (0, 0, 0)

    return plane
