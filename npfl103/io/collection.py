"""This module implements a class that..."""
from __future__ import print_function, unicode_literals
import logging
import os

import xml.etree.ElementTree as ET

import time

from npfl103.io.document import Document
from npfl103.io.topic import Topic

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class Collection:
    """This class represents the entire collection of documents
    in the assignment.

    The Collection is initialized with the ``document.list`` file that
    contains paths to the individual documents. It is assumed the
    paths in the document list file are relative to the location of
    that file -- if not, you can use the ``docpath`` parameter
    to set the prefix to the document paths in the list file.
    (For instance, if you have absolute paths in ``documents.list``,
    you would use ``docpath=''``.)

    >>> corpus = Collection('../test_data/test-documents-tiny.list')
    >>> len(corpus)
    4
    >>> print(corpus[0].texts[0].to_text(sentence_idxs=[1, 3]))
    leden provázely v celé Evropě bouřlivé oslavy a ohňostroje .
    " Nevypadají jako opravdové .

    The Collection supports iteration over documents:

    >>> for doc in corpus:
    ...     print(len(list(doc.tokens(zones=['TEXT']))))
    354
    1290
    364
    393

    The documents are loaded lazily (only parsed when requested)
    and cached.

    You can supply any class that takes a filename as an initialization
    argument. For instance, the Topics can also be loaded as a Collection:

    >>> tcorpus = Collection('../test_data/test-topics.list', document_cls=Topic)
    >>> len(tcorpus)
    1
    >>> for topic in tcorpus:
    ...     print(topic.tid)
    10.2452/401-AH

    """
    def __init__(self, document_list, docpath=None, cache_disabled=False,
                 document_cls=Document):
        """Initialize the corpus.

        :param document_list: A file with one document path per line.

        :param docpath: A prefix for the document paths. If ``None``
            (default), will assume the paths are relative to the location
            of the ``document_list``.

        :param nocache: If True, will never cache the loaded documents.
            This decreases memory requirements, but slows down loading
            times when a document is accessed more than once.
        """

        if not os.path.isfile(document_list):
            raise ValueError('Document list file {0} not found!'
                             ''.format(document_list))

        self.document_list_fname = document_list
        with open(self.document_list_fname) as instream:
            self.document_list = [l.strip() for l in instream]

        if docpath is None:
            docpath = os.path.dirname(self.document_list_fname)
        self.docpath = docpath
        self._document_cls = document_cls

        self._cache_disabled = cache_disabled
        self._cache = {}

    def __getitem__(self, item):
        if item in self._cache:
            return self._cache[item]
        else:
            return self.load_document(item)

    def __iter__(self):
        _time_start = time.clock()
        for i in range(len(self.document_list)):
            if i % 1000 == 0 and i != 0:
                _now = time.clock()
                print('Loaded {0} documents in {1:.2f} s, {2:.5f} s'
                      ' average per document.'.format(i, _now - _time_start,
                                                      (_now - _time_start) / i))
            try:
                yield self[i]
            except (ET.ParseError, TypeError):
                logging.error('Could not parse document no. {0}, fname {1}'
                              ''.format(i, self.document_list[i]))
                raise

    def __len__(self):
        return len(self.document_list)

    def load_document(self, index):
        """Handles loading the document itself, when needed."""
        if index >= len(self.document_list):
            raise ValueError('Document with index {0} not in corpus ({1} documents'
                             'available)'.format(index, len(self.document_list)))

        fname = os.path.join(self.docpath, self.document_list[index])
        if not os.path.isfile(fname):
            # Try a gzipped version?
            fname += '.gz'
        if not os.path.isfile(fname):
            raise ValueError('Document no. {0} not found! (Fname: {1}, '
                             'docpath: {2})'
                             ''.format(index, fname, self.docpath))
        document = self._document_cls(fname)

        if not self._cache_disabled:
            self._cache[index] = document

        return document

    @property
    def _loaded_idxs(self):
        return self._cache.keys()
