# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 13:36:58 2016
An intertext finder that uses a variant of jaccard distance for bags of
lemmatized words. The jaccard distance between two sets is their intersection 
divided by their union. For ease of understanding, this module does not use 
a precise calculation of jaccard distance. Instead it approximates it by 
letting the user set the size of the bags of words, and a threshold size for
their intersection.
@author: s
"""

import nltk
import re
import pickle
import pandas as pd
import networkx as nx
from jellyfish import levenshtein_distance as ld
import cltk
import requests
import bs4
from cltk.stop.latin.stops import STOPS_LIST
import os

#some useful global constants

lstops=[w for w in STOPS_LIST]
punct=[',',"'",'"',':','?','.','!',';','-','[',']','(',')']
lstops.extend(punct)
lstops.extend(['sum1']) #lemmatizer returns 'sum1', but STOPS_LIST has 'sum'
lstops.extend(['edo1']) #lemmatizer labels 'est' as 'edo1'
lstops.extend(['qui1','jam']) #two more stops that were missed

bgs=[('res','publica'),('deus','immortalis'),('ut','tam'),('ut','talis'),('ut','tantus')]

acceptableTags=['-', 'A', 'C', 'D', 'E', 'M', 'N', 'P', 'R', 'T', 'V']

#These are stopwords and bigrams that are useful for Cicero's political rhetoric
#which was the original purpose of this module

#lstops.extend(['nihil','parvus','minus','omne','modo','tantus','qualis','civis','bonus'])
#
#bgs=[('res','publica'),('deus','immortalis'),('ut','tam'),('ut','talis'),('ut','tantus'),('neo1','tam'),('neo1','talis'),('neo1','tantus')]
#bgs.append(('reor','publica')) #haha it lemmatizes 're' to reor
#bgs.append(('redeo','publica'))#and 'rei' to redeo
#bgs.extend([('reor','publicum'),('redeo','publicum')])
#bgs.extend([('reor','publico'),('redeo','publico'),('res','publico'),('reor','publicus'),('redeo','publicus'), ('res','publicus')])
#bgs.extend([('patro','conscribo'),('populus1','Romanus'),('senatus','consulo'),('senatus','populus1'),('senatus','populo')])

class JaccardIntertextFinder:
    """
    Uses Jaccard distance to find intertexts. Only tested for Latin Prose
    """
    
    def __init__(self, shingleSize=8,threshold=3, bigrams=bgs,stops=lstops,
                 tags=acceptableTags):
        """
        Uses a lot of constants that users may want to be able to tweak.
        
        Args:
        
        shingleSize(int)-- How big do you want your bag of words to be? 
        
        threshold(int)-- The minimum number of matches within a bag of words that
            is necessary in order for the two sentences to be considered a potential match
        
        bigrams(list of tuples)-- a list [(term1,term2), (term1,term2) etc].
            Some bigrams are so common ('res publica', for instance) that users
            may want them to count only as a single match. Use this to pass a list
            of such bigrams.
            
        stops(list)-- a list of stopwords. These words will be ignored (not
            included in shingles).
            The default is for a modified list of
            latin stopwords that produced the best results. Users are encouraged
            to think carefully about the value of this list. It will make a 
            significant difference for the quality of the results.
            
        tags(list)-- Most methods for this class assume that your text has been
            tokenized, lemmatized and Part-of-Speech tagged. This list tells 
            the intertext finder which parts of speech should be considered. 
            The default considers all parts of speech, but users may want to 
            consider removing conjunctions or pronouns from consideration, for
            example. The tags correspond to the first element in the standard
            CLTK tags.
        
        
        """
        self.shingleSize=shingleSize
        self.matchThreshold=threshold
        self.bigrams=bigrams
        self.stops=stops
        self.goodTags=tags
        
    def FindJaccardMatches(self, text1,text2,name1='Text1',name2='Text2'):
        """
        Finds matches without controlling for common bigrams. Returns a results
        object.
        
        Args:
        text1(list)-- The first of the two texts you would like to compare. Results
            will be ordered according to it. Logically, this should be the text
            to which the other one refers, but results will be symmetrical.
            text1 (and text2) must be a list of sentences, where each sentence
            is a list of (word, tag, lemma) triples.
            
            This structure may seem complex to users who are new to Natural 
            Language processing, so here is a more detailed explanation.
            
            Begin with something that is just a continuous block of text that
            you would find anywhere. eg "Hi. I am Lucius."
            Now break that into a list of sentences, like so.
            
            TODO: Finish this
            
        text2(list)-- an object similar to text1. A list of sentences, which
            are lists of (word, tag, lemma) triples.
            
        name1(str)-- the title of text1
        
        name2(str)-- the title of text2
        
        return()
        """
        
        shinMatches=[]
        i=0
        for sent in cat3:
            cat3shins=MakeShingles(sent)
            j=0
            for sen in prh:
                prshins=MakeShingles(sen)
                mmss=MatchShinglesNoOvercountBigrams(cat3shins,prshins,bigrams=bgs)
                if mmss[0]==True:
                    copywords=[[w for w,t,l in sen if l in mmss[1]],[w for w,t,l in sent if l in mmss[1]]]
                    shinMatches.append([cat3sents[i],prsents[j],copywords])
                j+=1
            i+=1







def MakeShingles(sent, shingleSize=8, goodTags=acceptableTags,stops=lstops):
    
    words=[l for w,t,l in sent if l!=None and l not in stops and t[0] in goodTags]
    shingles=[]
    for i in range (0,len(words)-shingleSize):
        shingles.append(words[i:i+shingleSize])
    return shingles
    

def MatchingShingles (shin1,shin2,thresh=3):
    match=False
    intersectwords=[]
    for shin in shin1:
        s1=set(shin)
        for s in shin2:
            s2=set(s)
            sint=s2.intersection(s1)
            if len(sint)>=thresh:
                match=True
                intersectwords.extend(sint)
    return([match,intersectwords])

def MatchShinglesNoOvercountBigrams(shin1,shin2,thresh=3,bigrams=bgs):
    match=False
    intersectwords=[]
    for shin in shin1:
        s1=set(shin)
        for s in shin2:
            s2=set(s)
            sint=s2.intersection(s1)
            ct=len(sint)
            for bigram in bigrams:
                if bigram[0] in sint and bigram[1] in sint:
                    ct-=2
            if ct>=thresh:
                match=True
                intersectwords.extend(sint)
    return([match,intersectwords])
        
#test1=set(['vir','publico','fortis'])
#is more refactoring to do before you can turn this into a function 
   
#shinMatches=[]
#i=0
#for sent in cat3:
#    cat3shins=MakeShingles(sent)
#    j=0
#    for sen in prh:
#        prshins=MakeShingles(sen)
#        mmss=MatchingShingles(cat3shins,prshins)
#        if mmss[0]==True:
#            copywords=[[w for w,t,l in sen if l in mmss[1]],[w for w,t,l in sent if l in mmss[1]]]
#            shinMatches.append([cat3sents[i],prsents[j],copywords])
#        j+=1
#    i+=1
#
##with bigramfilter
#bgs=[('res','publica'),('deus','immortalis'),('ut','tam'),('ut','talis'),('ut','tantus'),('neo1','tam'),('neo1','talis'),('neo1','tantus')]
#bgs.append(('reor','publica')) #haha it lemmatizes 're' to reor
#bgs.append(('redeo','publica'))#and 'rei' to redeo
#bgs.extend([('reor','publicum'),('redeo','publicum')])
#bgs.extend([('reor','publico'),('redeo','publico'),('res','publico'),('reor','publicus'),('redeo','publicus'), ('res','publicus')])
#shinMatches=[]
#i=0
#for sent in cat3:
#    cat3shins=MakeShingles(sent)
#    j=0
#    for sen in prh:
#        prshins=MakeShingles(sen)
#        mmss=MatchShinglesNoOvercountBigrams(cat3shins,prshins,bigrams=bgs)
#        if mmss[0]==True:
#            copywords=[[w for w,t,l in sen if l in mmss[1]],[w for w,t,l in sent if l in mmss[1]]]
#            shinMatches.append([cat3sents[i],prsents[j],copywords])
#        j+=1
#    i+=1
#

def makeEdgeList(speech1,speech2,speech1Name='Speech1',speech2Name='Speech2'
                    shingleSize=8,threshold=3):
    edgematrix=pd.DataFrame(columns=(['Source','Target','WordsInCommon']))
    S1Nodes=[]
    S2Nodes=[]
    words=[]
        
    for ind1,sent in enumerate(speech1):
        s1sh=MakeShingles(sent)
        for ind2,sen in enumerate(speech2):
            s2sh=MakeShingles(sen)
            mmss=MatchingShingles(s1sh,s2sh)
            if mmss[0]==True:
                S1Nodes.append(speech1Name+' '+str(ind1))
                S2Nodes.append(speech2Name+' '+str(ind2))
                S1.append(speech1Name)
                S2.append(speech2Name)
                wds=set(mmss[1])
                words.append(str(wds).replace('[','').replace(']','').replace(',','  '))
            j+=1
        i+=1
    edgematrix['Source']=S1Nodes
    edgematrix['Target']=S2Nodes
    edgematrix['WordsInCommon']=words
    return(edgematrix)

def makeEdgeListNOCbigrams(speech1,speech2,speech1Name,speech2Name,bigrams=bgs,shingleSize=8,simThresh=3):
    edgematrix=pd.DataFrame(columns=(['S1Node','S2Node','Speech1','Speech2','WordsInCommon']))
    S1Nodes=[]
    S2Nodes=[]
    words=[]
    S1=[]
    S2=[]
    i=0    
    for sent in speech1:
        s1sh=MakeShingles(sent,shingleSize)
        j=0
        for sen in speech2:
            s2sh=MakeShingles(sen,shingleSize)
            mmss=MatchShinglesNoOvercountBigrams(s1sh,s2sh, thresh=simThresh)
            if mmss[0]==True:
                S1Nodes.append(speech1Name+' '+str(i))
                S2Nodes.append(speech2Name+' '+str(j))
                S1.append(speech1Name)
                S2.append(speech2Name)
                wds=set(mmss[1])
                words.append(str(wds).replace('[','').replace(']','').replace(',','  '))
            j+=1
        i+=1
    edgematrix['S1Node']=S1Nodes
    edgematrix['S2Node']=S2Nodes
    edgematrix['Speech1']=S1
    edgematrix['Speech2']=S2
    edgematrix['WordsInCommon']=words
    return(edgematrix)
    
    
#    
#cicer=nltk.corpus.PlaintextCorpusReader(path,'cat3.txt')
#foo=nltk.sent_tokenize(cicer.raw())
 
#note to self: it might be worth it to make these return a concordance class object
   
def stableConcordance(word,sents):
    return([sent for sent in sents if word in sent])

def partialmatchConcordance(reob,sents):
    goods=[]
    for sent in sents:
        if([w for w in sent if reob.match(w)]):
            goods.append(sent)
    return (goods)

#probably best to do this recursively
def multiMatchConcordance(words,key=words[-1],sents,distBefore=3,distAfter=3):
    while words:
        word=words.pop(0)
        if word==key:
            return
            
def MatchInRangeConcordance(reob,key,sents,distBefore=3,distAfter=3):
    goods=[]
    for sent in sents:
        spot=None
        if type(key)==str:
            spot=sent.index(key)
        else:
            spot=sent.index([w for w in sent if key.match(w)][0])
        if spot:
            if([w for w in sent[max(0,spot-distBefore):min(spot+distAfter,len(sent))] if reob.match(w)]):
                goods.append(sent)
    return(goods)

def ListForHuman(sent):
    return(' '.join(w+' ' for w in sent))

###############################################################
#an actual project
##############################################################
# domo=nltk.corpus.PlaintextCorpusReader(path,'domo.txt')

# vobis=re.compile('^tu$|^tui$|^te$|^tibi$|^vos$|^vobis|^vestr')
# hic=re.compile('^hic$|haec|hoc|huius|hunc|hanc|huic|^hac$|^hi$|^hae$|haec|horum|harum|^hos$|^has$|^his$',re.I)

# dom1=stableConcordance('etiam',domo.sents())
# dom2=MatchInRangeConcordance(vobis,'etiam',dom1)
# dom3=MatchInRangeConcordance(hic,vobis,dom2,4,4)

# allcic=nltk.corpus.PlaintextCorpusReader(path,'.*.txt')

# jupregex=re.compile('Jup|Jov|Iup|Iov')
# jupc=partialmatchConcordance(jupregex,allcic.sents())
    

# prsEdges=makeEdgeListNOCbigrams(cat3,prh[0:140],'Cat3','PostRSen')

# prsEdges.to_csv('prs_edgematrix.csv')

# prqEdges=makeEdgeListNOCbigrams(cat3,prh[141:221],'Cat3','PostRQui')

# harEdges=makeEdgeListNOCbigrams(cat3,prh[221:544],'Cat3','Haruspicum')

# harEdges.to_csv('har_edgematrix.csv')

# prqEdges.to_csv('prq_edgematrix.csv')

# DDEdges=makeEdgeListNOCbigrams(cat3,prh[545:],'Cat3','DeDomo')

# DDEdges.to_csv('dd_edgematrix.csv')



#cleaning up the edge lists by finding more bigrams

# with open('cat3Heavy.pickle','rb') as f:
#     cat3=pickle.load(f)

# with open('PostReditumHeavy.pickle','rb') as f:
#     prh=pickle.load(f)

# with open('cat124Heavy.pickle','rb') as f:
#     cat124=pickle.load(f)
    
# allcat=cat124[:309]
# allcat.extend(cat3)
# allcat.extend(cat124[310:])

# prh=[s[0] for s in prh]
# allcat=[s[0] for s in allcat]

# prsEdges=makeEdgeListNOCbigrams(allcat,prh[0:140],'Cat','PostRSen',shingleSize=5)

# prsEdges.to_csv('prs_edgematrix4.csv')

# prqEdges=makeEdgeListNOCbigrams(allcat,prh[141:221],'Cat','PostRQui',shingleSize=5)

# harEdges=makeEdgeListNOCbigrams(allcat,prh[221:544],'Cat','Haruspicum',shingleSize=5)

# harEdges.to_csv('har_edgematrix4.csv')

# prqEdges.to_csv('prq_edgematrix4.csv')

# DDEdges=makeEdgeListNOCbigrams(allcat,prh[545:],'Cat ','DeDomo',shingleSize=5)

# DDEdges.to_csv('dd_edgematrix4.csv')






