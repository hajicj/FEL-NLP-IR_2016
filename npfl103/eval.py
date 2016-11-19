"""This module implements retrieval evaluation functions."""
from __future__ import print_function, unicode_literals

import collections

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


def parse_qrels(stream):
    """Reads the relevance annotations: one item per line,
    in the format ``tid iter docno rel``.

    The output data structure is a dict indexed by (tid, docno)
    pairs.

    >>> with open('test_data/test-qrels.txt') as hdl:
    ...     qrels = parse_qrels(hdl)
    >>> len(qrels)
    644

    Let's find all relevant document-topic pairs:

    >>> rel = [td for td, r in qrels.items() if r]
    >>> len(rel)
    51

    """
    qrels = collections.defaultdict(bool)

    for i, l in enumerate(stream):
        tid, _, docno, rel = l.strip().split()
        rel = int(rel)
        if (tid, docno) in qrels:
            raise ValueError('Qrels, line {0}: There cannot be repeated qrels'
                             ' for a topic, document pair! Topic: {1}, docno: {2}'
                             ''.format(i, tid, docno))
        qrels[(tid, docno)] = rel

    return qrels


def parse_result_ranks(stream):
    """Reads a results stream: one line per item, expected format:
    ``qid, iter, docno, rank, sim, run_id``.

    The output data structure is a dict indexed by (tid, docno)
    and the values are ranks.
    """
    ranks = collections.defaultdict(int)
    for i, l in enumerate(stream):
        tid, _, docno, rank, _, _ = l.strip().split()
        ranks[(tid, docno)] = int(rank)

    return ranks