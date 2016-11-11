"""This module implements a class that represents one document
from the collection."""
from __future__ import print_function, unicode_literals
import gzip
import io
import logging
import xml.etree.ElementTree as ET

from npfl103.io.vert import VText

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class DocumentBase:
    def __init__(self, fname):
        """Read the Document."""
        raise NotImplementedError('DocumentBase should not be instantiated directly!')

    @staticmethod
    def load_xmldoc(fname):
        _is_gzipped = fname.endswith('.gz')
        if _is_gzipped:
            with gzip.open(fname) as instream:
                xmldoc = ET.parse(instream)
        else:
            with open(fname) as instream:
                xmldoc = ET.parse(instream)
        return xmldoc

    @staticmethod
    def xmldoc2text(xmldoc, tag, strip=True):
        candidates = xmldoc.findall(tag)
        output = None
        if len(candidates) > 0:
            output = candidates[0].text
            if strip:
                output = output.strip()
        return output

    @staticmethod
    def xmldoc2vtext(xmldoc, tag, warn_on_more_than_one=True):
        candidates = xmldoc.findall(tag)
        vtext = None
        if len(candidates) > 0:
            if warn_on_more_than_one and len(candidates) > 1:
                logging.warning('Found more than one zone {0} in document:'
                                ' {1} in total, returning the first one.]'
                                ''.format(tag, len(candidates)))
            stream = io.StringIO(candidates[0].text)
            vtext = VText(stream_or_string=stream)
        return vtext


class Document(DocumentBase):
    """The Document class represents a document in the collection.

    >>> fname = '../test_data/LN-20020102001.vert'
    >>> d = Document(fname)

    It is uniquely identified by its ``docid``:

    >>> d.docid
    'LN-20020102001'

    It also has a ``docno``, which by default in the collection is the same
    as docid:

    >>> d.docno
    'LN-20020102001'

    The document has a ``title`` zone and a ``text`` zone.
    The text in each zoen is represented with an object of the ``VText``
    class.

    >>> len(d.title)
    26
    >>> len(d.text)
    354
    >>> len(d.text.sentences[-1])
    97
    >>> len(d.text.sentences)
    17

    """

    def __init__(self, fname):
        """Read the Document."""
        xmldoc = self.load_xmldoc(fname)

        self.docid = xmldoc.findall('DOCID')[0].text
        self.docno = xmldoc.findall('DOCNO')[0].text

        self.title = self.xmldoc2vtext(xmldoc, 'TITLE')
        self.text = self.xmldoc2vtext(xmldoc, 'TEXT')

        self.geography = None
        geographies = xmldoc.findall('GEOGRAPHY')
        if len(geographies) > 0:
            self.geography = geographies[0].text
