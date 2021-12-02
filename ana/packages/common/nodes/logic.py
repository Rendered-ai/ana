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
from ana.packages.common.lib.node import Node

logger = logging.getLogger(__name__)


class ConditionalSelector(Node):

    def exec(self):
        logger.info("Executing {}".format(self.name))
        # parse the inputs
        value = None
        a = float(self.inputs['ConditionA'][0])
        operator = str(self.inputs['Operator'][0])
        b = float(self.inputs['ConditionB'][0])
        t = self.inputs['True'][0]
        f = self.inputs['False'][0]
        if operator == "Less Than":
            if a < b:   value = t
            else:       value = f
        elif operator == "Equal To":
            if a == b:  value = t
            else:       value = f
        elif operator == "Greater Than":
            if a > b:   value = t
            else:       value = f
        else:
            logger.error("Encountered invalid value for Operator: {}. Exiting...".format(operator))
            sys.exit(1)
        return {"Value": value}
