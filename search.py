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
from npfl103.evaluation import do_eval, print_eval


__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__, add_help=True,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-r', '--root', action='store', default=None,
                        help='The assignment root. If given, the arguments --documents,'
                             ' --topics, --qrels, and --output will be interpreted'
                             ' relative to this location. It is recommended to use'
                             ' this argument.')

    parser.add_argument('-d', '--documents', action='store', required=True,
                        help='The documents list file.')
    parser.add_argument('-t', '--topics', action='store', required=True,
                        help='The topics list file.')
    parser.add_argument('-q', '--qrels', action='store', required=True,
                        help='The ground truth results file for the topics.')
    parser.add_argument('-o', '--output', action='store', required=True,
                        help='The file where your retrieval results will'
                             ' be stored.')
    parser.add_argument('-n', '--run_name', action='store', required=True,
                        help='How this experimental run should be named.')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Turn on INFO messages.')
    parser.add_argument('--debug', action='store_true',
                        help='Turn on DEBUG messages.')

    return parser


def main(args):
    logging.info('Starting main...')
    _start_time = time.clock()

    if args.root is not None:
        if not os.path.isdir(args.root):
            raise OSError('Root path is not a directory: {0}'.format(args.root))
        args.documents = os.path.join(args.root, args.documents)
        args.topics = os.path.join(args.root, args.topics)
        args.qrels = os.path.join(args.root, args.qrels)
        args.output = os.path.join(args.root, args.output)

    if not os.path.isfile(args.documents):
        raise OSError('Cannot find documents list: {0}'.format(args.documents))
    if not os.path.isfile(args.topics):
        raise OSError('Cannot find topics list: {0}'.format(args.topics))
    if not os.path.isfile(args.qrels):
        raise OSError('Cannot find ground truth file: {0}'.format(args.qrels))

    logging.info('Running retrieval pipeline with paths:'
                 '\n\troot: {0}\n\tdocuments: {1}\n\ttopics: {2}\n\tqrels: {3}'
                 ''.format(args.root, args.documents, args.topics, args.qrels))

    ###########################################################################
    logging.info('Building document pipeline for constructing similarity index.')

    coll_d = Collection(args.documents)

    # Now, apply your ideas!

    # - Configure the document and topic vectorizers here:
    document_vectorizer_class = BinaryVectorizer
    document_zones = ['TITLE', 'HEADING', 'TEXT']
    document_vtoken_field = 'form'
    document_token_filter = None

    # By default, the topic vectorizer shares most settings,
    # except for the zone.
    topic_vectorizer_class = document_vectorizer_class
    topic_zones = ['title']
    topic_vtoken_field = document_vtoken_field
    topic_token_filter = document_token_filter

    # The vectorizers share settings, except for the zones.
    document_vectorizer = document_vectorizer_class(
        zones=document_zones,
        field=document_vtoken_field,
        token_filter=document_token_filter
    )

    topic_vectorizer = topic_vectorizer_class(
        zones=topic_zones,
        field=topic_vtoken_field,
        token_filter=topic_token_filter
    )

    #
    #

    # Don't forget to name the TransformCorpus pipeline stages.
    vec_d = TransformCorpus(corpus=coll_d,
                            transform=document_vectorizer.transform,
                            name='document_vecs')

    # Other transformations go here.

    # The document vectors are then used to construct the similarity
    # index, which will later be applied as a transformation on the query
    # vectors. You can set a different k, of course.
    similarity_transform = Similarity(vec_d, k=10)

    ###########################################################################
    logging.info('Building query pipeline for getting similarity results.')

    coll_q = Collection(args.topics, document_cls=Topic)

    # Make sure to apply the transformations to the topics as well,
    # so that they end up in the same vector space.
    vec_q = TransformCorpus(corpus=coll_q,
                            transform=topic_vectorizer.transform,
                            name='query_vecs')

    query_similarity_corpus = TransformCorpus(corpus=vec_q,
                                              transform=similarity_transform,
                                              name='similarity')

    ###########################################################################
    logging.info('Running the query pipeline...')

    logging.info('\tWriting output to {0}'.format(args.output))
    if os.path.exists(args.output):
        logging.warn('Will overwrite output file!')

    with open(args.output, 'w') as output_stream:
        Similarity.write_trec(sim_corpus=query_similarity_corpus,
                              similarity=similarity_transform,
                              stream=output_stream,
                              run_name=args.run_name)

    ###########################################################################
    logging.info('Evaluating...')

    print_eval(truth_file=args.qrels,
               prediction_file=args.output)

    _end_time = time.clock()
    logging.info('search.py done in {0:.3f} s'.format(_end_time - _start_time))


if __name__ == '__main__':
    parser = build_argument_parser()
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    if args.debug:
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    main(args)
