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

"""
This script is called upon channel registration/deployment. It runs any tests defined in this directory.
"""
import sys
import argparse
import pytest

# get arguments from command line
argv = sys.argv
if "--" not in argv:
    argv = [] # no args were passed
else:
    argv = argv[argv.index("--") + 1:] # get all args after "--"

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--pytest', default="")
args = parser.parse_args(argv)

# execute pytest using arguments passed from command line
exit(pytest.main(args.pytest.split()))
