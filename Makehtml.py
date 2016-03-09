# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 19:11:09 2015
Fastest/best way to prettify output from the intertextuality engine

@author: s
"""


import re
import yattag
import webbrowser
from yattag import Doc




def MakeHTMLTable(matchList,title1='Text1',title2='Text2',
                  pathPlusName='JaccardIntertextOutput.html'):
    """
    Makes a relatively pretty table of your possible intertexts
    
    Args:
    
    matchList (list): a list of triples [(sentence1,sentence2,wordsInCommon)],
        where wordsInCommon is itself a tuple (from sentence1, from sentence2).
    
    title1(str): the title of the work from which all 'sentence1' elements are 
        drawn.
        
    title2(str): the title of the work from which all 'sentence2' elements are 
        drawn.
    
    pathPlusName (str): optional filename + path, in case you want to keep
        this html page for some reason. 
    """
    
    doc, tag, text = Doc().tagtext()
    
    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('head'):
            with tag('title'):
                text('Do do do Inspector Gadget (for intertexts)')
            with tag('style'):
                text("""
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                
                th, td {
                    text-align: left;
                    padding: 8px;
                }
                
                tr:nth-child(even){background-color: #f2f2f2}
                tr:hover{background-color:#faebd7}""")
        #TODO: Add some css styling
        with tag('body'):
            with tag('h1'):
                text('Possible Intertextualites between '+title1+' and '+title2)
            with tag('table', style='width:100%', border='1'):
               #headings
                with tag('tr'):
                    with tag('th'):
                        text(title1)
                    with tag('th'):
                        text(title2)
                    with tag ('th'):
                        text('Words in Common')
                #rows        
                for match in matchList:
                    with tag('tr'):
                        with tag('td'):
                            sent1=match[0]
                            for word in match[2][0]: 
                                bword=re.compile(' '+word+'[ ,.?!]')
                                sent1=re.sub(bword,' <b>'+word+' </b>',sent1)
                            doc.asis(sent1)
                        with tag('td'):
                            sent2=match[1]
                            for word in match[2][1]:
                                bword=re.compile(' '+word+'[ ,.?!]')
                                sent2=re.sub(bword,' <b>'+word+' </b>',sent2)
                            doc.asis(sent2)
                        with tag('td'):
                            text(str(match[2]))
                
    a=doc.getvalue()
    with open (pathPlusName,'w') as f:
        f.write(a)
    webbrowser.open(pathPlusName)


