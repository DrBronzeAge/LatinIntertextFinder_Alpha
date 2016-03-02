This is the alpha version of a module that finds and visualizes intertextualites in Latin-- initially built for the speeches of Cicero.
It tackles the problem by lemmatizing all the words in the speech, then splitting each sentence into a bag of shingles. If sentences have 
any shingles that cross a threshold for Jaccard similarity they are flagged and eventually dumped into html for easier expert inspection.
There are also functions to visualize the density and distribution of intertexts, but those currently rely on R.