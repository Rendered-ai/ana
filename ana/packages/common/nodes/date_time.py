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
import datetime
import pytz
import julian
from ana.packages.common.lib.node import Node

logger = logging.getLogger(__name__)


class DateTime(Node):
    """
    Create a date/time
    """

    def exec(self):
        """Execute node"""
        logger.info("Executing {}".format(self.name))

        # get inputs
        datetime_in = self.inputs["datetime"][0]
        try:
            if isinstance(datetime_in, datetime.datetime):
                pass
            elif isinstance(datetime_in, str):
                datetime_in = datetime.datetime.fromisoformat(self.inputs["datetime"][0])
            else:
                raise ValueError
        except ValueError:
            logger.error("Input value 'datetime' must be in ISO 8601 format")
            raise

        # if the datetime isn't timezone aware then assume utc
        if datetime_in.tzinfo is None:
            datetime_in.replace(tzinfo=pytz.UTC)

        # convert to utc and julian formats
        datetime_out_utc = datetime_in.isoformat()
        logger.debug("Datetime UTC: %s", datetime_out_utc)
        datetime_out_julian = julian.to_jd(datetime_in)
        logger.debug("Datetime Julian: %s", datetime_out_julian)

        return {"utc": datetime_out_utc, "julian": datetime_out_julian}
