# -*- coding: utf-8 -*-
"""This module implements a class that..."""
from __future__ import print_function, unicode_literals

import logging
import operator
from math import inf

from npfl103.io import format_as_results

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class Similarity:
    """The Similarity class transforms a query vector from the term
    vector space to the similarity space of a collection.

    The transform returns a "sparse" vector where the "terms" are
    document indexes into the underlying corpus and the "weights"
    are similarity scores of the query to the i-th document in the collection.

    You can also supply a ``k`` parameter to only return the top ``k``
    closest documents. This makes the output vector sparse, and thus
    manageable for large collections.

    It is assumed that higher scores mean the document is more relevant.

    Using Similarity
    ----------------

    The :class:`Similarity` is a *transformer*, not a corpus. It is passed
    as the ``transform`` argument of a TransformedCorpus with queries.
    The collection of documents that should be queried is passed to the
    Similarity transformer at *initialization*. Observe:

    >>> from npfl103.io import Collection, BinaryVectorizer, Topic
    >>> from npfl103.transform import TransformCorpus

    >>> coll_d = Collection('test_data/test-documents-tiny.list')
    >>> vec_d = TransformCorpus(coll_d, BinaryVectorizer().transform, 'document_vecs')
    >>> sim = Similarity(vec_d, k=10)   # It's 10 by default.

    Now build the query corpus:

    >>> coll_q = Collection('test_data/test-topics.list', document_cls=Topic)
    >>> ts = [t for t in coll_q]
    >>> len(ts)
    2

    >>> vec_q = TransformCorpus(coll_q, BinaryVectorizer().transform, 'query_vecs')

    Once again: the ``Similarity`` class transforms the *query* to the
    *similarity space*. Like this:

    >>> sc = TransformCorpus(vec_q, sim, 'similarity')
    >>> similarity_outputs = [s for s in sc]
    >>> len(similarity_outputs)
    2
    >>> similarity_outputs[0]
    {0: 6.0, 1: 11.0, 2: 6.0, 3: 6.0}

    Outputting the results
    ----------------------

    Pass the similarity TransformCorpus to the ``Similarity.write_trec()``
    method.

    >>> import io
    >>> hdl = io.StringIO()
    >>> Similarity.write_trec(sc, sim, hdl, run_name='test')

    Afterwards, use the TREC evaluation script ``trec_eval`` to evaluate
    the results. (Of course, we would write to a file which is then
    read by TREC.)

    """

    def __init__(self, corpus, k=10):
        """Initialize the Similarity.

        If you set ``k=None``, the transform will return the similarity
        scores for all documents in the collection (which might not fit
        into memory!), so use that with care.
        """
        self.corpus = corpus
        self.k = k

        # Collects document IDs
        self._corpud_ids = None

    def score(self, query, document):
        """This is the "clever" part: given two (sparse) vectors
        in the same space, how do you compute their distance and/or
        similarity? By default, the score is the dot-product of
        the two sparse vectors."""
        output = 0.0
        for term, w in query.items():
            if term in document:
                output += w * document[term]
        return output

    def __call__(self, query):
        # Could theoretically be implemented by setting the internal K to math.inf
        if self.k is None:
            return {i: self.score(query, d) for i, d in enumerate(self.corpus)}

        candidates = {-1: -inf}
        _current_min_score = -inf
        _current_min_idx = -1

        for i, d in enumerate(self.corpus):
            score = self.score(query, d)
            if score > _current_min_score:
                if len(candidates) == self.k:
                    del candidates[_current_min_idx]
                candidates[i] = score
                _current_min_idx, _current_min_score = min(candidates.items(),
                                                           key=operator.itemgetter(1))

        # Filter out the remaining -1s in case corpus smaller than k
        output = {i: sim for i, sim in candidates.items() if i >= 0}
        return output

    @staticmethod
    def write_trec(sim_corpus, similarity, stream, run_name='default_run'):
        doc_collection = similarity.corpus.collection
        topic_collection = sim_corpus.collection
        for i, query_results in enumerate(sim_corpus):
            s = format_as_results(query_results,
                                  topic_uid=topic_collection.get_uid(i),
                                  doc_collection=doc_collection,
                                  run_name=run_name)
            stream.write(s)
            # logging.warning('Wrote\n{0}\nto stream'.format(s))
            stream.write('\n')
