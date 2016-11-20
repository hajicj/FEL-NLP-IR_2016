import operator

from npfl103.io.vert import VText, VToken
from npfl103.io.document import Document
from npfl103.io.topic import Topic
from npfl103.io.collection import Collection
from npfl103.io.vectorization import BinaryVectorizer, TermFrequencyVectorizer


def format_as_results(sim_vec, topic_uid, doc_collection,
                      run_name='default_run'):
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

    :returns: A string in this format.

    :param sim_vec: The similarity sparse vector. Keys are considered
        document idxs (they get UIDs retrieved from the underlying collection).

    :param topic_uid: Supply the UID for the topic for which the similarity
        vector holds query results.

    :param doc_collection: Supply the document collection from which to take
        UIDs for the documents in the query results.

    :param run_name: Identifier of the system used to produce the similarities.
    """
    # Sort the similarity vector by rank
    sorted_sims = sorted(sim_vec.items(), key=operator.itemgetter(1), reverse=True)

    output_lines = []
    for i, sim in sorted_sims:
        docno = doc_collection.get_uid(i)
        output_line = '\t'.join([topic_uid,
                                 '0',
                                 docno,
                                 str(i),
                                 str(sim),
                                 run_name])
        output_lines.append(output_line)
    return '\n'.join(output_lines)