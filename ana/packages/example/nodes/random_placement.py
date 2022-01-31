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
import math
from ana.packages.common.lib.node import Node
from ana.packages.common.lib.generator import CreateBranchGenerator
import ana.packages.common.lib.context as ctx
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RandomPlacementClass(Node):
    """
    A class to represent the RandomPlacement node, a node that places objects in a scene.
    """

    def exec(self):
        """Execute node"""
        logger.info("Executing {}".format(self.name))

        try:
            # First we grab the generator method from the inputs
            branch_generator = CreateBranchGenerator(self.inputs["Object Generators"])

            object_number = min(200, int(self.inputs["Number of Objects"][0]))

            object_list = []

            for ii in np.arange(object_number):
                this_object = branch_generator.exec() #Picks a new branch from the inputs and executes it
                object_list.append(this_object)
                #.root is the actual blender object
                this_object.root.location = (
                    0.1*(ctx.random.random()-0.5),
                    0.1*(ctx.random.random()-0.5),
                    2+0.1*ii)
                this_object.root.rotation_euler = (
                    math.radians(ctx.random.uniform(0,360)),
                    math.radians(ctx.random.uniform(0,360)),
                    math.radians(ctx.random.uniform(0,360)))

        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise

        return {"Objects": object_list}
