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
import bpy, os, bpy_extras, mathutils, numpy, cv2, json, logging, imageio
import ana.packages.common.lib.context as ctx
from  ana.packages.common.lib.camera_checks import collect_mesh_objects

logger = logging.getLogger(__name__)
loglevel = logging.getLogger().level
MIN_FEATURE_SIZE = 2  # Minimum value of 2 - bboxs with boundingRect h=1, have bbox h=0

def compute_polygons(obj):
    """ Generates the polygon from a mask segmentation and bounding box array. """
    maskfile = obj.mask.replace('#', str(obj.active_scene.frame_current))
    poly,bbox = [],None
    img = imageio.imread(maskfile)
    img = numpy.where(img == obj.instance, 255, 0).astype(numpy.uint8)
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    for c in contours:
        a = c.flatten()
        for i in a: poly.append(i)
    polyarr = numpy.array(poly, dtype=numpy.int32)
    poly = polyarr.reshape(int(len(polyarr)/2), 2)
    x,y,w,h = cv2.boundingRect(poly)
    if w < MIN_FEATURE_SIZE or h < MIN_FEATURE_SIZE: poly,bbox = None,None
    else: 
        bbox = [int(val) for val in [x,y,w-1,h-1]]
        poly = [[int(val) for val in numpy.array(poly).flatten()]]
    return poly, bbox

def total_bound_box(obj):
    #returns a bound box for object and all it's children
    mesh_objects = collect_mesh_objects(obj)
    bbox = mesh_objects[0].bound_box

    xmin = bbox[0][0]
    xmax = bbox[0][0]
    ymin = bbox[0][1]
    ymax = bbox[0][1]
    zmin = bbox[0][2]
    zmax = bbox[0][2]

    for mesh_object in mesh_objects:

        for coord in mesh_object.bound_box:
            if coord[0] < xmin: xmin=coord[0]
            if coord[0] > xmax: xmax=coord[0]
            if coord[1] < ymin: ymin=coord[1]
            if coord[1] > ymax: ymax=coord[1]
            if coord[2] < zmin: zmin=coord[2]
            if coord[2] > zmax: zmax=coord[2]

    return [xmin,xmax,ymin,ymax,zmin,zmax]




def compute_bbox3d(obj):
    blendobj = obj.root
    if blendobj.type in ['EMPTY', 'ARMATURE']: blendobj = blendobj.children[0]
    bboxcoords = [blendobj.matrix_world @ mathutils.Vector(coord) for coord in blendobj.bound_box]
    bbox3d = []
    for coord in bboxcoords:
        camcoord = bpy_extras.object_utils.world_to_camera_view(obj.active_scene, obj.active_scene.camera, coord)
        bbox3d.append( int(camcoord[0]*obj.active_scene.render.resolution_x) )
        bbox3d.append( int((1-camcoord[1])*obj.active_scene.render.resolution_y) )
        bbox3d.append( camcoord[2] )
    return [val for val in bbox3d]


def compute_centroid(obj):
    blendobj = obj.root
    if blendobj.type in ['EMPTY', 'ARMATURE']: blendobj = blendobj.children[0]
    bboxcoords = [blendobj.matrix_world @ mathutils.Vector(coord) for coord in blendobj.bound_box]
    center = sum((mathutils.Vector(b) for b in bboxcoords), mathutils.Vector()) / 8
    camcoord = bpy_extras.object_utils.world_to_camera_view(obj.active_scene, obj.active_scene.camera, center)
    x = int(camcoord[0]*obj.active_scene.render.resolution_x)
    y = int((1-camcoord[1])*obj.active_scene.render.resolution_y)
    return [y,x], camcoord[2]


def compute_rle(obj):
    maskfile = obj.mask.replace('#', str(obj.active_scene.frame_current))
    img = imageio.imread(maskfile)
    rle = { 'size':img.shape, 'counts':[] }
    count = 1
    prev = [0,0,0]
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if not (img[y,x] == prev).all():
                rle['counts'].append(count)
                prev = img[y,x]
                count = 1
            else: count += 1
    return rle


def truncated(obj, bbox):
    if bbox is None:
        return
    x, y, w, h = bbox
    if x == 0 or y == 0:
        return True
    maskfile = obj.mask.replace('#', str(obj.active_scene.frame_current))
    img = imageio.imread(maskfile)
    if x+w+1 == img.shape[0] or y+h+1 == img.shape[1]:
        return True
    return False


def compute_size(obj):
    """ Return x,y,z or length, width, depth. """
    return [c for c in obj.root.dimensions]


# https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
def euler_from_quaternion(x, y, z, w):
    """
    Convert a quaternion into euler angles (roll, pitch, yaw)
    roll is rotation around x in radians (counterclockwise)
    pitch is rotation around y in radians (counterclockwise)
    yaw is rotation around z in radians (counterclockwise)
    """
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = numpy.arctan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = numpy.arcsin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = numpy.arctan2(t3, t4)

    return [roll_x, pitch_y, yaw_z]  # in radians


def compute_rotation(obj):
    """ Return Euler angles: roll, pitch, and yaw. """
    loc, rot, scale = obj.root.matrix_world.decompose()

    roll, pitch, yaw = None, None, None
    # Test me
    # if type(rot) == mathutils.Euler:
    #     rot.order = 'XYX'
    #     roll, pitch, yaw = rot

    if type(rot) == mathutils.Quaternion:
        w, x, y, z = rot
        roll, pitch, yaw = euler_from_quaternion(x, y, z, w)

    return roll, pitch, yaw


def compute_obstruction(obj):
    """Estimate the amount of an object's mask is hidden from view of the camera. 0 - full view; 1 - out of view. """
    maskfilebase, maskext = obj.mask.replace('#', str(obj.active_scene.frame_current)).rsplit('.', 1)
    solomaskfile = '{}-{}.{}'.format(maskfilebase, obj.solo_mask_id, maskext)

    if obj.solo_mask_id:
        soloimg = imageio.imread(solomaskfile)
    else:
        # print('Object {} has no mask'.format(obj.instance))
        return None  # unknown - object could be outside image boundary

    compositemaskfile = obj.mask.replace('#', str(obj.active_scene.frame_current))
    compimg = imageio.imread(compositemaskfile)
    compmask = numpy.nonzero(compimg == obj.instance)[0]

    solononzero = soloimg[numpy.nonzero(soloimg)]
    pix_id = numpy.unique(solononzero)[1]  # the second entry is the first entry + obj.instance
    solomask = numpy.nonzero(soloimg == pix_id)[0]

    obstruction = 1.0 - len(compmask) / len(solomask)

    return obstruction
