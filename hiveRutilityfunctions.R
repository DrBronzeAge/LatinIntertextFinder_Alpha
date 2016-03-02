#Housekeeping

library(HiveR)
library(grid)
library(RColorBrewer)
setwd("~/Python Scripts")

resetRads<-function(hiveObject){
  labs<-hiveObject$nodes$lab
  labs<-gsub('  ',' ',labs) #not sure where these extra spaces are coming from, but they're a pain
  rads<-c()
  for (i in 1:length(labs)){
    rads[i]<-as.numeric(unlist(strsplit(labs[i],' '))[2])
  }
  hiveObject$nodes$radius<-rads
  return(hiveObject)
}


MakeEdgeWeights<-function(wordsvector,threshold=3){
  end<-length(wordsvector)
  ews<-c()
  for (i in 1:end){
    wds<-as.character(wordsvector[i])
    ews[i]<-length(unlist(strsplit(wds,'  ')))-(threshold-1)
  }
  return(ews)
}

colourEdgeByWord<-function(colour,word,wordvector,edgevector){
  key<-grepl(word,wordvector)
  edgevector[key]<-colour
  return(edgevector)
}

resetAxes<-function(hiveObject){
  labs<-hiveObject$nodes$lab
  speeches<-c()
  for (i in 1:length(labs)){
    speeches[i]<-unlist(strsplit(labs[i],' '))[1]
  }
  uniSpeech<-unique(speeches)
  for (i in 1:length(uniSpeech)){
    key<-grepl(uniSpeech[i],labs)
    hiveObject$nodes$axis[key]<-i
  }
  return(hiveObject)
}

WeightNodesByEdges<-function(hiveObject){
  for (i in 1: length(hiveObject$nodes$id)){
    hiveObject$nodes$size[i]<-length(hiveObject$edges$color[hiveObject$edges$id1==i|hiveObject$edges$id2==i])
    
  }
  return(hiveObject)
}

#Below is code to actually make plots

# prs<-read.csv('prs_edgematrix4.csv')
# prq<-read.csv('prq_edgematrix4.csv')
# har<-read.csv('har_edgematrix4.csv')
# dd<-read.csv('dd_edgematrix4.csv')
# #ddhar<-read.csv('dd_har_edgematrix.csv')
# 
# em<-rbind(prs,prq)
# em<-rbind(em,har)
# em<-rbind(em,dd)
# 
# em<-em[,2:6]
# 
# fooem<-edge2HPD(edge_df = em,type="3D")
# 
# em2d<-rbind(dd,har)
# #em2d<-rbind(em2d,ddhar)
# 
# #MakeEdgeWeights(em$WordsInCommon,3)
# fooem<-resetAxes(fooem)
# 
# fooem<-resetRads(fooem)
# #colourEdgeByWord('Navy','public',em$WordsInCommon,fooem$edges$color)
# fooem$edges$color<-colourEdgeByWord('Navy','sceler',em$WordsInCommon,fooem$edges$color)
# fooem$edges$color<-colourEdgeByWord('Orange','consu',em$WordsInCommon,fooem$edges$color)
# fooem$edges$color<-colourEdgeByWord('Cyan','conloc',em$WordsInCommon,fooem$edges$color)
# fooem$edges$color<-colourEdgeByWord('Cyan','co[nl]loc',em$WordsInCommon,fooem$edges$color)
# 
# 
# #fooem<-edge2HPD(edge_df = em)
# #fooem$nodes
# fooem$edges$weight<-MakeEdgeWeights(em$WordsInCommon,3)
# 
# plot3dHive(fooem, ch=1,axLabs = c('Cat','Post Red. S','Post Red. Q.','Haruspicum','De Domo'))
# #OK, so the edge list keeps the order of the csv
# 
# #try a 2d
# #themcols<-brewer.pal(8,'Accent')
# themcols<-brewer.pal(8,'Dark2')
# #themcols<-brewer.pal(8,'Spectral')
# dh2<-edge2HPD(edge_df = em2d[,2:6], type="2D")
# dh2<-resetAxes(dh2)
# dh2<-resetRads(dh2)
# dh2$nodes$radius[dh2$nodes$radius<=0]<-1
# dh2$edges$color<-themcol[8]
# #dh2$edges$color<-colourEdgeByWord(themcols[3],'caed',em2d$WordsInCommon,dh2$edges$color)
# dh2$edges$color<-colourEdgeByWord(colours()[645],'meus',em2d$WordsInCommon,dh2$edges$color)
# dh2$edges$color<-colourEdgeByWord(colours()[73],'consilium',em2d$WordsInCommon,dh2$edges$color)
# #change the colour of the nodes for the catilinarians
# nodes<-dh2$nodes
# edges<-dh2$edges
# lv<-grepl('Cat',dh2$nodes$lab)
# lv2<-grep('Domo',dh2$nodes$lab)
# lv3<-grep('Harus',dh2$nodes$lab)
# dh2$nodes$color[lv]<-themcols[3]
# dh2$nodes$color[which(dh2$nodes$radius<428 & lv)]<-themcols[4]
# dh2$nodes$color[which(dh2$nodes$radius<310 & lv)]<-themcols[3]
# dh2$nodes$color[lv2]<-themcols[5]
# dh2$nodes$color[lv3]<-themcols[1]
# dh2<-WeightNodesByEdges(dh2)
# dh2$nodes$size<-sqrt(dh2$nodes$size)
# dh2$edges$weight<-MakeEdgeWeights(em2d$WordsInCommon)
# 
#  #cat1&2
# dh2$edges$weight<-dh2$edges$weight*1.5
# plotHive(dh2,ch=0.08, method='norm', bkgnd='white',axLabs=c('In Catilinam 1-4','De Domo','Haruspicum \nResponsis'),
#          axLab.gpar=gpar(col='Black',cex=1.1,fontface='italic',fontfamily='A'),axLab.pos = c(.2,.2,.3))
# #would you like me to add edges for hic tu etiam? Can call out with colour
# #
# #6:37
# plotHive(dh2,ch=0.08, method='norm', bkgnd='white')
# #9:05:30
# #1:56