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
lstops.extend(['qui1','jam']) #two more stops that are very helpful

bgs=[('res','publica'),('deus','immortalis'),('ut','tam'),('ut','talis'),('ut','tantus')]

acceptableTags=['-', 'A', 'C', 'D', 'E', 'M', 'N', 'P', 'R', 'T', 'V']


#These are some additional stopwords and bigrams that are useful for Cicero's
#political rhetoric, which was the original purpose of this project


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
        Finds matches without controlling for common bigrams. Returns object.
        
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
        
        return(MatcherOutput)-- a simple class with one or two useful methods
        """
        
        shinMatches=[]
        for t1Sent in text1:
            text1shins=MakeShingles(t1Sent,self.shingleSize,goodTags=self.goodTags,
                                    stops=self.stops)
            for t2Sent in text2:
                text2shins=MakeShingles(t2Sent,self.shingleSize,
                                        goodTags=self.goodTags,stops=self.stops)
                compared=MatchShinglesNoOvercountBigrams(text1shins,
                                        text2shins,bigrams=self.bigrams,
                                        thresh=self.matchThreshold)
                                        
                if compared[0]==True:
                   
                   copywords=[[w for w,t,l in t1Sent if l in compared[1]],
                               [w for w,t,l in t2Sent if l in compared[1]]]
                   
                   shinMatches.append(([w for w,t,l in t1Sent],
                                        [w for w,t,l in t2Sent],copywords))
                    
        return(MatcherOutput(shinMatches,name1,name2))
        
        
        
    def FindJaccardMatches_NoOvercountBigrams(self, text1,text2,
                                              name1='Text1',name2='Text2'):
                                                  
        """
        Finds matches while controlling for common bigrams (they count as only
        one word, not two). Returns an Object
        
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
        
        return(MatcherOutput)-- a simple class with one or two useful methods
        """
        shinMatches=[]
        for t1Sent in text1:
            text1shins=MakeShingles(t1Sent,self.shingleSize,goodTags=self.goodTags,
                                    stops=self.stops)
            for t2Sent in text2:
                text2shins=MakeShingles(t2Sent,self.shingleSize,
                                        goodTags=self.goodTags,stops=self.stops)
                compared=MatchShinglesNoOvercountBigrams(text1shins,
                                        text2shins,bigrams=bgs,
                                        thresh=self.matchThreshold)
                                        
                if compared[0]==True:
                   
                   copywords=[[w for w,t,l in t1Sent if l in compared[1]],
                               [w for w,t,l in t2Sent if l in compared[1]]]
                   
                   shinMatches.append(([w for w,t,l in t1Sent],
                                        [w for w,t,l in t2Sent],copywords))
                    
        return(MatcherOutput(shinMatches,name1,name2))
        
        
    def MatchWithEdgeList(self,text1,text2,title1='Text1',title2='Text2'):
        edgeList=[]
        shinMatches=[]
        
        for t1_ind,t1_sent in enumerate(text1):
            t1_shin=MakeShingles(t1_sent,self.shingleSize,goodTags=self.goodTags,
                                    stops=self.stops)
            for t2_ind,t2_sent in enumerate(text2):
                t2_shin=MakeShingles(t2_sent,self.shingleSize,
                                     goodTags=self.goodTags,stops=self.stops)
                compared=MatchingShingles(t1_shin,t2_shin,self.matchThreshold)
                if compared[0]==True:
                    #stuff for the edge list
    #                S1Nodes.append(title1+' '+str(t1_ind))
    #                S2Nodes.append(title2+' '+str(t2_ind))
    #                wds=set(compared[1])
    #                words.append(str(wds).replace('[','').replace(']','')
    #                                .replace(',','  '))
                    edgeList.append({'source':title1+' '+str(t1_ind), 
                                     'target':title2+' '+str(t2_ind), 
                                     'words': set(compared[1])})
                    #stuff for the default data structure
                    copywords=[[w for w,t,l in t1_sent if l in compared[1]],
                                   [w for w,t,l in t2_sent if l in compared[1]]]
                       
                    shinMatches.append(([w for w,t,l in t1_sent],
                                            [w for w,t,l in t2_sent],copywords))
                    
    #    edgematrix['Source']=S1Nodes
    #    edgematrix['Target']=S2Nodes
    #    edgematrix['WordsInCommon']=words
        return(MatcherOutput(shinMatches, title1,title2,edgeList) ) 
          
        

class MatcherOutput:
    """
    Class for the output of Jaccard Matcher.  Collects some useful methods.
    """
    
    def __init__(self, output,name1,name2,edgematrix=[]):
        self.output_raw=output
        self.matching_sentences=[(ListForHuman(s1),ListForHuman(s2),wic) for s1,s2,wic in self.output_raw]
        self.title1=name1
        self.title2=name2
        self.NumberOfMatches=len(output)
        self.edgeList=edgematrix
               
    def Inspect(self):
        """
        Makes a quick html table for easy inspection. Automatically opens in
        your default browser.
        """
        MakeHTMLTable(self.matching_sentences,self.title1,self.title2)
    
#    def Visualize(self):
#        """
#        Makes a quick hive plot of intertexts for ease of understanding. 
#        Automatically opens in your default browser.
#        """
#        ddd_dat={}
#        for 
        


def TermDocumentMatrix (docs,selector='word',docnames=None, stops=None):
    """
    
    Function to create a Term-Document Matrix with a single call, since
    neither the nltk nor the cltk comes with one built in. 
    
    Arguments:
    
    
    """
    if selector=='word':
        sel=0
    elif selector=='lemma':
        sel=2
    else:
        raise ValueError("I do not recognize that selector; use 'word' or 'lemma' ")
    
    if not docnames:
        docnames=['Doc'+str(i+1) for i in range(0,len(docs))]

    TDM=pd.DataFrame(columns=['term'].extend(docnames))
    fdl=[]
    for doc in docs:
        dw=[]
        for sent in doc:
            if stops:
                dw.extend(w[sel] for w in sent if w[sel] not in stops)
            else:
                dw.extend(w[sel] for w in sent)
        fdl.append(nltk.FreqDist(dw))
    
    words=[]
    for fd in fdl:
        words.extend(fd.keys())
    words=set(words)
    TDM['term']=list(words)
    for k,v in enumerate(docnames):
        TDM[docnames[k]]=[fdl[k][w] for w in words]
    return(TDM)



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
        


def makeEdgeList(speech1,speech2,speech1Name='Speech1',speech2Name='Speech2',
                    shingleSize=8,threshold=3):
    edgematrix=pd.DataFrame(columns=(['Source','Target','WordsInCommon']))
    S1Nodes=[]
    S2Nodes=[]
    words=[]
        
    for ind1,sent in enumerate(speech1):
        s1sh=MakeShingles(sent,shingleSize)
        for ind2,sen in enumerate(speech2):
            s2sh=MakeShingles(sen)
            mmss=MatchingShingles(s1sh,s2sh,threshold)
            if mmss[0]==True:
                S1Nodes.append(speech1Name+' '+str(ind1))
                S2Nodes.append(speech2Name+' '+str(ind2))
                S1.append(speech1Name)
                S2.append(speech2Name)
                wds=set(mmss[1])
                words.append(str(wds).replace('[','').replace(']','')
                                .replace(',','  '))
    edgematrix['Source']=S1Nodes
    edgematrix['Target']=S2Nodes
    edgematrix['WordsInCommon']=words
    return(edgematrix)

def makeEdgeListNOCbigrams(speech1,speech2,speech1Name='Speech1',
                    speech2Name='Speech2',shingleSize=8,threshold=3, 
                    bigrams=bgs):
    edgematrix=pd.DataFrame(columns=(['Source','Target','WordsInCommon']))
    S1Nodes=[]
    S2Nodes=[]
    words=[]
    
    for ind1,sent in enumerate(speech1):
        s1sh=MakeShingles(sent)
        for ind2,sen in enumerate(speech2):
            s2sh=MakeShingles(sen)
            mmss=MatchShinglesNoOvercountBigrams(s1sh,s2sh, threshold,bigrams)
            if mmss[0]==True:
                S1Nodes.append(speech1Name+' '+str(ind1))
                S2Nodes.append(speech2Name+' '+str(ind2))
                S1.append(speech1Name)
                S2.append(speech2Name)
                wds=set(mmss[1])
                words.append(str(wds).replace('[','').replace(']','')
                                .replace(',','  '))
    edgematrix['Source']=S1Nodes
    edgematrix['Target']=S2Nodes
    edgematrix['WordsInCommon']=words
    return(edgematrix)
    
    
   
def stableConcordance(word,sents):
    return([sent for sent in sents if word in sent])

def partialmatchConcordance(reob,sents):
    goods=[]
    for sent in sents:
        if([w for w in sent if reob.match(w)]):
            goods.append(sent)
    return (goods)


            
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
    

