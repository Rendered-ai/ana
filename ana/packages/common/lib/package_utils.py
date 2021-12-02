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
import os
import ana.packages.common.lib.context as ctx

def get_volume_path(package, inpath):
    """
    Convert a volume path to an absolute path
    """
    if ":" in inpath:
        # path includes a volume
        volume_name, rel_path = inpath.split(":")
        volume_path = ctx.packages[package]['volumes'][volume_name]
        if os.path.isabs(volume_path):
            # volume is an absolute path
            return os.path.join(volume_path, rel_path)
        else:
            # volume is relative to "--data" parameter
            return os.path.join(ctx.data, volume_path, rel_path)
    else:
        # path does not include a volume
        if os.path.isabs(inpath):
            # path is absolute
            return inpath
        else:
            # path is relative to "--data" parameter
            return os.path.join(ctx.data, inpath)

