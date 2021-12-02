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
import argparse
import time
import logging
import yaml
import os
import ana.packages.common.lib.context as ctx
from ana.packages.common.lib.interp import interp

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    '''
    This is the main execution procedure for Ana. It takes a graph file as input
    and produces images and other synthetic artifacts.
    '''

    starttime = time.time()

    # get arguments from command line
    argv = sys.argv
    if "--" not in argv:
        argv = [] # no args were passed
    else:
        argv = argv[argv.index("--") + 1:] # get all args after "--"

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph', required=True)
    parser.add_argument('--channel', required=True)
    parser.add_argument('--loglevel', default="ERROR")
    parser.add_argument('--logfile', default=None)
    parser.add_argument('--seed', default=None, type=int)
    parser.add_argument('--interp_num', default=0, type=int)
    parser.add_argument('--preview', action="store_true", default=False)
    parser.add_argument('--output', default="./output")
    parser.add_argument('--data', default='./data')
    args = parser.parse_args(argv)

    # Create Ana
    try:
        ctx.initialize(
            channel_name=args.channel,
            seed=args.seed,
            interp_num=args.interp_num,
            preview=args.preview,
            output=args.output,
            data=args.data,
            loglevel=args.loglevel,
            logfile=args.logfile)
    except Exception as e:
        message = f"An exception of type {type(e).__name__} occurred while initializing channel"
        logging.error(message, exc_info=e)
        sys.exit(1)

    # load graph - supports yaml or json format
    try:
        if '/' not in args.graph:
            if '.yml' not in args.graph and os.path.isfile(f'./channels/{args.channel}/graphs/{args.graph}.yml'):
                args.graph = f'channels/{args.channel}/graphs/{args.graph}.yml'
            elif os.path.isfile(f'./channels/{args.channel}/graphs/{args.graph}'):
                args.graph = f'channels/{args.channel}/graphs/{args.graph}'
        with open(args.graph, "r") as f:
            input_graph = yaml.safe_load(f)
    except Exception as e:
        message = f"An exception of type {type(e).__name__} occurred while loading graph"
        logging.error(message, exc_info=e)
        sys.exit(1)

    try:
        interp(input_graph)
    except Exception as e:
        message = f"An exception of type {type(e).__name__} occurred while interpreting graph"
        logging.error(message, exc_info=e)
        sys.exit(1)


    print('Elapsed Time: {:.3f}sec'.format(time.time()-starttime))
