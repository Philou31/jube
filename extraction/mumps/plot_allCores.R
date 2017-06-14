                                        # R script to generate plots from allCores csv file
library('methods')
library('ggplot2')
library('scales')
library('reshape')

args <- commandArgs(TRUE)
prefix <- args[1]     # prefix for output files
allCoresfile <- args[2]  # csv file allCores results

print(allCoresfile)

df <- read.csv(allCoresfile)
linena <- which(is.na(df), arr.ind=TRUE)
linerm <- unique(linena[,'row'])
if(length(linerm)>0){
    df[linerm,]$Memloc <- NA
    df[linerm,]$Memtot <- NA
}
df$Solver=df$Analysis+df$Factorisation+df$Preconditioning+df$Solve
df$Niter[df$Niter==0]=NA

                                        # Time per code part

timeparts <- function(df,meas,prefix,ylab,fileext){
    if(nrow(df)>1){
        orders <- unique(df$Order)
        wbar = .8
        cols <- c("black","darkred","green","blue")
        for (ord in orders){
            title <- "Times by step, interpolation "
            title <- paste(title,ord)
            dataord <- df
            dataord <- melt(dataord[dataord$Order==ord,],id=c("Solvername","Nth","Ncores"),measure=meas)
            dataord <- dataord[order(dataord$Ncores,dataord$Nth),]
            rows <- seq(1,length(dataord$Ncores))
            rownames(dataord) <- rows
            dataord$Ncores2 <- factor(dataord$Ncores,labels = paste(unique(dataord$Ncores)," cores"))

            p <- ggplot(data=dataord, aes(x=factor(Nth),y=value,fill=factor(variable))) 
            p <- p + geom_bar(position="stack",stat="identity",width=wbar) + facet_grid(Ncores2 ~ Solvername)
            p <- p + scale_x_discrete(breaks=unique(dataord$Nth))
            p <- p + xlab("#threads per process (Remark: #process=#cores/#threads)")
            p <- p + ylab(ylab)
            p <- p + scale_fill_manual(values=cols,name="Solver step",label=meas)
            p <- p + ggtitle(title) + theme_bw(base_size=20)
            filename <- paste(prefix,fileext,sep="")
            filename <- paste(filename,ord,sep="_")
            filename <- paste(filename,"pdf",sep=".")
            ggsave(filename, width=12,height=10)
        }
    }
}

speedup_ncores<- function(df,solvername,prefix){
    if(nrow(df)>1){
        orders <- unique(df$Order)
        wbar = .5
        if(solvername=="MUMPS"){
            cols <-  c("black","darkred","blue")
        } else {
            cols <- c("black","darkred","green","blue")
        }
        for (ord in orders){
            title <- paste(solvername,"best speedups, interpolation ")
            title <- paste(title,ord)
            dataord <- df
            dataord <- df[dataord$Order==ord,]
            dataord <- dataord[order(dataord$Ncores,dataord$Nth),]
            rows <- seq(1,length(dataord$Ncores))
            rownames(dataord) <- rows

            cores <- sort(unique(dataord$Ncores))
            su <- rep(1,length(cores))
            ideal <- rep(1,length(cores))
            nth <- rep(1,length(cores))
            mincores <- min(cores)
            tref <- min(dataord[dataord$Ncores==mincores,]$Solver,na.rm=TRUE)

            for (i in 1:length(cores)) {
                
                dnc <- dataord[dataord$Ncores==cores[i],]
                minrow <- dnc[which.min(dnc$Solver),]
                su[i] <- tref/minrow$Solver
                ideal[i] <- minrow$Ncores/mincores
                nth[i] <- minrow$Nth
            }

            dfsu <- data.frame(cores,ideal,su,nth)
            dfsu$label <- paste("#th = ",as.character(dfsu$nth),sep="")
            dataord <- melt(dfsu,id=c("cores","nth","label"))
            dataord[dataord$variable=="su",]$label = ""
            p <- ggplot(data=dataord, aes(x=factor(cores),y=value,fill=factor(variable))) 
            p <- p + geom_bar(position="identity",stat="identity",width=wbar,alpha=.6)
            p <- p + scale_x_discrete() + scale_y_discrete(breaks=c(ideal))
            p <- p + xlab("#cores")
            p <- p + ylab("Speedup")
            p <- p + ggtitle(title)  + theme_bw(base_size=22)
            p <- p + geom_text(data=dataord,aes(x=factor(cores),y=value,label=label),vjust=-0.5,size=6)
            p <- p + scale_fill_manual(values=c("darkblue","red"),name="Solver",label=c("Ideal",solvername))  
            filename <- paste(prefix,solvername,sep="")
            filename <- paste(filename,"_speedup_",sep="")
            filename <- paste(filename,ord,sep="")
            filename <- paste(filename,".pdf",sep="")
            ggsave(filename, width=10,height=6)
        }
    }
}

                                        # Times and Memory comparisons
compare <- function(df,meas,prefix,plot_type){
    titlepref <- ""
    orders <- unique(df$Order)
    dfmeas <- df[,c("Order","Solvername","Nth","Ncores")]
    dfmeas$meas <-df[,c(meas)]
    if(meas == "Solver"){
        measpref <- "Execution times, interpolation"
        unit <- "time (sec)"
        ofileprefix <- paste(prefix,"time",sep="")
    } else if(meas == "Memloc") {
        measpref <- "Maximum local memory, interpolation"
        unit <- "memory (MB)"
        ofileprefix <- paste(prefix,"maxmemloc",sep="")
    } else if(meas == "Niter") {
        measpref <- "Maximum number of iterations, interpolation"
        unit <- "niter"
        ofileprefix <- paste(prefix,"niter",sep="")
    } else {
        measpref <- "Maximum global memory, interpolation"
        unit <- "memory (MB)"
        ofileprefix <- paste(prefix,"maxmemglob",sep="")
    }
    titleprefix <-  paste(titlepref,measpref)
    for (ord in orders){
        dataord <- dfmeas
        dataord <- dataord[dataord$Order==ord,]
        dataord <- dataord[order(dataord$Solvername,dataord$Ncores,dataord$Nth),]
        dataord <- dataord[complete.cases(dataord),]
        rows <- seq(1,length(dataord$Ncores))
        rownames(dataord) <- rows
        if(plot_type == "bar"){
            compare_plotbar(dataord,meas,ofileprefix,titleprefix,unit,ord)
        } else if (plot_type =="curve") {
            compare_plotcurve(dataord,meas,ofileprefix,titleprefix,unit,ord)
        } else {
            compare_plotbar(dataord,meas,ofileprefix,titleprefix,unit,ord)
            compare_plotcurve(dataord,meas,ofileprefix,titleprefix,unit,ord)
        }
    }
}

compare_plotbar <- function(dataord,meas,ofileprefix,titleprefix,ylabel,ord){
    title <- paste(titleprefix,ord)
    wbar = .8
    dataord$Ncores2 <- factor(dataord$Ncores,labels = paste(unique(dataord$Ncores)," cores"))
    p <- ggplot(data=dataord, aes(x=factor(Nth),y=meas,fill=factor(Solvername))) 
    p <- p + geom_bar(position="dodge",stat="identity",width=wbar,alpha=.6)
    p <- p + facet_grid(Ncores2 ~ ., scales="free")
    p <- p + scale_x_discrete()
    p <- p + xlab("#threads per process (Remark: #process=#cores/#threads)")
    p <- p + ylab(ylabel)
    p <- p + scale_fill_manual(values=c("red","darkblue","darkgreen","black"),name="Solver")
    p <- p + ggtitle(title)  + theme_bw(base_size=20)
    filename <- paste(ofileprefix,ord,sep="")
    filename <- paste(filename,"_bar.pdf",sep="")
    ggsave(filename, width=10,height=6)
}

compare_plotcurve <- function(dataord,meas,ofileprefix,titleprefix,ylabel,ord){
    title <- paste(titleprefix,ord)
    dataord$Ncores2 <- factor(dataord$Ncores,labels = paste(unique(dataord$Ncores)," cores"))
    mincore=(min(dataord$Ncores))
    minval=max(dataord[dataord$Ncores==mincore,]$meas,na.rm=TRUE) 
    maxcore=max(dataord$Ncores)
    maxval =minval/(maxcore/mincore)
    df <- data.frame(x1 = mincore, x2 = maxcore, y1 = minval, y2 = maxval)
    
    p <- ggplot(data=dataord, aes(x=Ncores,y=meas,colour=factor(Nth))) 
    p <- p + geom_line(size=1) + geom_point(size=4)
    cols <- c("orange","darkgreen","red","blue","black","purple","yellow")    
    breaks <- unique(dataord$Nth)
    if(meas=="Solver"){
        p <- p + geom_segment(aes(x=x1,y=y1,xend=x2,yend=y2,colour="Slope=-2"), size=1, linetype=2, data = df)
        if(max(breaks) > 9){
            cols <- c("blue","orange","darkgreen","red","black","purple","yellow")
        }
        breaks <- c(breaks,"Slope=-2")
    }
    p <- p + scale_x_log10(breaks = unique(dataord$Ncores))   
    p <- p + scale_color_manual(values=cols,name="#threads per\n process",breaks=breaks)
    p <- p + xlab("#cores (Remark: #process=#cores/#threads)") +ylab(ylabel)
    p <- p + facet_grid(.~ Solvername) + scale_alpha_discrete()
    p <- p + ggtitle(title)  + theme_bw(base_size=20)
    filename <- paste(ofileprefix,ord,sep="")
    filename <- paste(filename,"_curve.pdf",sep="")
    ggsave(filename, width=16,height=6)   
}

compare_best <- function(df,meas,prefix){
    titlepref <- ""
    orders <- unique(df$Order)
    dfmeas <- df[,c("Order","Solvername","Nth","Ncores")]
    dfmeas$meas <-df[,c(meas)]
    if(meas == "Solver"){
        measpref <- "Best execution times, interpolation"
        unit <- "time (sec)"
        ofileprefix <- paste(prefix,"time",sep="")
    } else if(meas == "Memloc") {
        measpref <- "Maximum local memory, interpolation"
        unit <- "memory (MB)"
        ofileprefix <- paste(prefix,"maxmemloc",sep="")
    } else if(meas == "Niter") {
        measpref <- "Maximum number of iterations, interpolation"
        unit <- "niter"
        ofileprefix <- paste(prefix,"niter",sep="")
    } else {
        measpref <- "Maximum global memory, interpolation"
        unit <- "memory (MB)"
        ofileprefix <- paste(prefix,"maxmemglob",sep="")
    }
    titleprefix <-  paste(titlepref,measpref)
    for (ord in orders){
        dataord <- dfmeas
        dataord <- dataord[dataord$Order==ord,]
        dataord <- dataord[order(dataord$Solvername,dataord$Ncores,dataord$Nth),]
        dataord <- dataord[complete.cases(dataord),]

        rows <- seq(1,length(dataord$Ncores))
        rownames(dataord) <- rows
        title <- paste(titleprefix,ord)
        dataord$Ncores2 <- factor(dataord$Ncores,labels = paste(unique(dataord$Ncores)," cores"))
        mincore=(min(dataord$Ncores))
        minval=max(dataord[dataord$Ncores==mincore,]$meas,na.rm=TRUE) 
        maxcore=max(dataord$Ncores)
        maxval =minval/(maxcore/mincore)
        df <- data.frame(x1 = mincore, x2 = maxcore, y1 = minval, y2 = maxval)
        
        p <- ggplot(data=dataord, aes(x=Ncores,y=meas)) 
        p <- p + geom_line(aes(group=factor(Solvername)),size=1) + geom_point(aes(x=Ncores,shape=factor(Solvername),colour=factor(Nth)), size=6)
        cols <- c("orange","darkgreen","red","blue","black","purple","yellow")    
        breaks <- unique(dataord$Nth)
        if(meas=="Solver"){
            p <- p + geom_segment(aes(x=x1,y=y1,xend=x2,yend=y2,colour="Slope=-2"), size=1, linetype=2, data = df)
            if(max(breaks) > 9){
                cols <- c("blue","orange","darkgreen","red","black","purple","yellow")
            }
            breaks <- c(breaks,"Slope=-2")
        }
        p <- p + scale_x_log10(breaks = unique(dataord$Ncores))   
        p <- p + scale_color_manual(values=cols,name="#threads per\n process",breaks=breaks)
        p <- p + xlab("#cores (Remark: #process=#cores/#threads)") +ylab(unit)
        p <- p + scale_alpha_discrete()
        p <- p + scale_shape_manual(values = c(16,15,17,18),name = "Solver")
        p <- p + ggtitle(title)  + theme_bw(base_size=20)
        filename <- paste(ofileprefix,ord,sep="")
        filename <- paste(filename,"_best.pdf",sep="")
        ggsave(filename, width=10,height=6)          
    }
}


if(nrow(df)>0){
    timeparts(df,c("Analysis","Factorisation","Preconditioning","Solve"),prefix, "Time (sec)","timeparts")
                                        #    speedup_ncores(df,prefix)
    compare(df,"Solver",prefix,"both")
    compare(df,"Memloc",prefix,"both")
    compare(df,"Memtot",prefix,"both")
    compare(df,"Niter",prefix,"both")
}


                                        # Select best times per number of cores for each solver & plot



dfres <- df[df$Order=="dummy",]
ind <- 1
for (ord in unique(df$Order)){
    dfo <- df[df$Order==ord,]
    for (solver in unique(dfo$Solvername)){
        dfos <- dfo[dfo$Solvername==solver,]
        for (ncores in unique(dfos$Ncores)){
            dfosn <- dfos[dfos$Ncores==ncores,]
            mintime <- min(dfosn$Solver,na.rm=TRUE)
            dfres[ind,] <- dfosn[dfosn$Solver==mintime,]
            ind <- ind + 1
        }
    }
}
dfres <- dfres[order(dfres$Order,dfres$Solvername,dfres$Ncores),]
compare_best(dfres,"Solver",prefix)
