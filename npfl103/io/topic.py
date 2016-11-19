"""This module implements a class that..."""
from __future__ import print_function, unicode_literals

import collections
import gzip
import logging
import operator

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
        if fname.endswith('.gz'):
            opener = gzip.open
        else:
            opener = open

        with opener(fname, mode='rt') as instream:
            parsed_results = self.parse(instream)

        # Sort by idx
        sorted_results = sorted(parsed_results, key=operator.itemgetter(0))
        objects = collections.defaultdict(list)
        for idx, tag, content in sorted_results:
            objects[tag].append(content)

        self.tid = objects['num'][0].strip()

        self._vtexts = []
        self._vtext_zones = []
        for idx, tag, content in sorted_results:
            if tag in self.zones:
                self._vtexts.append(content)
                self._vtext_zones.append(tag)

        self.titles = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'title']
        self.descs = [vt for i, vt in enumerate(self._vtexts)
                      if self._vtext_zones[i] == 'desc']
        self.narrs = [vt for i, vt in enumerate(self._vtexts)
                      if self._vtext_zones[i] == 'narr']
