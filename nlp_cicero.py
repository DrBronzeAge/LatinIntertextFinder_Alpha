# -*- coding: utf-8 -*-
"""
Created on Tue Dec  1 13:20:39 2015
Fixed the trouble with cltk. Key to the fix was to build the parts of cltk_data that you need
manually. Most can be found on github.
Also a manual fix for one issue with cltk lemmatizer: it labels
sum, es, et etc. as 'sum1', but their stopword list only includes 'sum'-- no wonder
I was getting like twelve million hits when I look a 6 shingles with an
intersection >3
@author: s
"""

#import pymongo
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
lstops.extend(['sum1']) #seriously, fuck you guys
lstops.extend(['edo1']) #also, your lemmatizer labels 'est' as 'edo1'
lstops.extend(['qui1','vir','fortis','jam'])
lstops.extend(['nihil','parvus','minus','omne','modo','tantus','qualis','civis','bonus'])

bgs=[('res','publica'),('deus','immortalis'),('ut','tam'),('ut','talis'),('ut','tantus'),('neo1','tam'),('neo1','talis'),('neo1','tantus')]
bgs.append(('reor','publica')) #haha it lemmatizes 're' to reor
bgs.append(('redeo','publica'))#and 'rei' to redeo
bgs.extend([('reor','publicum'),('redeo','publicum')])
bgs.extend([('reor','publico'),('redeo','publico'),('res','publico'),('reor','publicus'),('redeo','publicus'), ('res','publicus')])
bgs.extend([('patro','conscribo'),('populus1','Romanus'),('senatus','consulo'),('senatus','populus1'),('senatus','populo')])
#
#from cltk.tokenize.sentence import TokenizeSentence
#lsent=TokenizeSentence('latin')
#lst.tokenize()=lsent.tokenize_sentences
#cltk's sentence tokenizer won't play nicely with nltk's corpus reader.  I
#could fix it, but it isn't worth the bother right now
from cltk.tokenize.word import WordTokenizer
lword=WordTokenizer('latin')
from cltk.stem.lemma import LemmaReplacer
latlem=LemmaReplacer('latin')
from cltk.tag import ner

from cltk.tag.pos import POSTag
postagger=POSTag('latin')


p_red=['postreditum.txt','postreditum2.txt','haruspicum.txt','domo.txt']
path="C:/Users/s/Desktop/Latin_lib/latin_text_latin_library-master/cicero"

#cic1=nltk.corpus.PlaintextCorpusReader(path,p_red, word_tokenizer=lword)

#cic1.sents()[8:10]
#
#
##for reasons not entirely clear to me, they want you to use the various taggers
##as methods, rather than having a class for each
#postagger.tag_ngram_123_backoff(foo)
#
#foo="[1] Litteras tuas accepi pr. Non. Febr. eoque ipso die ex testamento crevi hereditatem. ex multis meis miserrimis curis est una levata si, ut scribis, ista hereditas fidem et famam meam tueri potest; quam quidem intellego te etiam sine hereditate tuis opibus defensurum fuisse.[2] de dote quod scribis, per omnis deos te obtestor ut totam rem suscipias et illam miseram mea culpa et neglegentia tueare meis opibus si quae sunt, tuis quibus tibi molestum non erit facultatibus. quoi quidem deesse omnia, quod scribis, obsecro te, noli pati. in quos enim sumptus abeunt fructus praediorum? iam illa HS L_X_ quae scribis nemo mihi umquam dixit ex dote esse detracta; numquam enim essem passus. sed haec minima est ex iis iniuriis quas accepi; de quibus ad te dolore et lacrimis scribere prohibeor. ex ea pecunia quae fuit in Asia partem dimidiam fere exegi."
#
#
#bar=postagger.tag_ngram_123_backoff(foo)

#OK-- so the data structure we're going to want is a list of threeples-- (word, tag, lemma)
#to do it, we need to sentence tokenize, then postag the sentences, then lemmatize the words.
#I don't think it is worth it to go fourples with NE recognition, but it could be done

#so let's try it:

#They don't like mixing corpus readers.  This POS tagger can't handle a word-tokenized
#sentence, so we'll do it the hard way
#cic1sents=nltk.sent_tokenize(cic1.raw())

#c1postagged=[postagger.tag_ngram_123_backoff(sent) for sent in cic1sents]
##note to self: this takes a while
#c1posNlem=[]
#for sen in c1postagged:
#    c1posNlem.append([(w,t,latlem.lemmatize(w.lower())) for w,t in sen])
#    
    
#OK, so that crash took a lot of work with it.  Let's rebuild
    
def GetFromPerseus(word):
    """
    input is a word from a corpus as a string. output is a list of lemma,
    parser output, dictionary definition.
    
    Try and except block plain because a lot of different things can go wrong,
    but all should produce the same input.
    """
    punct=[',',"'",'"',':','?','.','!',';','-','[',']','(',')']
    if word in punct:
        return([None,None,None])
    try:
        link=GetPerseusLink(word)
        perP=bs4.BeautifulSoup(requests.get(link).text)
        #for now we're only getting the first result
        firstH=perP.find('div', class_='analysis')
        lemma=firstH.find('h4').text.strip()
        LandS=firstH.find('span',class_='lemma_definition').text.strip()
        parsed=firstH.find('td',class_=None).text.strip()
        return(lemma,parsed,LandS)
    except:
        return([None,None,None]) #yeah, that's awful but it needs to 
        #match what cltk does for this to work as a supplement


def GetPerseusLink(word):
    base="http://www.perseus.tufts.edu/hopper/morph?l="
    suff="&la=la"
    link=base+word+suff
    return (link)
    
def MakePerseusTag(pars):
    tag='None' #again, to match cltk
    #catch NoneTypes, because a lot of things will be that
    if pars==None: 
        return(tag)
        
    pal=pars.split(' ')
    
    if pal[0]=='adv':
        tag=AdvTag()
    if pal[0]=='conj':
        tag=ConjTag()
    if pal[0]=='prep':
        tag=PrepTag()
    if pal[0]=='noun' or pal[0]=='adj':
        tag=NounAdjTag(pal)
    if pal[0]=='verb':
        tag==VerbTag(pal)
    if pal[0]=='part':
        tag=PartTag(pal)
    if pal[0]=='pron':
        tag=PronTag(pal)
    return(tag)

#necessary evils, but uninteresting 
def AdvTag():
    return('D--------')
def PrepTag():
    return('R--------')
def ConjTag():
    return('C--------')

def PronTag(pal):
    if pal[3]=='abl':
        case='b'
    else:
        case=pal[3][0]
        
    tag='p-'+pal[1][0]+'---'+pal[2][0]+case+'-'
    return(tag.upper())

def NounAdjTag(pal):
    """
    just to explain what's going on, the booleans check for a problem built into
    the cltk tag system.  They usually use the first letter (nominative maps to 
    'N', etc). But sometimes there are conflicts, and there is no better way 
    to check for them
    """
    try:

        if pal[3]!='abl':
            tag=pal[0][0]+'-'+pal[1][0]+'---'+pal[2][0]+pal[3][0]+'-'
            return(tag.upper())
        else:
            tag=pal[0][0]+'-'+pal[1][0]+'---'+pal[2][0]+'b'+'-'
            return(tag.upper())
    except:
        tag=pal[0][0]+'-------!'
        return(tag.upper())

def VerbTag(pal):
    """
    TODO: Add a check for future perfects.  Pretttty loooow priority, though.
    Treating adjectival participals as verbs is soooo annoying
    """
    if len(pal)==5:
        if 'superl' in pal:
            return(NounAdjTag(pal))
        
        if pal[2]=='inf':
            mood='n'
            if pal[1]=='perf':
                tense='r'
            else:
                tense=pal[1][0]
            tag='v--'+tense+mood+pal[3][0]+'---'
            return(tag.upper())
        elif pal[4]=='imperat':
            mood='r'
        else:
            mood=pal[4][0]
            
        if pal[3]=='perf':
            tense='r'
        elif pal[3]=='plup':
            tense='l'
        else:
            tense=pal[3][0]
        if 'gerundive' not in pal:    
            tag=pal[0][0]+pal[1][0]+pal[2][0]+tense+'-'+pal[4][0]+'---'
        else:
            tag='v-'+pal[1][0]+'---'+pal[3][0]+pal[4][0]+'-'
        return(tag.upper())

         
    if 'superl' in pal:
        return(NounAdjTag(pal))
    
    if pal[2]=='inf':
        mood='n'
        if pal[1]=='perf':
            tense='r'
        else:
            tense=pal[1][0]
        tag='v--'+tense+mood+pal[3][0]+'---'
        return(tag.upper())
    elif pal[4]=='imperat':
        mood='r'
    else:
        mood=pal[2][0]
        
    if pal[3]=='perf':
        tense='r'
    elif pal[3]=='plup':
        tense='l'
    else:
        tense=pal[3][0]
    if 'gerundive' not in pal:    
        tag=pal[0][0]+pal[1][0]+pal[2][0]+tense+mood+pal[5][0]+'---'
    else:
        tag='v-'+pal[1][0]+'---'+pal[3][0]+pal[4][0]+'-'
    return(tag.upper())

def PartTag(pal):
    """
    This one is odd because they seem to double mark participles.  They get a 't'
    at the start of the tag, then also a 'p' indicating that the mood is participial.
    I assume they wanted to be able to collect all verb forms by checking to see
    if it had a letter in position 5 ( index 4)?  
    """
    if pal[2]=='perf':
        tense='r'
        voice='p' #gerundives don't get labled as participles
    else:
        tense=pal[2][0]
        voice='a'# so if past, passive, else active
    
    if pal[4]=='abl':
        case='b'
    else:
        case=pal[4][0]
    
    tag='t-'+pal[1][0]+tense+'p'+voice+pal[3][0]+case+'-'
    return(tag.upper())
    



#for testing
#jupire=re.compile('Iov|Iup')
#jup=[sent for sent in cic1sents if jupire.search(sent)]
#jupwords=[postagger.tag_unigram(sent) for sent in jup ]

def FindRelevantSents(reob, rawtext):
    """
    Meant to narrow down the portion of text to only the relevant bits
    """    
    return([sent for sent in nltk.sent_tokenize(rawtext) if reob.search(sent)])


def FindAgreeWordsInUnparsedsents(reob, unparsedsents):
    """takes a compiled re object and a list of sentences-- that is, it assumes
    that the raw text has been run through a sentence tokenizer, but not a word
    tokenizer yet.  Easy to make it more flexible if the need ever arises"""
    pack=[postagger.tag_unigram(sent) for sent in unparsedsents]
    pack=modifyPack(pack)
    allInSent=[]
    gramrel=[]
    for sent in pack:
        allInSent.extend([(w,l) for w,t,l in sent])
    
        #is possible a word shows up twice, or we get some kind of figura etymologica
        #is probably better not to double, but could be considered undercounting
        #process for getting grammatical matches is more complex-- split into tw
        #functions for readability
        keys=[(w,t,l) for w,t,l in sent if reob.search(w)]
        ktag=keys[0][1] #the pos/parse tag for the term of interest
        if ktag[-2]!='-': #check to see if it has case-- and therefore is a noun/adj
            gramrel.extend(GetSubstConnx(ktag,sent))
        if ktag[0]=='V':
            gramrel=GetVerbConnx(ktag)
    allInSent=[(w,l) for w,l in allInSent if not reob.search(w)] #filter
    gramrel=[(w,l) for w,l in gramrel if not reob.search(w)]     
    return([allInSent,gramrel])

def FindRelevantParsedSentences(reob,parsedsents):
    goods=[]
    for sent in parsedsents:
        if([w for w,t,l in sent if reob.match(w)]):
            goods.append(sent)
    return goods



def FindAgreeWordsInParsedSents(reob, parsedsents):
    """takes a compiled re object and a list of sentences that have been fully
    parsed and pos-tagged.  Assumes that the sentences it gets sent are ones that have
    the word/term included in it"""
#    pack=[postagger.tag_unigram(sent) for sent in sents]
#    pack=modifyPack(pack)
    allInSent=[]
    gramrel=[]
    for sent in parsedsents:
        allInSent.extend([(w,l) for w,t,l in sent])
    
        #is possible a word shows up twice, or we get some kind of figura etymologica
        #is probably better not to double, but could be considered undercounting
        #process for getting grammatical matches is more complex-- split into tw
        #functions for readability
        keys=[(w,t,l) for w,t,l in sent if reob.search(w)]
        ktag=keys[0][1] #the pos/parse tag for the term of interest
        if ktag[-2]!='-': #check to see if it has case-- and therefore is a noun/adj
            gramrel.extend(GetSubstConnx(ktag,sent))
        if ktag[0]=='V':
            gramrel=GetVerbConnx(ktag)
    allInSent=[(w,l) for w,l in allInSent if not reob.search(w)] #filter
    gramrel=[(w,l) for w,l in gramrel if not reob.search(w)]     
    return([allInSent,gramrel])
    

def modifyPack(pack):
    """
    fix cases with no lemma or tag that should have one
    also wastes a lot of time and bandwidth checking punctuation marks
    Soo... apparently perseus considers 'amantissimos' a verb? That's annoying
    """
    modpack=[]
    for sent in pack:
        tups=[]
        for tup in sent:
            if tup[1]==None:
                stuff=GetFromPerseus(tup[0])
                tups.append([tup[0],MakePerseusTag(stuff[1]), stuff[0]])
            else:
                tups.append([tup[0],tup[1], latlem.lemmatize(tup[0])[0]])
        modpack.append(tups)
    return(modpack)
    
    
def GetSubstConnx(ktag,sent):
    """
    takes in a POS tag for the word we're interested in, and a list of tokenized
    sentences, in wich each sentence is a list of (word, POSTag, lemma) tuples
    returns a list of all words that are probably gramattically connected to 
    the word of interest (word,lemma tuples)
    """
    gender=ktag[-3]
    number=ktag[2]
    case=ktag[-2]
    relwords=[]
    relwords.extend([(w,l) for w,t,l in sent if t[-3]==gender and t[2]==number and t[-2]==case])
    if case=='N' or case=='A':
        relwords.extend([(w,l) for w,t,l in sent if t[0]=='V'])
    return (relwords)

def GetVerbConnx(ktag,sent):
    """
    See GetSubstConnx.  One thing to watch out for, it only gets nominatives
    accusatives and adverbs. In many instances will be other important words
    """   
    number=ktag[2]
    relwords=[(w,l) for w,t,l in sent if t[-2]=='N' or t[-2]=='A' or t[0]=='D']
    return(relwords)


#
#
#def ReadySearchforR(reob,rawtext,filestart):
#    """
#    Output will be that it saves two csv files to another directory to use for
#    making wordclouds in R
#    takes a compiled regular expression, a rawtext, and a filename
#    also returns the actual results, for debugging and exploration
#    """
#    fbroad=filestart+'broad.csv'
#    fnarrow=filestart+'tight.csv'
#    
#    sents=FindRelevantSents(reob,rawtext)
#    results=FindAgreeWords(reob,sents)
#    broad=[l for w,l in results[0] if l not in lstops]
#    tight=[l for w,l in results[1] if l not in lstops]
#    bdf=pd.DataFrame(columns=['word','count'])
#    tdf=pd.DataFrame(columns=['word','count'])
#    bfq=nltk.FreqDist(broad)
#    tfq=nltk.FreqDist(tight)
#    
#    
#testfoo=FindAgreeWords(jupire,FindRelevantSents(jupire,cic1.raw()))
#
#
##Ok, let's try to make one for the whole cat3, then pickle it
#
#
#cat3=nltk.corpus.PlaintextCorpusReader(path,'cat3.txt', word_tokenizer=lword)
#cat3sents=nltk.sent_tokenize(cat3.raw())
#
#bar=[postagger.tag_unigram(cat3sents[5])]
#
#modifyPack(bar)
#tester=[w for w,t in postagger.tag_unigram(cat3sents[5])]
#
#catmod3=[]
#for sent in cat3sents[8:]:
#    catmod3.append(modifyPack([postagger.tag_unigram(sent)]))
#
#pack=[postagger.tag_unigram(cat3sents[8])]
#
#
#cat124l=['cat1.txt','cat2.txt','cat4.txt']
#cats=nltk.corpus.PlaintextCorpusReader(path,cat124l, word_tokenizer=lword)
#catsSents=nltk.sent_tokenize(cats.raw())
#
#cat124=[]
#for sent in catsSents[312:]:
#    cat124.append(modifyPack([postagger.tag_unigram(sent)]))
#
#pack=[postagger.tag_unigram(catsSents[312])]
#    
#with open ('cat124Heavy.pickle','wb') as f:
#    pickle.dump(cat124,f)
#    
#    
##group1=['cat1.txt','cat2.txt']
##Trying a new mode of exploration
#
##
##a=set(['a','b','c','d'])
##b=set(['c','d','e','f'])
##
##c=b.intersection(a)
#
#with open ('cat3Heavy.pickle','rb')as f:
#    cat3=pickle.load(f)
#
#with open ('PostReditumHeavy.pickle','rb') as f:
#    prh=pickle.load(f)
#
##something weird with structure here---
#cat3=[sent[0] for sent in cat3]
#prh=[sent[0] for sent in prh]
#acceptabletags=['T','A','D','N','V']
#
#    
#cat3sents=nltk.sent_tokenize(nltk.corpus.PlaintextCorpusReader(path,'cat3.txt', word_tokenizer=lword).raw())
#prsents=nltk.sent_tokenize(nltk.corpus.PlaintextCorpusReader(path,p_red, word_tokenizer=lword).raw())  
#matches=[]
#i=0
#for sent in cat3[0:10]:
#    words=[l for w,t,l in sent if l!=None and l not in lstops and t[0] in acceptabletags]
#    j=0
#    for sen in prh:
#        ws=set([l for w,t,l in sen if l!=None and l not in lstops and t[0] in acceptabletags])
#        if len(ws.intersection(words))>=3:
#            matches.append([cat3sents[i],prsents[j], ws.intersection(words)])
#        j+=1
#    i+=1
#
##ok, lets try shingling
#
#
#foo=cat3[1]

def MakeShingles(sent, shingleSize=8, acceptableTags=['-', 'A', 'C', 'D', 'E', 'M', 'N', 'P', 'R', 'T', 'V']):
    words=[l for w,t,l in sent if l!=None and l not in lstops and t[0] in acceptableTags]
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

def makeEdgeList(speech1,speech2,speech1Name,speech2Name):
    edgematrix=pd.DataFrame(columns=(['S1Node','S2Node','Speech1','Speech2','WordsInCommon']))
    S1Nodes=[]
    S2Nodes=[]
    words=[]
    S1=[]
    S2=[]
    i=0    
    for sent in speech1:
        s1sh=MakeShingles(sent)
        j=0
        for sen in speech2:
            s2sh=MakeShingles(sen)
            mmss=MatchingShingles(s1sh,s2sh)
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
