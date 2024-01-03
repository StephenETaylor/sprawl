
I mean to write a module or two which will support n-grams in python.numpy.
The big problem with python n-grams is that each n-tuple is an object, and
each of the strings is an object, so an n-tuple of strings is n+1 objects.
If you have have a 100 million trigrams, thats 400 million objects (not counting
their content).  since each object is about 70 bytes, those 100 million trigrams
are 2.8 GB.  Which doesn't sound so bad, but note that we could store the same
100 million objects as say 32-bit offsets into a string table.

The nGram.py file creates an inmemory list of N words, so that each
bigram, trigram, ... n-gram in the list is present in the list already.

my idea is that the first occurence of of each n-gram will correspond to the 
count, and there'll be a dict for each n to convert that offset in the table 
into the canonical offset for the the count of identical n-grams.  
Seems likewith modesst care we could have a linked list for each occurenc3 of 
each word, which of course converts easily into the 2*n-1 n-grams each occurence
participates in. 

It looks to me like string hashcodes are 64-bit ints.  If so, then perhaps n-grams, inspite of being n times as long as a single word, wo also be 64-bit ints.

counting n-grams was the original intended application, so I should add
appropriate API...

I'll add counts first to the unigram class.  Its tempting to use a dict with
offsets, but instead I'll create a dictio class, which will keep:
numpy arrays of:
  sorted 64-bit hashcodes
  corresponding tables of:
   unigram offsets (so you can find the original string)
   lengths (maybe uint8?)
   content, which could be id numbers, counts, or something else.
idea is to use binary search on hashcodes to find count to update.
   
