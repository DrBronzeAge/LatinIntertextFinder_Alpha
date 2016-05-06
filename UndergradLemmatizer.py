# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 15:45:09 2016
This is what I call the undergraduate's backoff lemmatizer. Like an undergrad,
it tries to use what it knows (CLTK's algorithmic lemmatizer) and when it hits
a word it can't handle, it just looks it up on Perseus. Results are still 
imperfect because it just grabs the parsing at the top, but it does seem to be
fully deterministic
@author: s
"""
import cltk
import requests
import bs4

from cltk.tokenize.word import WordTokenizer
lword=WordTokenizer('latin')
from cltk.stem.lemma import LemmaReplacer
latlem=LemmaReplacer('latin')
from cltk.tag import ner

from cltk.tag.pos import POSTag
postagger=POSTag('latin')


class UndergradBackoffLemmatizer:
    """
    I am what I am and that's all that I am.  It will require an internet 
    connection to function properly.
    """
    
    def __init__(self):
        """
        Really doesn't need anything to initialize.  
        TODO: Maybe add a couple of toggles, so that we don't look up stopwords?
        """
    
    def TagAndLemmatize(self,TokenizedSents):
        TaggedAndLemmatized=[]
        for sent in TokenizedSents:
            TaggedAndLemmatized.append(BackoffLemma([postagger.tag_unigram(w) for w in sent]))
        return(TaggedAndLemmatized)



def BackoffLemma(pack):
    """
    fix cases with no lemma or tag that should have one
    also wastes a lot of time and bandwidth checking punctuation marks
    Soo... apparently perseus considers 'amantissimos' a verb? That's annoying
    
    TODO: this returns a tuple that is unnecessarily embedded in a list. eg:
    [ [['vos','P-----','tu' ]], [['est','v------','sum1']] ]
    rather than:
    [ ['vos','P-----','tu'], ['est','v------','sum1'] ]
    """
    modpack=[]
    for sent in pack:
        tups=[]
        for tup in sent:
            if tup[0] in punct:
                tups.append([tup[0],None,None])
            elif tup[1]==None:
                stuff=GetFromPerseus(tup[0])
                tups.append([tup[0],MakePerseusTag(stuff[1]), stuff[0]])
            else:
                tups.append([tup[0],tup[1], latlem.lemmatize(tup[0])[0]])
        modpack.append(tups)
    return(modpack)


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

#######################
#test
cat3=nltk.corpus.PlaintextCorpusReader(path,'cat3.txt', word_tokenizer=lword) 
cat3s=cat3.sents()   
ugl=UndergradBackoffLemmatizer()
cl=ugl.TagAndLemmatize(cat3s[3:5])