"""This module implements a class that represents one document
from the collection."""
from __future__ import print_function, unicode_literals

import copy
import gzip
import html
import io
import logging
import operator
import re
import xml.etree.ElementTree as ET

import collections

from npfl103.io.vert import VText

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class DocumentBase:
    zones = []

    def __init__(self, fname):
        """Read the Document."""

        # self._zone_vtext_dispatch = {}
        self._vtext_zones = []
        self._vtexts = []

    def tokens(self, zones=None, **vtext_to_stream_kwargs):
        """This is the basic interface for iterating over tokens.
        The ``field`` kwarg is important.
        """
        if zones is None:
            zones = self.zones

        for z in zones:
            if z not in self.zones:
                raise ValueError('Requesting non-existent zone: "{0}"! '
                                 '(Available: {1})'.format(z, self.zones))

        for vtext, vz in zip(self._vtexts, self._vtext_zones):
            if vz in zones:
                for token in vtext.to_token_stream(**vtext_to_stream_kwargs):
                    yield token

    @property
    def uid(self):
        """Returns the document's unique ID by which it should be referred
        to in the results."""
        raise NotImplementedError()

    @staticmethod
    def parse_vtexts(xmldoc, zones):
        """Returns a list of VTexts and the corresponding zone names."""
        vtexts, vtzones = [], []
        for element in xmldoc.getroot():
            if element.tag not in zones:
                continue
            vtext = VText(io.StringIO(element.text))
            vtexts.append(vtext)
            vtzones.append(element.tag)

        return vtexts, vtzones

    @staticmethod
    def load_xmldoc(fname):
        opener = open
        _is_gzipped = fname.endswith('.gz')
        if _is_gzipped:
            opener = gzip.open

        try:
            # if _is_gzipped:
            #     with opener(fname) as instream:
            #         xmldoc = ET.parse(instream)
            # else:
            with opener(fname) as instream:
                escaped_stream = io.StringIO('\n'.join(
                    [html.escape(l) for l in instream]))
                xmldoc = ET.parse(escaped_stream)

        except ET.ParseError:

            # logging.error('ET Parse error in doc. {0}!'.format(fname))
            # One problem we found: stray </CZE> tag in document
            with opener(fname, 'r') as instream:
                if _is_gzipped:
                    lines = [html.escape(str(l, 'utf-8')) for l in instream]
                else:
                    lines = [html.escape(l) for l in instream]

            _doc_end_idx = len(lines)
            for i, l in enumerate(reversed(lines)):
                # if isinstance(l, bytes):
                #     l = str(l, 'utf-8')
                if l.find('</DOC>') >= 0:
                    if i >= 1:
                        _doc_end_idx = -1 * i
                    break
            relevant_lines = lines[:_doc_end_idx]
            cut_stream = io.StringIO('\n'.join(relevant_lines))

            xmldoc = ET.parse(cut_stream)

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

    @staticmethod
    def xmldoc2many_vtexts(xmldoc, tag):
        """Returns a list of VTexts corresponding to texts of the given tag."""
        vtexts = [VText(io.StringIO(c.text) for c in xmldoc.findall(tag))]
        return vtexts

    def parse(self, stream):
        """Returns a list of (tag, text) pairs based on opening/closing tags.
        It was not doable to parse this through XML because of tokenization
        of documents sometimes incompatible with XML.

        Assumptions:

        * The documents are flat - no nested tags.
        * There is no more than one tag per line. (It can begin and end
          on the same line, though.)
        * If there is an opening tag on the line, it is at the line's beginning
        * If there is a closing tag, it is at the end of the line.
        """
        re_open_tag = re.compile('^<([^/>]*)>')
        re_close_tag = re.compile('</([^/>]*)>$')

        output = []   # Triplets: tag_start_idx, tag, text
        c_tag_start_idx_stack = []
        c_open_tag_stack = []
        c_text_stack = []  # Text accumulators
        for lno, line in enumerate(stream):

            # Looking for tags on the given line
            open_tags = re_open_tag.findall(line)
            if len(open_tags) > 1:
                raise ValueError('Line {0}: too many open tags: {1}\n'
                                 'Line: {2}'.format(lno, open_tags, line))

            close_tags = re_close_tag.findall(line)
            if len(close_tags) > 1:
                raise ValueError('Line {0}: too many close tags: {1}\n'
                                 'Line: {2}'.format(lno, close_tags, line))

            otag = None
            if len(open_tags) > 0:
                # There might be attributes in the open tag; we ignore them
                otag = open_tags[0].split()[0]
                #otag = open_tags[0]
            ctag = None
            if len(close_tags) > 0:
                ctag = close_tags[0]

            # Strip tags from text
            clean_line = copy.deepcopy(line)
            if otag is not None:
                clean_line = clean_line[len(otag)+2:]
            if ctag is not None:
                # After a closing tag, we ignore the ending \n
                clean_line = clean_line.rstrip()[:-(len(ctag)+3)]

            # Case: both otag and ctag are not None. In this case,
            # we can process the whole line at once.
            if ctag is not None and otag is not None:
                if ctag != otag:
                    raise ValueError('If an open and close tag are present'
                                     ' on the same line, they must be the same!'
                                     ' Line no. {0}, ot: {1}, ct: {2}\n'
                                     'Line: {3}'
                                     ''.format(lno, otag, ctag, line))
                output.append((lno, otag, clean_line))

            # If a new tag is being opened: add to stack
            elif otag is not None and ctag is None:
                c_tag_start_idx_stack.append(lno)
                c_open_tag_stack.append(otag)
                c_text_stack.append([clean_line])

            # If a tag is being closed:
            elif otag is None and ctag is not None:
                if len(c_open_tag_stack) < 1:
                    if ctag == 'CZE':
                        logging.warning('Line {0}: parasitic closing tag CZE found,'
                                        ' ignoring it.'.format(lno))
                        continue
                    raise ValueError('Line {0}: closing tag {1} without being'
                                     ' previously opened!\nLine: {2}'
                                     ''.format(lno, ctag, line))
                if ctag != c_open_tag_stack[-1]:
                    raise ValueError('Line {0}: closing tag {1} different'
                                     ' from currently opened tag {2}!\n'
                                     'Line: {3}'.format(lno, ctag, otag, line))

                # Add text to stack
                c_text_stack[-1].append(clean_line)

                # Pop tag
                tag = c_open_tag_stack.pop()

                # Pop index
                idx = c_tag_start_idx_stack.pop()

                # Pop text and postprocess if necessary
                _text_lines = c_text_stack.pop()
                text = ''.join(_text_lines)
                if tag in self.zones:
                    text = VText(io.StringIO(text))

                output.append((idx, tag, text))

            elif otag is None and ctag is None:
                c_text_stack[-1].append(clean_line)

        return output


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

    The ``docno`` is really important, because it identifies the document
    for the purposes of recording retrieval results. Don't mess with ``docno``.

    A more general mechanism to recover a document's identifier is implemented
    through the ``uid`` property:

    >>> d.uid
    'LN-20020102001'

    The document has a ``TITLE`` zone, a ``TEXT`` zone, and a ``HEADING``
    zone. Each zone can contain multiple texts, in the order in which
    they come in the document. The texts in each zone are represented
    with an object of the ``VText`` class.

    >>> len(d.titles[0])
    26
    >>> len(d.texts[0])
    354
    >>> len(d.texts[0].sentences[-1])
    97
    >>> len(d.texts[0].sentences)
    17

    You can also iterate over the document's tokens, possibly with specifying
    which zones to iterate over.

    >>> for i, t in enumerate(d.tokens()):
    ...     if i >= 3: break
    ...     print(t)
    304
    miliony
    lidí

    You can also supply kwargs for iterating
    over each zone like you would pass them to :meth:`VText.to_token_stream`.
    Note, however, that the start and end arguments will be applied to each
    zone as well, so this will return 4 lemmas:

    >>> for t in d.tokens(zones=['TEXT'], start=0, end=4, field='lemma'):
    ...     print(t)
    příchod
    nový
    evropský
    měna

    If you iterate over multiple zones, the tokens will be interleaved
    according to how they were ordered in the original document: title,
    then heading 1, text 1, heading 2, text 2, etc.

    The ``tokens()`` method is a generator.

    """
    zones = ['TITLE', 'HEADING', 'TEXT']

    def __init__(self, fname):
        """Read the Document."""
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

        self.docid = objects['DOCID'][0]
        self.docno = objects['DOCNO'][0]
        self.geographies = objects['GEOGRAPHY']

        self._vtexts = []
        self._vtext_zones = []
        for idx, tag, content in sorted_results:
            if tag in self.zones:
                self._vtexts.append(content)
                self._vtext_zones.append(tag)

        self.titles = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'TITLE']
        self.headings = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'HEADING']
        self.texts = [vt for i, vt in enumerate(self._vtexts)
                       if self._vtext_zones[i] == 'TEXT']

    @property
    def uid(self):
        return self.docno