"""This module implements a class that..."""
from __future__ import print_function, unicode_literals
from npfl103.io.document import Document

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class DocumentVectorizer:
    """The DocumentVectorizer class transforms a Document to a sparse
    vector, represented by a dictionary. Dictionary keys are the terms
    in the document, values are just ``1`` for each term (we're using
    binary sparse vectors to represent the document).

    This class is the interface between the ``Document`` representation
    of the data, which is just a model of how the data is recorded,
    to a vector space.

    Note that you can build your own transformations of the vector
    space down the line. This is really just the conversion step. Don't
    worry about implementing e.g. the TF-IDF transformation at this point.

    >>> doc = Document('../test_data/LN-20020102001.vert')
    >>> tf = lambda t: t.pos == 'N'
    >>> vectorizer = DocumentVectorizer(zones=['title'], field='form', token_filter=tf)
    >>> v = vectorizer.transform(doc)
    >>> print(v)
    {'zemích': 1, 'lidí': 1, 'eura': 1, 'půlnoci': 1, 'miliony': 1, 'revoluce': 1, 'kontinentu': 1, 'peníze': 1, 'dějinách': 1}

    Making better vectorizers
    -------------------------

    When subclassing the Vectorizer, you will have to think about
    two things. First, what are your terms going to be? And second,
    how are you going to weigh them?

    The answer to the first question will be things like "word forms"
    or "lemmas" or "disambiguated lemmas and part of speech tags" --
    the fields that you have at your disposal in the tokens. You can
    even do n-grams, if you feel like it.

    The answer to the second question might be "1" or "term frequency
    in the document" or "pivot-normalized term frequency".

    Both of these decisions are done in the
    :meth:`DocumentSparseVectorizer.transform` method. The input of this
    method is a :class:`Document`, the output is a dict with term keys
    and term weight values. However, for the second part -- how weights
    are decided -- it's better to defer transformations of term weights
    later down the line.
    """

    def __init__(self, zones=None, **vtext_to_stream_kwargs):
        """Initialize the vectorizer."""
        self.zones = zones
        self.vtext_to_stream_kwargs = vtext_to_stream_kwargs

    def transform(self, document):
        """Transforms an incoming document into a dict of tokens.

        Default terms: word forms

        Default weights: 1 for each term that appears in the document.
        """
        output = {}
        for term in document.tokens(zones=self.zones,
                                    **self.vtext_to_stream_kwargs):
            output[term] = 1
        return output
