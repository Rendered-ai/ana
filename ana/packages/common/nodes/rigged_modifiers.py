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
import logging
from ana.packages.common.lib.node import Node
from ana.packages.common.lib.generator import ObjectModifier
from ana.packages.common.lib.rigged_object import RiggedObject

logger = logging.getLogger(__name__)


class RandomizeRig(Node):
    """Implement a dent modifier on objects"""

    def exec(self):
        logger.info("Executing {}".format(self.name))
        children = self.inputs["object_generator"]

        # add modifier to generator tree
        generator = ObjectModifier(
            method=RiggedObject.modify_rig.__name__,
            children=children)
        return {"object_generator": generator}
