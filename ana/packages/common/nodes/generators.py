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
import numpy
from ana.packages.common.lib.node       import Node
from ana.packages.common.lib.generator  import CreateBranchGenerator

logger = logging.getLogger(__name__)


class SelectGenerator(Node):
    def exec(self):
        """ Select a generator from a list of generators. """
        logger.info("Executing {}".format(self.name))
        try:
            children = numpy.array(self.inputs["Generators"]).flatten()
            generator = CreateBranchGenerator(children=children)
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise
        return {"Generator": generator} 


class Weight(Node):
    """ Add modify the weight of a generator/modifier """
    def exec(self):
        logger.info("Executing {}".format(self.name))

        if len(self.inputs["Generator"]) != 1:
            logger.error("Weight 'generator' input port requires exactly 1 link")
            raise ValueError
        generator = self.inputs["Generator"][0]
        try:
            generator.weight = float(self.inputs["Weight"][0])
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise
        return {"Generator": generator}


class SetInstanceCount(Node):
    """ Set the count property of a generator to produce multiple instances. """
    def exec(self):
        logger.info("Executing {}".format(self.name))

        if len(self.inputs["Generator"]) != 1:
            logger.error("SetInstanceCount 'generator' port requires exactly 1 link.")
            raise ValueError
        generator = self.inputs["Generator"][0]
        try:
            generator.count = int(self.inputs["Count"][0])
        except Exception as e:
            logger.error("{} in \"{}\": \"{}\"".format(type(e).__name__, type(self).__name__, e).replace("\n", ""))
            raise
        return {"Generator": generator}
