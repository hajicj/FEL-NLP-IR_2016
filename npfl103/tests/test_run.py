#!/usr/bin/env python
"""This is a script that..."""
from __future__ import print_function, unicode_literals
import argparse
import logging
import os
import time

from npfl103.io import Collection, BinaryVectorizer, Topic
from npfl103.transform import TransformCorpus
from npfl103.similarity import Similarity

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.clock()

    # Your code goes here
    test_data_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data')
    doclist = os.path.join(test_data_root, 'test-documents.list')
    qlist = os.path.join(test_data_root, 'test-topics.list')
    outfile = os.path.join(test_data_root, 'test-output.res')
    print('Root: {0}'.format(test_data_root))

    coll_d = Collection(doclist)
    vec_d = TransformCorpus(coll_d, BinaryVectorizer().transform, 'document_vecs')
    sim = Similarity(vec_d, k=10)

    coll_q = Collection(qlist, document_cls=Topic)
    vec_q = TransformCorpus(coll_q, BinaryVectorizer().transform, 'query_vecs')
    sc = TransformCorpus(vec_q, sim, 'similarity')

    with open(outfile, 'w') as hdl:
        Similarity.write_trec(sc, sim, hdl, run_name='test_run')

    # To evaluate


    _end_time = time.clock()
    logging.info('test_run.py done in {0:.3f} s'.format(_end_time - _start_time))


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)
