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

    >>> description = t.descs[0]
    >>> print(description.to_text())
    Najděte dokumenty o růstech cen po zavedení Eura .


    """
    zones = ['title', 'desc', 'narr']

    def __init__(self, fname):
        xmldoc = self.load_xmldoc(fname)

        self.tid = self.xmldoc2text(xmldoc, 'num')

        self._vtexts, self._vtext_zones = self.parse_vtexts(xmldoc, self.zones)

        self.titles = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'title']
        self.descs = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'desc']
        self.narrs = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'narr']