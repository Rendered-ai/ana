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
import ana.packages.common.lib.context as ctx
import logging

logger = logging.getLogger(__name__)
loglevel = logging.getLogger().level

def setup():
    """Perform setup operations prior to executing nodes in the graph"""
    # reset blender
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)
        
    for particle in bpy.data.particles:
        bpy.data.particles.remove(particle, do_unlink=True)
        
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat, do_unlink=True)

    # rename the original scene and view layer to be the channel name
    scene = bpy.data.scenes['Scene']
    scene.name = ctx.channel.name
    scene.view_layers['View Layer'].name = ctx.channel.name

    #bpy.ops.preferences.addon_enable(module="BlendLuxCore")
    bpy.context.scene.render.engine = 'CYCLES'
    cyclesprefs = bpy.context.preferences.addons['cycles'].preferences
    optix_devices = cyclesprefs.get_devices_for_type('OPTIX')
    cuda_devices = cyclesprefs.get_devices_for_type('CUDA')
    cpu_devices = cyclesprefs.get_devices_for_type('CPU')
    if len(optix_devices):
        cyclesprefs.compute_device_type = 'OPTIX'
        scene.cycles.device  = 'GPU'
        scene.cycles.feature_set = 'EXPERIMENTAL'
        for device in optix_devices:
            device.use = True
            logger.info(f"Enabled OPTIX device {device.name}.")
    elif len(cuda_devices):
        cyclesprefs.compute_device_type = 'CUDA'
        scene.cycles.device  = 'GPU'
        scene.cycles.feature_set = 'EXPERIMENTAL'
        for device in cuda_devices:
            device.use = True
            logger.info(f"Enabled CUDA device {device.name}.")
    else:
        scene.cycles.device  = 'CPU'
        scene.cycles.feature_set = 'EXPERIMENTAL'
        for device in cpu_devices:
            device.use = True
            logger.info(f"Enabled CPU device {device.name}.")
