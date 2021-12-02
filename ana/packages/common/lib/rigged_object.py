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
from abc import ABC
import logging
from ana.packages.common.lib.ana_object import AnaObject
import ana.packages.common.lib.context as ctx

logger = logging.getLogger(__name__)

class RiggedObject(AnaObject):

    def modify_rig(self):
        #Apply the modifiers in the dictionary to the specified objects

        if 'RigModifiers' not in self.config:
            print("WARNING: Rigged object does not have a modification list")
            return
        
        for modification in self.config["RigModifiers"]:

            Armature_name = modification['armature_name']
            Bone_name = modification['bone_name']

            Arm =  self.find_object([Armature_name])#First lets find the object we want to modifiy

            pose_bone = Arm.pose.bones[Bone_name]
            
            if modification['type']=='rotate':
                min = modification['min']
                max = modification['max']
                rot_axis = modification['axis']
                angle = min + ctx.random.random()*(max-min)
                angle_axis = [angle]
                angle_axis.extend(rot_axis)

                print("Rotating with", angle_axis)                
                pose_bone.rotation_mode = 'AXIS_ANGLE'
                pose_bone.rotation_axis_angle = angle_axis

                applied_as = {"Rotation (angle, axis)": angle_axis}

                self.modifiers.append({
                    "rig_modifier": {
                        "modifier": modification,
                        "rig_modifier_applied_as": applied_as
                    }  
                })

            if modification['type']=='translate':
                min = modification['min']
                max = modification['max']
                loc_axis = modification['axis']
                translation = min + ctx.random.random()*(max-min)
                translation_axis = [translation]
                translation_axis.extend(loc_axis)

                print("Translating ", translation)                
                pose_bone.location = (
                    loc_axis[0] * translation,
                    loc_axis[1] * translation,
                    loc_axis[2] * translation)

                applied_as = {"Translation (translation, axis)": translation_axis}

                self.modifiers.append({
                    "rig_modifier": {
                        "modifier": modification,
                        "rig_modifier_applied_as": applied_as
                    }  
                })

            else:
                print("WARNING: Unrecognized rig modification")

