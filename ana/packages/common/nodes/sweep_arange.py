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
import numpy as np
import ana.packages.common.lib.context as ctx
from ana.packages.common.lib.node import Node

logger = logging.getLogger(__name__)


class SweepArange(Node):
    """Do a parameter sweep across evenly spaced values within a half-open interval [start,stop)"""

    def exec(self):
        """Execute node"""
        logger.info("Executing {}".format(self.name))

        start = float(self.inputs["start"][0])
        stop = float(self.inputs["stop"][0])
        step = float(self.inputs["step"][0])

        values = np.arange(start, stop, step)
        value = values[ctx.interp_num % len(values)]

        logger.debug("Arange value = %s", value)

        return {"value": value}
