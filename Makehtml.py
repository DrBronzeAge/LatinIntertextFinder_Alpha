# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 19:11:09 2015
Fastest/best way to prettify output from the intertextuality engine

@author: s
"""

import bs4
import requests
import re
import yattag

#All of this stuff at the top was an effort to make sentences correspond to section numbers.
#it worked, but isn't terrible re-usable, at least in its current form

#PRSenate=bs4.BeautifulSoup(requests.get('http://www.thelatinlibrary.com/cicero/postreditum.shtml').text)
#PrQuirites=bs4.BeautifulSoup(requests.get('http://www.thelatinlibrary.com/cicero/postreditum2.shtml').text)
#DeDomo=bs4.BeautifulSoup(requests.get("http://www.thelatinlibrary.com/cicero/domo.shtml").text)
#Haruspicum=bs4.BeautifulSoup(requests.get("http://www.thelatinlibrary.com/cicero/haruspicum.shtml").text)
# prs=nltk.corpus.PlaintextCorpusReader(path,'postreditum.txt', word_tokenizer=lword).raw()
# prsSect=prs.split('[')
# ff=re.compile('^\[',re.M)
# prsSect=re.split(ff,prs)
# domo=nltk.corpus.PlaintextCorpusReader(path,'domo.txt', word_tokenizer=lword).raw()
# domoSect=domo.split('. [' or '? [')
# fre=re.split(sBreak,domo)
# catSect=nltk.corpus.PlaintextCorpusReader(path,'cat3.txt', word_tokenizer=lword).raw().split('[')
# hsect=nltk.corpus.PlaintextCorpusReader(path,'haruspicum.txt', word_tokenizer=lword).raw().split('. [')
# prmatches=[(cat,[sect for sect in prsSect if mat[4:-4] in sect][0],words)
#  for cat,mat,words in shinMatches if mat in str([pr.text for pr in PRSenate.find_all('p')])]

# prqmatches=[(cat,[pr.text for pr in PrQuirites.find_all('p') if mat in pr.text][0],words)
#  for cat,mat,words in shinMatches if mat in str([pr.text for pr in PrQuirites.find_all('p')])]
     
# DDmatches=[(cat,[sect for sect in domoSect if mat[4:-4] in sect][0],words)
#  for cat,mat,words in shinMatches if mat in str([pr.text for pr in DeDomo.find_all('p')])]

# hpmatches=[(cat,[sect for sect in hsect if mat[10:-10] in sect][0],words)
#  for cat,mat,words in shinMatches if mat in str([pr.text for pr in Haruspicum.find_all('p')])]

     
# Catil=bs4.BeautifulSoup(requests.get("http://www.thelatinlibrary.com/cicero/cat3.shtml").text)
# from yattag import Doc

#generate html files for each in order

doc, tag, text = Doc().tagtext()

doc.asis('<!DOCTYPE html>')
with tag('html'):
    with tag('body'):
        with tag('h2'):
            text('Post Reditum Ad Senatus')
        with tag('table', style='width:100%', border='1'):
            for match in prmatches:
                with tag('tr'):
                    with tag('td'):
                        foo=match[0]
                        for word in match[2][1]: #for some reason, I put those in there backwards
                            bword=re.compile(' '+word+'[ ,.?!]')
                            foo=re.sub(bword,' <b>'+word+' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        foo=match[1]
                        for word in match[2][0]:
                            bword=re.compile(' '+word+'[ ,.?!]')
                            foo=re.sub(bword,' <b>'+word+' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        text(str(match[2]))
            
a=doc.getvalue()

with open ('PostReditumAdSentatusintertext.html','w') as f:
    f.write(a)
    
    
    
    
doc, tag, text = Doc().tagtext()

doc.asis('<!DOCTYPE html>')
with tag('html'):
    with tag('body'):
        with tag('h2'):
            text('Post Reditum Ad Quirites')
        with tag('table', style='width:100%', border='1'):
            for match in prqmatches:
                with tag('tr'):
                    with tag('td'):
                        foo=match[0]
                        for word in match[2][1]: #for some reason, I put those in there backwards
                            bword=re.compile('[ ]'+word+'[ ,.?!]')
                            foo=re.sub(bword,r' <b>'+word+r' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        foo=match[1]
                        for word in match[2][0]:
                            bword=re.compile('[ ]'+word+'[ ,.?!]')
                            foo=re.sub(bword,r' <b>'+word+r' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        text(str(match[2]))
            
a=doc.getvalue()

with open ('PostReditumAdQuiritesintertext.html','w') as f:
    f.write(a)


#for domo
doc, tag, text = Doc().tagtext()

doc.asis('<!DOCTYPE html>')
with tag('html'):
    with tag('body'):
        with tag('h2'):
            text('De Domo')
        with tag('table', style='width:100%', border='1'):
            for match in DDmatches:
                with tag('tr'):
                    with tag('td'):
                        foo=match[0]
                        for word in match[2][1]: #for some reason, I put those in there backwards
                            bword=re.compile('[ ]'+word+'[ ,.?!]')
                            foo=re.sub(bword,r' <b>'+word+r' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        foo=match[1]
                        for word in match[2][0]:
                            bword=re.compile('[ ]'+word+'[ ,.?!]')
                            foo=re.sub(bword,r' <b>'+word+r' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        text(str(match[2]))
            
a=doc.getvalue()

with open ('DeDomointertext.html','w') as f:
    f.write(a)
    

doc, tag, text = Doc().tagtext()

doc.asis('<!DOCTYPE html>')
with tag('html'):
    with tag('body'):
        with tag('h2'):
            text('Haruspicum')
        with tag('table', style='width:100%', border='1'):
            for match in hpmatches:
                with tag('tr'):
                    with tag('td'):
                        foo=match[0]
                        for word in match[2][1]: #for some reason, I put those in there backwards
                            bword=re.compile('[ ]'+word+'[ ,.?!]')
                            foo=re.sub(bword,r' <b>'+word+r' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        foo=match[1]
                        for word in match[2][0]:
                            bword=re.compile('[ ]'+word+'[ ,.?!]')
                            foo=re.sub(bword,r' <b>'+word+r' </b>',foo)
                        doc.asis(foo)
                    with tag('td'):
                        text(str(match[2]))
            
a=doc.getvalue()
b=a.encode(encoding='utf-8',errors='replace')
b=str(b)
with open ('Haruspicum_intertext.html','w') as f:
    f.write(a)

#print(doc.getvalue())
#
#g=prmatches[0]
#c=g[0]
#p=g[1]
#word=g[2][1]
#for word in 

dummy=bs4.BeautifulSoup(a)

dummy.find('tr').find('td').text=dummy.find('tr').find('td').text.replace('Rem','DidThisWork')

g='aaa'
b=re.compile(' '+g+'[ ,.]')

tester='baaa aaa baaab'
re.sub(b,'I win',tester)

