"""This module implements a class that..."""
from __future__ import print_function, unicode_literals

from npfl103.io.document import DocumentBase

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class Topic(DocumentBase):
    """Represents one query topic. Like the document has zones ``title``
    and ``text``, the Topic has zones ``title``, ``desc``, and ``narr``.

    >>> fname = '../test_data/topic-401-AH.vert'
    >>> t = Topic(fname)

    The Topic is uniquely identified by its topic id (``tid``):

    >>> t.tid
    '10.2452/401-AH'

    The zones are again represented as VTexts.

    >>> description = t.desc
    >>> print(description.to_text())
    Najděte dokumenty o růstech cen po zavedení Eura .


    """
    def __init__(self, fname):
        xmldoc = self.load_xmldoc(fname)

        self.tid = self.xmldoc2text(xmldoc, 'num')

        self.title = self.xmldoc2vtext(xmldoc, 'title')
        self.desc = self.xmldoc2vtext(xmldoc, 'desc')
        self.narr = self.xmldoc2vtext(xmldoc, 'narr')