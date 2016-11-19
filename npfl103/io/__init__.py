from npfl103.io.vert import VText, VToken
from npfl103.io.document import Document
from npfl103.io.topic import Topic
from npfl103.io.collection import Collection
from npfl103.io.vectorization import BinaryVectorizer, TermFrequencyVectorizer


def format_as_results(sim_vec, name, ):
    """Formats a similarity vector as the TREC output.

    The format of the system results contains 5 tab-separated
    columns:

    1. qid
    2. iter
    3. docno
    4. rank
    5. sim
    6. run_id

    Example::

        10.2452/401-AH 0 LN-20020201065 0 0 baseline
        10.2452/401-AH 0 LN-20020102011 1 0 baseline

    The important fields matter are "qid" (query ID, a string), "docno" (document
    number, a string appearing in the DOCNO tags in the documents), "rank" (integer
    starting from 0), "sim" (similarity score, a float) and "run_id" (identifying
    the system/run name, must be same for one file). The "sim" field is ignore by
    the evaluation tool but you are required to fill it.  The "iter" (string) field
    is ignored and unimportant.

    """
    pass
