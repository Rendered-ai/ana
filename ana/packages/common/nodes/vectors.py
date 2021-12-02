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

logger = logging.getLogger(__name__)


class Vector2D(Node):

    def exec(self):
        logger.info("Executing {}".format(self.name))
        # parse inputs
        x = float(self.inputs['x'][0])
        y = float(self.inputs['y'][0])
        return {"Vector": [x,y]}


class Vector3D(Node):

    def exec(self):
        logger.info("Executing {}".format(self.name))
        # parse inputs
        x = float(self.inputs['x'][0])
        y = float(self.inputs['y'][0])
        z = float(self.inputs['z'][0])
        return {"Vector": [x,y,z]}
