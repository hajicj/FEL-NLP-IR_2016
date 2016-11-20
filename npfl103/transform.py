"""This module implements a class that..."""
from __future__ import print_function, unicode_literals

import pprint

from npfl103.io import Collection

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class TransformCorpus(object):
    """The TransformedCollection class is the building block
    of vector space transformation pipelines. On initialization,
    supply a callable that takes a sparse vector in __call__ and outputs
    another sparse vector (remember that sparse vectors are implemented
    as just dicts, see the :class:`DocumentVectorizer`), and a corpus
    to transform.

    Example
    -------

    Let's run through the pipeline of reading a collection of documents
    and mapping it into a vector space.

    >>> from npfl103.io import Collection
    >>> c = Collection('test_data/test-documents-tiny.list')

    Let's use straightforward term frequencies in the extracted vectors:

    >>> from npfl103.io import TermFrequencyVectorizer
    >>> vectorizer = TermFrequencyVectorizer(field='lemma')
    >>> vdocs = (vectorizer.transform(doc) for doc in c)

    (Note the generator expression. This also means you can only
    iterate over it once. This is fine for now; we'll get back to it later.)

    Let's transform the feature vectors using straightforward
    normalization:

    >>> def normalize(vec):   # Assumes that term frequencies are used
    ...     document_length = sum(vec.values())
    ...     return {k: v / document_length for k, v in vec.items()}
    >>> tcorp = TransformCorpus(corpus=vdocs, transform=normalize, name='normalize')

    Notice that we provided a ``name`` to the ``TransformCorpus``.
    This is just a practicality, but having to think of names for stages
    of your pipeline is a good practice to avoid a *lot* of pain down
    the line when doing experiments, so we went ahead and enforced it.

    Let's now look at the transformed documents. We can look at the
    relative frequencies of the 10 most frequent words:

    >>> nvecs = [v for v in tcorp]    # Not a generator this time.
    >>> top10 = sorted(nvecs[0].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:10]

    (We sort by both relative frequency and name, to avoid unstable sort
    conflicts messing up our doctest...)

    >>> pprint.pprint(top10)
    [(',', 0.10526315789473684),
     ('.', 0.04736842105263158),
     ('v', 0.02894736842105263),
     ('se', 0.02631578947368421),
     ('a', 0.02631578947368421),
     ('euro', 0.02368421052631579),
     ('na', 0.018421052631578946),
     ('nový', 0.013157894736842105),
     ('měna', 0.013157894736842105),
     ('evropský', 0.013157894736842105)]

    This isn't a very good representation for retrieval, is it? Maybe
    the commas and periods and conjunctions like 'a' or 'v' are not
    very relevant to the content of the document. We could try applying
    the IDF transform to reflect their unhelpfulness in distinguishing
    documents relevant and irrelevent to a given query, or we could
    exploit the rich linguistic information that we have.

    Let's try the second approach now and only keep the nouns.

    >>> tf = lambda t: t.pos in ['N']
    >>> vectorizer = TermFrequencyVectorizer(field='lemma', token_filter=tf)
    >>> vdocs = (vectorizer.transform(doc) for doc in c)
    >>> tcorp = TransformCorpus(vdocs, normalize, name='normalize')
    >>> vecs = [v for v in tcorp]
    >>> top10 = sorted(vecs[0].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:10]
    >>> pprint.pprint(top10)
    [('euro', 0.06766917293233082),
     ('měna', 0.03759398496240601),
     ('země', 0.03007518796992481),
     ('miliarda`1000000000', 0.022556390977443608),
     ('0', 0.022556390977443608),
     ('Španělsko', 0.015037593984962405),
     ('Řecko', 0.015037593984962405),
     ('člověk', 0.015037593984962405),
     ('zpráva', 0.015037593984962405),
     ('unie', 0.015037593984962405)]

    ...Better?

    Where do the clever parts go?
    -----------------------------

    Into the transform callable, not into the TransformedCorpus.

    The TransformedCorpus is just a technical class that allows chaining
    transformations into pipelines with a constant memory footprint.
    The "clever" stuff has to happen in the supplied transformation callable,
    and if the transformer needs to iterate through the corpus before it is
    operational (like for instance the IDF transform -- it needs to compute
    for each term how many documents contain it), it needs to get
    the collection at its initialization.

    Relationship between TransformedCorpus and Vectorizer
    -----------------------------------------------------

    **TL;DR:** TransformCorpus is not designed to deal with sequential
    data. The job of the Vectorizer is to convert sequential documents
    to non-sequential vectors. But to make it more elegant and easily
    re-iterable, it pays to wrap the Vectorizer into a TransformCorpups.

    The Vectorizer could in principle be implemented as a TransformCorpus
    where the ``transform`` callable passed to the TransformCorpus
    can deal with the :class:`Document` object. However, we decided
    to keep these two things separate: the Vectorizer deals with converting
    the corpus of Documents to sparse vectors, the TransformCorpus
    object deals with pipelining operations in the vector space.
    It's more of a clarity/comprehensibility thing.

    And to put it together, if you want a TransformedCorpus to apply
    the vectorizer, it's quite straightforward:

    >>> vectorizer = TermFrequencyVectorizer(field='lemma', token_filter=tf)
    >>> vec_transform = lambda doc: vectorizer.transform(doc)
    >>> vectorization_tcorp = TransformCorpus(c, vec_transform, name='vec')

    And onwards just like before:

    >>> tcorp = TransformCorpus(vectorization_tcorp, normalize, name='normalize')
    >>> vecs = [v for v in tcorp]
    >>> top10 = sorted(vecs[0].items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:10]
    >>> pprint.pprint(top10)
    [('euro', 0.06766917293233082),
     ('měna', 0.03759398496240601),
     ('země', 0.03007518796992481),
     ('miliarda`1000000000', 0.022556390977443608),
     ('0', 0.022556390977443608),
     ('Španělsko', 0.015037593984962405),
     ('Řecko', 0.015037593984962405),
     ('člověk', 0.015037593984962405),
     ('zpráva', 0.015037593984962405),
     ('unie', 0.015037593984962405)]

    This does have one advantage: the iteration is repeatable. A simple
    generator expression like the one we used for vectorization is
    a fire-and-forget operation, but using the TransformCorpus enables repeated
    iteration with the nicely small generator memory footprint.

    Getting the IDs
    ---------------

    To make retrieval results traceable, we need to be able to see
    which document is which after running the transformation. We don't
    compute that explicitly - we provide a ``collection()`` method
    that returns the underlying Collection, which in turn has the
    ``get_uid(idx)`` method that retrieves the UID of the ``idx``-th
    collection member (document or topic).

    >>> coll = tcorp.collection
    >>> len(coll)
    4
    >>> coll.get_uid(2)
    'LN-20020102101'

    """
    def __init__(self, corpus, transform, name):
        """Initialize MyClass."""
        self.corpus = corpus
        self.transform = transform

        self.name = name

    def __iter__(self):
        for doc in self.corpus:
            yield self.transform(doc)

    @property
    def collection(self):
        """Dive down to recover the underlying Collection. Useful
        mostly for recovering document IDs (docno for outputting query
        results).
        """
        if isinstance(self.corpus, Collection):
            return self.corpus
        elif isinstance(self.corpus, TransformCorpus):
            return self.corpus.collection
        else:
            raise ValueError('Cannot get collection if self.corpus type'
                             ' is {0}'.format(type(self.corpus)))
