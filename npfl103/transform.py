"""This module implements a class that..."""
from __future__ import print_function, unicode_literals

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class TransformedCorpus(object):
    """The TransformedCollection class is the building block
    of vector space transformation pipelines. On initialization,
    supply a callable that takes a sparse vector in __call__ and outputs
    another sparse vector (remember that sparse vectors are implemented
    as just dicts, see the :class:`DocumentVectorizer`), and a corpus
    to transform:

    >>> c =

    This is just a technical class that allows chaining transformations
    into pipelines with a constant memory footprint. The "clever" stuff
    has to happen in the supplied transformation callable, and if the
    transformer needs to iterate through the corpus before it is operational
    (like for instance the IDF transform -- it needs to compute for each
    term how many documents contain it), it needs to get the collection
    so far at its initialization.

    """
    def __init__(self, corpus, transform):
        """Initialize MyClass."""
        self.corpus = corpus
        self.transform = transform

    def __iter__(self):
        for doc in self.corpus:
            yield self.transform(doc)
