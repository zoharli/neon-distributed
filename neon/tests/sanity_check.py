# ----------------------------------------------------------------------------
# Copyright 2014 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Sanity check
"""
import argparse
import logging
import os
import sys
from neon.backends import gen_backend
from neon.util.persist import deserialize


def parse_args():
    parser = argparse.ArgumentParser(description='Run sanity check examples')
    parser.add_argument('--cpu', default=0, help='Run CPU sanity check',
                        type=int)
    parser.add_argument('--gpu', default="", help='Run GPU sanity check '
                        '(specify one of cudanet or nervanagpu')
    return parser.parse_args()


def sanity_check(conf_file, result, **be_args):
    experiment = deserialize(os.path.join(dir, conf_file))
    backend = gen_backend(model=experiment.model, **be_args)
    experiment.initialize(backend)
    res = experiment.run()
    print(float(res['test']['MisclassRate_TOP_1']))
    assert float(res['test']['MisclassRate_TOP_1']) == result


if __name__ == '__main__':
    # setup an initial console logger (may be overridden in config)
    logging.basicConfig(level=40)  # ERROR or higher
    res = 0
    args = parse_args()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    check_file = os.path.join(script_dir, '..', '..', 'examples',
                              'convnet', 'synthetic-sanity_check.yaml')
    expected_result = 0.5390625
    for be in ["cpu", "gpu"]:
        be_args = {'rng_seed': 0}
        if (args.__dict__[be] != 0 and args.__dict__[be] != "" and
                args.__dict__[be] != "0"):
            if be == "gpu":
                be_args[be] = args.__dict__[be]
            print('{} check '.format(be)),
            sanity_check(check_file, expected_result, **be_args)
            print('OK')
    sys.exit(res)
