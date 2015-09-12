# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
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

import cPickle
from functools import partial
from glob import glob
from multiprocessing import Pool
import os
import struct


def convert_file(iopair, keylist):
    '''
    Function for converting from an imageset batch cpickle file into a
    flat binary with a choice of keys.
    Input file is cpickled dict with the following fields:
    dict['data']:  list of jpeg strings
    dict['labels']: dict of integer lists, default is 'l_id' for the category
                    label of the corresponding jpeg.

    The following condition should be true (a label for each jpeg)
        len(dict['data']) == len(dict['labels']['l_id'])

    Args:
        iopair (tuple) : Names of input and output files.
        keylist(list) : A list of keys to be used in the flat binary file.
    '''
    ifname, ofname = iopair
    with open(ifname, 'r') as ifp:
        print "Converting ", ifname
        tdata = cPickle.load(ifp)
        jpegs = tdata['data']
        labels = tdata['labels']
        num_imgs = len(jpegs)

        with open(ofname, 'wb') as f:
            f.write(struct.pack('I', num_imgs))
            f.write(struct.pack('I', len(keylist)))

            for key in keylist:
                ksz = len(key)
                f.write(struct.pack('L' + 'B' * ksz, ksz, *bytearray(key)))
                f.write(struct.pack('I' * num_imgs, *labels[key]))

            for i in range(num_imgs):
                jsz = len(jpegs[i])
                bin = struct.pack('I' + 'B' * jsz, jsz, *bytearray(jpegs[i]))
                f.write(bin)

# Location of original imageset batches generated by batch writer
IPATH = '/usr/local/data/I1K/cc2_imageset_batches'

# Location of where we'll dump out flat binary imageset batches
OPATH = '/usr/local/data/I1K/imageset_batches_dw'

ifiles = glob(os.path.join(IPATH, "data_batch_*"))
ofiles = [fname.replace(IPATH, OPATH) for fname in ifiles]
keylist = ['l_id']

pool = Pool(processes=8)
pool.map(partial(convert_file, keylist=keylist), zip(ifiles, ofiles))