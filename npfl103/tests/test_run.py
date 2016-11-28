#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is a script that..."""
from __future__ import print_function, unicode_literals
import argparse
import logging
import os
import pprint
import time

from npfl103.io import Collection, BinaryVectorizer, Topic
from npfl103.transform import TransformCorpus
from npfl103.similarity import Similarity
from npfl103.evaluation import do_eval, print_eval

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

    test_data_root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_data')
    doclist = os.path.join(test_data_root, 'test-documents.list')
    qlist = os.path.join(test_data_root, 'test-topics.list')
    outfile = os.path.join(test_data_root, 'test-output.res')

    logging.info('Test data root: {0}'.format(test_data_root))

    logging.info('Constructing document pipeline for building similarity index.')
    coll_d = Collection(doclist)
    vec_d = TransformCorpus(coll_d, BinaryVectorizer().transform, 'document_vecs')
    sim = Similarity(vec_d, k=10)

    logging.info('Constructing query pipeline for getting similarity results.')
    coll_q = Collection(qlist, document_cls=Topic)
    vec_q = TransformCorpus(coll_q, BinaryVectorizer().transform, 'query_vecs')
    sc = TransformCorpus(vec_q, sim, 'similarity')

    logging.info('Running the queries')
    with open(outfile, 'w') as hdl:
        Similarity.write_trec(sc, sim, hdl, run_name='test_run')

    # Evaluation
    truth_file = os.path.join(test_data_root, 'test-qrels.txt')
    pred_file = outfile

    # We could do something fancy with the results if we capture them, like this:
    # results = do_eval(truth_file, pred_file)

    # But now we only print them.
    print_eval(truth_file, pred_file)

    # If we wanted detailed results by individual query topics, we'd do this:
    # print_eval(truth_file, pred_file, results_by_query=True)

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
