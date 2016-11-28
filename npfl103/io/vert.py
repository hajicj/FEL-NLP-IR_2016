# -*- coding: utf-8 -*-
"""This module deals with the vertical text format."""
from __future__ import print_function, unicode_literals
import io
import logging

__version__ = "0.0.1"
__author__ = "Jan Hajic jr."


class VTParseException(ValueError):
    pass


class VToken:
    """Represents a token of the vertical texts.

    >>> line = '''5	nestalo	stát-2_^(něco_se_přihodilo)	VpNS---XR-NA---	0	Pred'''
    >>> token = VToken(line)

    The ``idx`` field holds the token's position in its sentence.

    >>> token.idx
    5

    The ``form`` field holds the word from the document.

    >>> token.form
    'nestalo'

    The word also has a ``lemma`` -- its base form.

    >>> token.lemma
    'stát'
    >>> token.wsd_lemma
    'stát-2'
    >>> token.full_lemma
    'stát-2_^(něco_se_přihodilo)'

    The information that we discarded by taking the lemma of the token
    (such as negation: "nestalo" vs. "stát") is kept in the morphological
    tag:

    >>> token.tag
    'VpNS---XR-NA---'

    The part-of-speech (noun, verb, adjective...) is in the ``pos`` attribute:

    >>> token.pos
    'V'

    Another part of the full morphological tag that the VToken exposes
    directly is negation:

    >>> token.negation
    'N'

    Note that negation has three values: ``A`` (affirmative), ``N`` (negative),
    and ``-`` (not applicable).

    For full documentation of the morphological tags, see README of assignment
    and online documentation of ÚFAL positional morphological tags.

    >>> token.head
    0
    >>> token.afun
    'Pred'

    It's basically a Plain Old Data class.
    """
    def __init__(self, line):
        """Creates the token.

        :param line:

        :return:
        """

        line = line.strip()

        idx, form, full_lemma, tag, head, afun = line.split()

        self.idx = int(idx)
        '''The position of the token in its sentence.'''

        self.form = form
        '''The surface form of the word. (What you see on the page.)'''

        self.full_lemma = full_lemma
        '''The base form of the word, with additional information:
        word sense disambiguated, additional notes (explanation, entity
        tag, etc. -- not that important right now)'''

        self.lemma = self.get_bare_lemma(full_lemma)
        '''The bare base form, without word sense disambiguation
        and additional notes.'''

        self.wsd_lemma = self.get_wsd_lemma(full_lemma)
        '''The lemma with disambiguation tags, so that e.g.
        the crown of a tree is a different lemma than the crown of a king.'''

        self.tag = tag
        '''Morphological tag. Positional UFAL system.'''

        self.head = int(head)
        '''The index of this token's dependency relationship head
        in the sentence. If head is zero, this token is the root.'''

        self.afun = afun
        '''The syntactic function of the token.'''

    @property
    def pos(self):
        """Simple part-of-speech: N for noun, A for adjective,
        V for verb, D for adverb, P for preposition, etc."""
        return self.tag[0]

    @property
    def negation(self):
        """Negation tag. Quite useful for verbs, possibly.
        Has values 'A' (yes, affirmative), 'N' (no, negative),
        and mostly '-' (not applicable)."""
        return self.tag[10]

    @staticmethod
    def get_bare_lemma(full_lemma):
        """Extracts the basic "short" version of a lemma.

        >>> VToken.get_bare_lemma('stát-2_^(něco_se_přihodilo)')
        'stát'

        :param full_lemma: The string with a lemma.

        :return: The bare lemma.
        """
        bare_lemma = wsd_lemma = VToken.get_wsd_lemma(full_lemma)
        # Find rightmost '-'
        _idx = wsd_lemma.rfind('-')
        if _idx >= 0:
            bare_lemma = wsd_lemma[:_idx]
        return bare_lemma


    @staticmethod
    def get_wsd_lemma(full_lemma):
        """Extracts the disambiguated version of a lemma.
        This means removing all remarks beyound ``_``,
        but leaves the ``-2`` word sense tags.

        >>> VToken.get_wsd_lemma('stát-2_^(něco_se_přihodilo)')
        'stát-2'

        :param full_lemma: The string with a lemma.

        :return: The lemma with the word sense number.
        """
        current_lemma = full_lemma
        # Explanatory remarks
        _idx = current_lemma.find('_^')
        if _idx != -1:
            current_lemma = current_lemma[:_idx]
        _idx = current_lemma.find('_;')
        if _idx != -1:
            current_lemma = current_lemma[:_idx]
        _idx = current_lemma.find('_')
        if _idx != -1:
            current_lemma = current_lemma[:_idx]
        return current_lemma


class VText:
    """Represents a vertical text:

    ``
        1	leden	leden	NNIS1-----A----	2	Sb
        2	provázely	provázet_:T	VpTP---XR-AA---	0	Pred
        3	v	v-1	RR--6----------	2	AuxP
        4	celé	celý	AAFS6----1A----	5	Atr
        5	Evropě	Evropa_;G	NNFS6-----A----	3	Adv
        6	bouřlivé	bouřlivý	AAFS2----1A----	7	Atr
        7	oslavy	oslava	NNFS2-----A----	8	Atr
        8	a	a-1	J^-------------	5	Coord
        9	ohňostroje	ohňostroj	NNIS2-----A----	8	Atr
        10	.	.	Z:-------------	0	AuxK
    ``

    Supports iteration over sentences and tokens.

    >>> stream = io.StringIO('''
    ... 1	leden	leden	NNIS1-----A----	2	Sb
    ... 2	provázely	provázet_:T	VpTP---XR-AA---	0	Pred
    ... 3	v	v-1	RR--6----------	2	AuxP
    ... 4	celé	celý	AAFS6----1A----	5	Atr
    ... 5	Evropě	Evropa_;G	NNFS6-----A----	3	Adv
    ... 6	bouřlivé	bouřlivý	AAFS2----1A----	7	Atr
    ... 7	oslavy	oslava	NNFS2-----A----	8	Atr
    ... 8	a	a-1	J^-------------	5	Coord
    ... 9	ohňostroje	ohňostroj	NNIS2-----A----	8	Atr
    ... 10	.	.	Z:-------------	0	AuxK
    ...
    ... 1	"	"	Z:-------------	2	AuxG
    ... 2	Nevypadají	vypadat_:T	VB-P---3P-NA---	0	Pred
    ... 3	jako	jako	J,-------------	4	AuxY
    ... 4	opravdové	opravdový	AAIP1----1A----	2	Obj
    ... 5	.	.	Z:-------------	0	AuxK''')
    >>> vt = VText(stream)
    >>> len(vt.sentences)
    2
    >>> len(vt.tokens)
    15
    >>> [len(s) for s in vt.sentences]
    [10, 5]
    >>> vt.tokens[10].tag
    'Z:-------------'

    Iterating over the VTokens
    --------------------------

    To iterate over the full VToken objects, just use

    >>> for i, t in enumerate(vt):
    ...     if i > 4: break
    ...     print(t.form)
    leden
    provázely
    v
    celé
    Evropě

    Exporting
    ---------

    You can also export the text of the document.

    >>> print(vt.to_text())
    leden provázely v celé Evropě bouřlivé oslavy a ohňostroje .
    " Nevypadají jako opravdové .

    And ask for specific VToken fields to be exported.

    >>> print(vt.to_text(field='lemma'))
    leden provázet v celý Evropa bouřlivý oslava a ohňostroj .
    " vypadat jako opravdový .

    Or ask just for specific sentences.

    >>> print(vt.to_text(sentence_idxs=[1]))
    " Nevypadají jako opravdové .

    Iterating over a stream of simple tokens
    ----------------------------------------

    To iterate over the tokens instead of aggregating them all
    this way, use ``to_text_stream()``. This currently only supports
    iterating over tokens, not sentences, and will not mark sentence
    ends. However, you can at least specify a start token and
    an end token.

    >>> for w in vt.to_token_stream(0, 4):
    ...     print(w)
    leden
    provázely
    v
    celé

    The ``to_text_stream()`` method is especially useful for iterating
    over an entire corpus without hogging memory.

    Token filters
    ^^^^^^^^^^^^^

    You can also filter the tokens based on their properties. Because
    the filter has the entire :class:`VToken` at its disposal, it can
    access other fields than the one that is being returned: for instance,
    it can output forms filtered by part-of-speech tags. If we only want
    nouns:

    >>> for w in vt.to_token_stream(token_filter=lambda t: t.pos in ['N']):
    ...     print(w)
    leden
    Evropě
    oslavy
    ohňostroje

    A token filter can be any callable -- we can for instance define a silly
    filter that only lets pass one word from each part of speech.

    >>> class UniqueTokenFilter:
    ...     def __init__(self): self._passed = {}
    ...     def __call__(self, vtoken):
    ...         if vtoken.pos in self._passed:
    ...             return False
    ...         self._passed[vtoken.pos] = True
    ...         return True
    >>> tf = UniqueTokenFilter()
    >>> for w in vt.to_token_stream(token_filter=tf):
    ...     print(w)
    leden
    provázely
    v
    celé
    a
    .


    """

    def __init__(self, stream_or_string):

        if isinstance(stream_or_string, str):
            lines = stream_or_string.split('\n')
        else:
            lines = (l for l in stream_or_string)

        self.tokens = []
        self.sentences = []

        # see self.sentences @property to find out how this works
        self._sentence_starts_index = [0]
        self._sentence_ends_index = []

        _sentence_ended = False
        for _lno, line in enumerate(lines):
            if line.strip() == '':
                # Sometimes the stream starts with an empty line
                # (this happens in the assignment data, but you probably
                #  won't feed in sentences that way during testing/playing
                #  around, so it's not hardcoded).
                if _lno == 0 or _sentence_ended:
                    continue
                # New sentence
                self._sentence_ends_index.append(len(self.tokens))
                self._sentence_starts_index.append(len(self.tokens))
                _sentence_ended = True
                continue
            else:
                _sentence_ended = False
                try:
                    token = VToken(line.strip())
                    self.tokens.append(token)
                except VTParseException:
                    logging.warning('Could not parse line {0} of VText: {1}'
                                    ''.format(_lno, line))

        # Maybe the last line wasn't empty, so we need to finish the sentece.
        # There are appropriate empty lines in the data, but this is just
        # expected robustness.
        if not _sentence_ended:
            self._sentence_ends_index.append(len(self.tokens))
            self._sentence_starts_index.append(len(self.tokens))
            _sentence_ended = False

        # Get rid of the last expected sentence start.
        if len(self._sentence_ends_index) == len(self._sentence_starts_index) - 1:
            self._sentence_starts_index = self._sentence_starts_index[:-1]

        # Build sentences index (note that Python only does references
        # to objects, so the tokens really are only stored once).
        self.sentences = [self.tokens[start:end]
                          for start, end in zip(self._sentence_starts_index,
                                                self._sentence_ends_index)]

    def __len__(self):
        return len(self.tokens)

    def __iter__(self):
        return (t for t in self.tokens)

    def __pass_all_filter(self, token):
        """The default token filter, which lets everything through."""
        return True

    def to_text(self, sentence_idxs=None, field='form', as_sentences=True,
                token_filter=None):
        """Formats the VText as a string with one sentence per line.
        Gets the corresponding field from the VText's VTokens as tokens
        of the output text. If you don't want to split the text into
        lines, set ``sentences=False``.

        :param filter_fn: Something callable that takes a VToken
            as an argument and returns True if the token should be
            part of the text, False if it shouldn't. The filter
            can be a function, or it can be a class that implements
            ``__call__``.

        """
        if token_filter is None:
            token_filter = self.__pass_all_filter

        if sentence_idxs is None:
            sentence_idxs = frozenset([i for i in range(len(self.sentences))])

        if as_sentences:
            output_lines = [' '.join([getattr(t, field) for t in s
                                      if token_filter(t)])
                            for i, s in enumerate(self.sentences)
                            if i in sentence_idxs]
            return '\n'.join(output_lines)
        else:
            return ' '.join([getattr(t, field) for t in self.tokens
                             if token_filter(t)])

    def to_token_stream(self, start=None, end=None, field='form',
                        token_filter=None):
        """Trick: use ``field='self'`` to return a stream of the VToken
        objects."""
        if token_filter is None:
            token_filter = self.__pass_all_filter

        if start is None:
            start = 0
        if end is None:
            end = len(self.tokens)

        for i, token in enumerate(self.tokens):
            if i < start:
                continue
            if i >= end:
                break
            if token_filter(token):
                yield getattr(token, field)
