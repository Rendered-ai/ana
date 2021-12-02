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


class ObjectToDictionary(Node):
    """Store an object as a key/value pair in a dictionary"""

    def exec(self):
        """Execute node"""
        logger.info("Executing {}".format(self.name))
        object_name = self.inputs["object_name"][0]
        obj = self.inputs["object"][0]
        output_dict = {object_name: obj}
        
        return {"dict": output_dict}
