library('methods')
library('ggplot2')
library('scales')
library('reshape')

mtfile <- "/work/eocoe/eocoe26/jube/Mumps/data.csv"

print(mtfile)

df <- read.csv(mtfile)
linena <- which(is.na(df), arr.ind=TRUE)
linerm <- unique(linena[,'row'])
if(length(linerm)>0){
    df[linerm,]$Memloc <- NA
    df[linerm,]$Memtot <- NA
}
df$Total=df$Analysis+df$Factorisation+df$Preconditioning+df$Solve
df$Niter[df$Niter==0]=NA

df <- df[order(df$Order,df$Solvername,df$Ncores),]

dftime <-df[, c("Solvername","Order","Ncores","Nth","Analysis","Factorisation", 
"Preconditioning","Solve","Total")]
nproc <- min(df$Ncores)
for (ord in unique(dftime$Order)){
    title <- ""
    title <- paste(title,"Multi-threading performances, interpolation ",sep="")
    title <- paste(title,ord,sep="")
    title <- paste(title,",\n",sep="")
    title <- paste(title,nproc,sep="")
    title <- paste(title," MPI processes",sep="")

    dfo <- dftime[dftime$Order==ord,]
    dfom <- melt(dfo,id=c("Solvername","Nth"),measure=c("Analysis","Factorisation", 
"Preconditioning","Solve","Total"))
    print(dfom)
    p <- ggplot(data=dfom, aes(x=factor(Nth),y=value,group=factor(Solvername)))
    p <- p + geom_point(aes(shape=factor(Solvername)), size=4) + geom_line(size=.5)
    p <- p + facet_wrap(~ variable, scales="free")
    p <- p + scale_shape_manual(values = c(16,15,17,18),name = "Solver")
    p <- p + xlab("#threads per process (Remark: #cores=#threads*#process)")
    p <- p + ylab("Time (sec)")
    p <- p + ggtitle(title)  + theme_bw(base_size=20)
    filename <- paste(prefix,"mt_",sep="")
    filename <- paste(filename,ord,sep="")
    filename <- paste(filename,"_times.pdf",sep="")
    ggsave(filename, width=12,height=6)
}

