#!/usr/bin/env python3
"""
   Support for n-grams in numpy
   except that I've only tested them on english, non-utf8 examples
"""
import math
import numpy as np

class dictio:
    """ 
    a dictionary-like object 
    for 
    in which the hashcodes of items
    are stored in a sorted list suitable for binary search,
    and the offsets into a unigram table
    """
    def __init__(self, unigObject, nforgrams):
        self.unig = unigObject
        self.sortedHashes = np.ndarray(self.unig.hashcodes.shape, dtype=np.int64)
        par_offset = np.arange(start=0, stop=self.sortedHashes.shape[0], dtype=np.int32)
        if nforgrams == 1: #if we can use existing hashcodes in unig
            sortidx = np.argsort(self.unig.hashcodes, kind = 'stable')
            self.sortedHashes = self.unig.hashcodes[sortidx]
        else:
            gen = self.unig.getiter()
            for offset in gen():
                hcs = self.unig.get(offset)
                for i in range(1,nforgrams):
                    hcs += ' ' + self.unig.get(offset+i)
                hashcode = hash(hcs)
                self.sortedHashes[offset] = hashcode
            sortidx = np.argsort(self.sortedHashes, kind = 'stable')
            self.sortedHashes = self.sortedHashes[sortidx]
        self.par_offset = par_offset[sortidx]

    def find(self, string):
        hashcode = hash(string)
        idx = np.searchsorted(self.sortedHashes, hashcode)
        return self.par_offset[idx]

    def count(self):
        """
            build a list of unique items and their counts
        """
        offset = []
        count = []
        anchor = None
        for i in range(self.sortedHashes.shape[0]):
            hs = self.sortedHashes[i]
            if anchor is None or anchor != hs:
                anchor = hs
                offset.append(i)
                count.append(1)
            elif anchor == hs:
                count[-1] += 1
        return offset,count


class unigrams:
    def __init__(self, filename, punctuation):
        self.punct = set()
        self.bpunct = dict()
        for p in punctuation:
            self.punct.add(p)
            bp = p.encode('utf8')
            self.bpunct[bp] = p

        # dry run
        bytecnt = 0
        wordcnt = 0
        linecnt = 0
        word = ''
        # read file as bytes, not as UTF8
        #  only non-ASCII character believed to be \nbsp == \240 == \xA0
        with open(filename,'rb') as fi:
            for c0 in fi.read():
                c = chr(c0)
                if c in self.punct:  # if at end of word
                    if c == '\n':
                        linecnt += 1
                    wordcnt +=1
                    bytecnt += 1+len(word.encode('utf8'))
                    word = ''
                else:
                    word += c

        print('finished dry run.  word count:',wordcnt, 
                'byte count:', bytecnt,
                'line count:', linecnt,
                flush=True)

        #non-dry run
        #allocate storage
        self.hashcodes = np.zeros(wordcnt, dtype = np.int64)
        self.lengths =   np.zeros(wordcnt, dtype = np.uint8)
        self.offsets =   np.zeros(wordcnt, dtype = np.uint32)
        self.contents =  np.zeros(wordcnt, dtype = np.uint32)
        self.linestarts = np.zeros(linecnt, dtype= np.uint32)
        self.bits =      np.zeros(bytecnt, dtype = np.uint8)
        # set pointers into storage 
        nextWordOffset = 0
        nextWordNumber = 0
        nextByteOffset = 0
        lineNumber = 0
        word = ''
        with open(filename,'rb') as fi:
            for c0 in fi.read():
                c = chr(c0)
                if c in self.punct:
                    if len(word) == 0: continue   #ignore adjacent punctuation
                    self.contents[nextWordNumber] = lineNumber
                    bitswd =  word.encode('utf8') + b' ' 
                    self.offsets[nextWordNumber] = (nextWordOffset)
                    self.lengths[nextWordNumber] = (len(bitswd))
                    self.hashcodes[nextWordNumber] = (hash(word))
                    nextWordNumber += 1
                    self.bits [nextWordOffset:nextWordOffset+len(bitswd)] = bytearray(bitswd)
                    nextWordOffset += len(bitswd)
                    if c == '\n':
                        lineNumber += 1
                        self.lineStarts = nextWordNumber
                    word = ''
                else:  # accumulate character
                    word += c

        self.mxhash = np.max(self.hashcodes)

    def maxhash(self):
        return self.mxhash

    def get(self, wordNumber):
        """
        returns a string, based on an offset, such as might be returned
        by self.getiter() or dictio.find()
        """
        offset = self.offsets[wordNumber]
        length = self.lengths[wordNumber] - 1 #omit trailing space

        return bytearray(self.bits[offset:offset+length]).decode('utf8')

    def getiter(self):
        """
        returns a generator, which returns (one at a time, of course)
        an index which can be used for any of the (parallel) arrays:
        hashcode, byteoffset, length, content
        """
        current = 0
        last = self.offsets.size
        def iterator():
            nonlocal current
            while current < last:
                retval = current
                current += 1
                yield retval
        return iterator





if __name__ == '__main__':

    uni = unigrams('nGram.py', ' ():.,+-=[]*"\'/\m\n\t#')

    #check to see if there are duplicate strings for any hashcode
    shash = np.argsort(uni.hashcodes)
    last = None
    for i in shash:
        if last is None or uni.hashcodes[i] != last:
            last = i
            hsh = uni.hashcodes[last]
            lng = uni.lengths[last]
            ofs = uni.offsets[last]
            continue
        if lng != uni.length[i]:
            print (i,last, uni.lengths[i], lng, 'lengths do not match')
        if (uni.backingstore[ofs:ofs+lng] !=
           uni.backingstore[uni.offsets[i]:uni.offsets[i]+uni.lengths[i]]):
                   print('strings do not match')
    print('each unique hash has unique string.  Max hash', uni.mxhash, 'has',math.ceil(math.log(uni.mxhash,10)),'digits')
    minhash = min(uni.hashcodes)
    mindig = math.ceil(math.log(minhash,10))
    print ('min hash has',mindig, 'digits')



