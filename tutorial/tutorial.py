
# coding: utf-8

# # Information Retrieval
# 
# This is a tutorial for the `npfl103` package for Information Retrieval assignments.
# It will cover the following steps:
# 
# 1. Loading documents and queries (topics)
# 2. Processing documents and queries into a vector space
# 3. Transforming the document vectors from one space to another
# 4. Making queries
# 5. Writing the outputs
# 6. Evaluating
# 
# Note that the Python classes you're supposed to use have documentation inside, with quite detailed examples.
# We don't cover all of that here -- the tutorial focuses on how the library fits together.

# In[1]:

import npfl103


# ### Tutorial data
# 
# The data for the tutorial lives in the `tutorial_assignment` subfolder. It mirrors the assignment folder in structure and file types.

# In[2]:

import os

dpath = os.path.join('.', 'tutorial-assignment')
dlist = os.path.join(dpath, 'documents.list')
qlist = os.path.join(dpath, 'topics.list')


# ## Loading documents and queries
# 
# For loading data, use the `npfl103.io` module. From the top down, there is a class for representing the entire collection of documents (`Collection`), a `Document` class for representing one document and an equivalent `Topic` class for representing one query topic, a `VText` class for representing a block of text in one zone of a document/query, and a `VToken` class for representing one word (or equivalent token) in a zone text.
# 
# These classes are nothing interesting: they merely represent the data (both the queries and the documents that should be retrieved). Check out their documentation strings for details on how to operate them.
# 
# The main entry point to data loading is the `Collection` class. Initialize it with the `documents.list` (or `topics.list`) file:

# In[3]:

from npfl103.io import Collection

coll_docs = Collection(dlist)


# Notice that creating the Collection was fast. This is because the whole pipeline in `npfl103` is lazy: no document is read until it is actually requested. This helps keep time and especially memory requirements down; the library is designed to have a constant memory footprint.

# ### Collection item classes
# 
# A Collection consists of individual documents. There are two implemented document types: the `Document` class from `npfl103.io`, and the `Topic` class. Collections are by default created as collections of `Document`s; however, for reading the queries, we use the same Collection mechanism and explicitly supply the `Topic` class.

# In[4]:

from npfl103.io import Topic
coll_queries = Collection(qlist, document_cls=Topic)


# ### Caching
# 
# The constant memory footprint is not exactly true: for speeding up repeated document reads, the Collection caches the documents it read. Eventually, you may run out of memory. In that case, try creating a Collection with `nocache=True`.

# ## Processing documents and queries into a vector space
# 
# To run a vector space information retrieval experiment, we now have to convert the loaded representations of documents and queries into a vector space. For this, we provide the `Vectorizer` classes.

# In[5]:

from npfl103.io import BinaryVectorizer, TermFrequencyVectorizer


# The purpose of a `Vectorizer` is to take a stream of a document's tokens and convert it into one vector representing this document in some vector space. Each token is used as a dimension of the vector space. If your tokens are just part of speech tags (noun, verb, etc.), then your space will have just some 10 dimensions; if your tokens are word forms, then there will be thousands of dimensions.
# 
# (The vectors will be *sparse* vectors, only remembering the nonzero elements -- implemented simply as a `dict`.) 
# 
# When we initialize a Vectorizer, we need to specify two things:
# 
# * What the stream of tokens should contain (what the dimensions of the space will be),
# * How the values of the vector items will be computed (binary? frequencies? etc.)

# Let's build a term frequency vectorizer that iterates over lemmas.

# In[6]:

vectorizer = TermFrequencyVectorizer(field='lemma')


# The vectorizer provides a `transform` method that does the processing.

# In[7]:

vdocs = (vectorizer.transform(d) for d in coll_docs)


# (Notice that we're still using generator expressions, so nothing really gets computed so far.)

# **After running through a** `Vectorizer`**, there is no implementation difference between what a Document and a Topic look like.**

# ### Which tokens?
# 
# Not all tokens are relevant. For instance, you might only want to represent a document using its title and headings, not the texts themselves. Or you might want to only use tokens which are "content words" -- usually defined as nouns, adjectives, verbs, or adverbs. The Vectorizers accept some arguments to specify which tokens should be used:
# 
# * Zones (TITLE, HEADING, ...)
# * Field (form, lemma, pos, full_pos, ... - see format specification in the assignment README)
# * Start and end token (e.g. you might only want to read the beginnings of documents)
# * Token filter
# 
# We've already seen an example using `field`. The `zones` for documents are `TITLE`, `HEADING`, and `TEXT`. The zones for queries (topics) are `title`, `narr`, and `desc`. Take a moment to look into the data, to make sure you know what the roles of the zones are.
# 
# Except for zones, **make sure you use the same vectorization settings for both the Documents and the Topics!**
# 
# #### Token filter
# 
# The token filter argument is a function that returns True or False when called with a `VToken` object. This enables filtering out tokens based on a different field than the one used to build the vector space. For instance, the aforementioned content word filtering would be iplemented as:

# In[8]:

cw_vectorizer = TermFrequencyVectorizer(field='lemma', token_filter=lambda t: t.pos in 'NADV')


# We can compare the results of the "plain" vectorizer and the content word vectorizer:

# In[9]:

vdocs = [vectorizer.transform(d) for d in coll_docs]   # This actually parses the documents.


# In[10]:

cw_docs = [cw_vectorizer.transform(d) for d in coll_docs]


# In[11]:

d = vdocs[0]
cw_d = cw_docs[0]

# Print the top 10 most frequent tokens
import pprint, operator
print('All words:')
pprint.pprint({w: n for w, n in sorted(d.items(), key=operator.itemgetter(1), reverse=True)[:10]})
print('----------------------\nContent words:')
pprint.pprint({w: n for w, n in sorted(cw_d.items(), key=operator.itemgetter(1), reverse=True)[:10]})


# We can see that token filtering can make a pretty large difference.

# ## Transforming vectors
# 
# While the Vectorizers got us from the raw data to a vector space, we might not be particularly happy with the immediate results. For instance, in the above example, we see very general words like "new" or "be", and we might wish to apply the Inverse Document Frequency transform. Or we want to normalize the frequencies to sum to 1, or use pivot normalization, or... whatever.
# 
# **To do operations on vector spaces, we use** `TransformCorpus` **objects as "pipeline sections" that operate on the flow of data.**

# In[12]:

from npfl103.transform import TransformCorpus


# These "pipeline" components get two parameters: the transformation they should be applying, and the source of the data to apply it on. Let's make an example transformation: normalizing the frequencies to 1.

# In[13]:

# This is the transformation we want to apply.
def normalize(vec):
    doc_length = sum(vec.values())
    return {k: v / doc_length for k, v in vec.items()}

normalized_docs = TransformCorpus(corpus=cw_docs, transform=normalize, name='normalized_docs')


# * The `corpus` is an iterable that contains dictionary-like objects as sparse document vectors.
# * The `transform` parameter is a callable: either a function, or a class that implements a `__call__` method.
# * Notice also the `name` parameter: this is for yourself, to be able to keep track of what each pipeline component does.

# Let's do the same thing for queries:

# In[14]:

cw_queries = (cw_vectorizer.transform(q) for q in coll_queries)   # Generator, again
normalized_queries = TransformCorpus(corpus=cw_queries, transform=normalize, name='normalized_queries')


# ### Vectorization as transformation
# 
# It is maybe more elegant to implement vectorization also as a pipeline component instead of having lists or generators floating around.

# In[15]:

cw_docs = TransformCorpus(corpus=coll_docs, transform=cw_vectorizer.transform, name='vectorized_docs')
cw_queries = TransformCorpus(corpus=coll_queries, transform=cw_vectorizer.transform, name='vectorized_queries')


# ### Chaining transformations
# 
# The pipelines can, of course, build on top of each other. Using the previous pipeline stages `cw_docs` and `cw_queries` objects of `TransformCorpus` class as the `corpus` parameter, we can put the normalization on top of these:

# In[16]:

normalized_docs = TransformCorpus(corpus=cw_docs, transform=normalize, name='normalized_docs')
normalized_queries = TransformCorpus(corpus=cw_queries, transform=normalize, name='normalized_docs')


# ### How would you implement TF-IDF in this system?
# 
# 1. Vectorize with TermFrequencyVectorizer
# 2. Implement IDF as a class with a `__call__` method that can be used as a transformation. (Hint: it needs to see the training corpus of documents at initialization time, to initialize the inverse document frequencies for the individual terms.)
# 3. Add a `TransformCorpus` that gets this IDF transformer as a `transform` method on top of the vectorized corpus (that was also used as input for the IDF transformer's initialization).

# ## Similarity queries
# 
# Assuming we're happy with the vector space in which our documents now live, we want to find for a query the similarity scores for all documents.
# 
# The same transformation mechanism is used. This time, we transform a query from the same space as the documents into a *similarity space*: the dimensions of this space are the documents which should be retrieved, and the values are the similarity scores for the query and that given document.

# In[17]:

from npfl103.similarity import Similarity

# The similarity is initialized with the document corpus.
similarity = Similarity(corpus=normalized_docs, k=10)       # Returning the top 10 documents. Use None for all docs.
similarity_corpus = TransformCorpus(corpus=normalized_queries, transform=similarity, name='sim')


# ## Recapitulation
# 
# At this point, the retrieval pipeline is set up. We have:
# 
# * Vectorized and processed the documents which we want to retrieve,
# * We can vectorize and process an incoming query in the same way,
# * We can use the query to compute similarities and return the top `K` documents.
# 
# Now, we only have to worry about recording our retrieval results and evaluating them against human judgments of relevant vs. non-relevant documents.

# ## Writing the outputs
# 
# In order to record the outputs, use the `Similarity.write_trec` static method:

# In[18]:

import io   # The system io, not npfl103.io
hdl = io.StringIO()  # Technical workaround, so that the tutorial does not create files at this point.

# This is what writes the output. In practice, you'll probably use "with open(...) as hdl:" to write to a file.
Similarity.write_trec(similarity_corpus, similarity, hdl)


# ## Evaluation
# 
# You should already have compiled `trec_eval` using the instructions in the `README` in `npfl103/eval`.
# The `npfl103.evaluation` package provides a `do_eval()` and `print_eval()` function to run evaluation
# from within the package.

# In[19]:

from npfl103.evaluation import do_eval, print_eval


# Since `trec_eval` (which is called inside these functions) needs an input file, not a stream,
# we have to dump our results to a file.

# In[20]:

results_file = 'tutorial-assignment/tutorial-output.dat'
with open(results_file, 'w') as outstream:
    Similarity.write_trec(similarity_corpus, similarity, outstream)


# The tutorial assignment has its ground truth file:

# In[21]:

qrels_file = 'tutorial-assignment/qrels.txt'
print_eval(qrels_file, results_file)


# You can also break down the results by query, by setting `results_by_query=True`:

# In[22]:

print_eval(qrels_file, results_file, results_by_query=True)


# If you want to do further processing with the results, use `do_eval()`.
# Instead of printing results, it returns them as a dictionary. Again, you can
# request the results by query (it will come in an `OrderedDict` of `OrderedDict`s,
# see `do_eval()` docstring).

# In[25]:

results = do_eval(qrels_file, results_file, results_by_query=True)
pprint.pprint([q for q in results])
pprint.pprint(results['10.2452/401-AH'])


# 

# # Happy hacking.
