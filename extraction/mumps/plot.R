library('methods')
library('ggplot2')
library('scales')
library('reshape')
library(RColorBrewer)

makeColors <- function(){
  maxColors <- 10
  usedColors <- c()
  possibleColors <- colorRampPalette( brewer.pal( 9 , "Set1" ) )(maxColors)
  
  function(values){/usr/lib/gimp/2.0/plug-ins
    newKeys <- setdiff(values, names(usedColors))
    newColors <- possibleColors[1:length(newKeys)]
    usedColors.new <-  c(usedColors, newColors)
    names(usedColors.new) <- c(names(usedColors), newKeys)
    usedColors <<- usedColors.new

    possibleColors <<- possibleColors[length(newKeys)+1:maxColors]
    usedColors
  }
}
mkColor <- makeColors()

mtfile <- "/work/eocoe/eocoe26/jube/Mumps/output_folder/000025/result/table_output_csv.dat"
print(mtfile)
df <- read.csv(mtfile)
df <- read.csv(mtfile, header=T)
ggplot(data=df, aes(x=threadspertask, y=facto, group=nodes, colour=factor(nodes), fill=factor(nodes))) + geom_line(size=2) + scale_colour_manual(values = mkColor(df$nodes)) + scale_fill_manual(values = mkColor(df$nodes))  + ggtitle("Factorisation times with strong scaling for TOKAM3X no inertia divertor") + xlab("Number of threads") + ylab("Time for factorization")+theme_bw()+ theme(text = element_text(size=30, face="bold"),  axis.text.x = element_text(angle = 90, hjust =1)) + scale_x_discrete(labels=df$threadspertask)
ggplot(data=df, aes(x=threadspertask, y=analysis, group=nodes, colour=factor(nodes), fill=factor(nodes))) + geom_line(size=2) + scale_colour_manual(values = mkColor(df$nodes)) + scale_fill_manual(values = mkColor(df$nodes))  + ggtitle("Analysis times with strong scaling for TOKAM3X no inertia divertor") + xlab("Number of threads") + ylab("Time for analysis")+theme_bw()+ theme(text = element_text(size=30, face="bold"),  axis.text.x = element_text(angle = 90, hjust =1)) + scale_x_discrete(labels=df$threadspertask)
