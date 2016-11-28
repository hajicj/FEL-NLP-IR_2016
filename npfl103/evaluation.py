# -*- coding: utf-8 -*-
"""This module implements retrieval evaluation functions."""
from __future__ import print_function, unicode_literals

import collections
import os
import subprocess

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."

EVAL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'eval'))
if not os.path.isdir(EVAL_PATH):
    raise OSError('Cannot find path to evaluation executable: {0}'.format(EVAL_PATH))

EVAL_EXEC = os.path.join(EVAL_PATH, 'trec_eval')
if not os.path.isfile(EVAL_EXEC):
    raise OSError('Cannot find evaluation executable: {0}'.format(EVAL_EXEC))


def do_eval(truth_file, prediction_file, results_by_query=False):
    """Given a file with retrieval ground truth in the TREC format
    and a system retrieval output file, also in the appropriate TREC
    format (see assignment README for the format definition), runs
    the ``trec_eval`` script and parses the evaluation.

    Results from ``trec_eval`` looks e.g. like this:

      runid       all  test_run
      num_q       all  2
      map         all  0.0988

    The first column is the *field*, second is the query ID (or "all"
    for aggregate scores), third is the value of that field for the given
    query. We represent these results aggregated by query: a dict of dicts,
    where the top-level dict has query IDs for keys and the inner dict
    has field names for keys ('runid', 'num_q', etc.)

    :returns: A results dictionary.

        By default, the ``trec_eval`` script only outputs the aggregate
        scores. In that case, **we only return the query dict** for the
        aggregate query ``all``.

        If you want scores by individual queries, set the ``results_by_query``
        flag. Then, the result will be a dict of dicts.
    """

    # Construct argument string for trec_eval
    TREC_EVAL_ARGS = []
    if results_by_query:
        TREC_EVAL_ARGS.append('-q')

    args = [EVAL_EXEC] + TREC_EVAL_ARGS + [truth_file, prediction_file]
    result = subprocess.run(args, stdout=subprocess.PIPE)
    result_str = result.stdout.decode('utf-8')
    print(result_str)

    # Parsing results
    results_dict = collections.OrderedDict()
    for line in result_str.split('\n'):
        if len(line.strip()) == 0:
            continue
        field, query, value = line.strip().split()
        if query not in results_dict:
            results_dict[query] = collections.OrderedDict()

        results_dict[query][field] = value

    if len(results_dict) == 1 and 'all' in results_dict:
        results_dict = results_dict['all']

    return results_dict


def print_eval(truth_file, prediction_file, results_by_query=False):
    """Exactly the same as ``do_eval()``, but prints the evaluation results
    instead of returning them."""
    # Construct argument string for trec_eval
    TREC_EVAL_ARGS = []
    if results_by_query:
        TREC_EVAL_ARGS.append('-q')

    args = [EVAL_EXEC] + TREC_EVAL_ARGS + [truth_file, prediction_file]
    result = subprocess.run(args, stdout=subprocess.PIPE)
    result_str = result.stdout.decode('utf-8')
    print(result_str)


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