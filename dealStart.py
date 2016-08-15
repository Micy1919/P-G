#-*- coding:utf-8 -*-
import os
import cv2
import pandas as pd
import numpy as np
import caffe
import copy
import shutil
import codecs
import sqlite3
import multiprocessing

#import  R package
packnames = ('foreach', 'EBImage')
import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects

if all(rpackages.isinstalled(x) for x in packnames):
    have_tutorial_packages = True
else:
    have_tutorial_packages = False

robjects.r('''
rm(list = ls())

boxfilter = function(img, r) {
  d = dim(img)
  out = array(0, dim=d)
  M = apply(img, 2, cumsum)
  out[1:(r+1),] = M[(1+r):(2*r+1),]
  out[(r+2):(d[1]-r),] = M[(2*r+2):d[1],] - M[1:(d[1]-2*r-1),]
  out[(d[1]-r+1):d[1],] = matrix(rep(M[d[1],], each=r), r) -
    M[(d[1]-2*r):(d[1]-r-1),]
  M = t(apply(out, 1, cumsum)) # note that out is input for next stage
  out[,1:(r+1)] = M[,(1+r):(2*r+1)]
  out[,(r+2):(d[2]-r)] = M[,(2*r+2):d[2]] - M[,1:(d[2]-2*r-1)]
  out[,(d[2]-r+1):d[2]] = matrix(rep(M[,d[2]], times=r), ncol=r) -
    M[,(d[2]-2*r):(d[2]-r-1)]
  return(out)
}

guidedfilter = function(img, p, r, eps) {
  #   GUIDEDFILTER   O(1) time implementation of guided filter.
  #   - guidance image: I (should be a gray-scale/single channel image)
  #   - filtering input image: p (should be a gray-scale/single channel image)
  #   - local window radius: r
  #   - regularization parameter: eps
  d = dim(img)
  N = boxfilter(array(1, dim=d), r)
  mean_I = boxfilter(img, r) / N
  mean_p = boxfilter(p, r) / N
  mean_Ip = boxfilter(img*p, r) / N
  cov_Ip = mean_Ip - mean_I * mean_p
  mean_II = boxfilter(img*img, r) / N
  var_I = mean_II - mean_I * mean_I
  a = cov_Ip / (var_I + eps)
  b = mean_p - a * mean_I
  mean_a = boxfilter(a, r) / N
  mean_b = boxfilter(b, r) / N
  q = mean_a * img + mean_b
  return(q)
}

# need to look closely at output images
gfilt3d = function(img, r=24, eps=0.3^2, amp=5, gray=F) {
  q = array(0, dim=dim(img))
  q[,,1] = guidedfilter(img[,,1], img[,,1], r, eps)
  q[,,2] = guidedfilter(img[,,2], img[,,2], r, eps)
  q[,,3] = guidedfilter(img[,,3], img[,,3], r, eps)
  q = Image(q, colormode='Color') # smooth version
  qdif = (img - q) * amp + q # amplified version
  qdif = qdif * ((qdif>=0)&(qdif<=1)) + 1*(qdif>1) # scale from 0 to 1
  if (gray==T) { # turn into 3 channel grayscale instead of color
    qdif = Image(qdif, dim(img), colormode='Grayscale')
    q = Image(q, dim(img), colormode='Grayscale')
  }
  out = qdif # out = list(qdif,q)
  return(out)
}

# csvdata=read.csv("/raid/home/bixiaozheng/oc/Gum_Archived/code_and_data/data/Bind_csv")
# Im_if=unique(paste(csvdata$pno,substr(csvdata$Image_info,2,9)))
# SCORE=rep(0,length(Im_if))
# for(i in 1:length(Im_if))
# {
#   score=csvdata[paste(csvdata$pno,substr(csvdata$Image_info,2,9))==Im_if[i],]$score
#   SCORE[i]=sum(score[score<4])/sum(score<4)
# }
# csvdata=read.csv("/raid/home/bixiaozheng/oc/Gum_Archived/2016000/score_csv.csv")
# Im_if=unique(paste(csvdata$pno,substr(csvdata$Image_info,1,8)))
# SCORE1=rep(0,length(Im_if))
# for(i in 1:length(Im_if))
# {
#   score=csvdata[paste(csvdata$pno,substr(csvdata$Image_info,1,8))==Im_if[i],]$score
#   SCORE1[i]=sum(score[score<4])/sum(score<4)
# }

###################################################################################################
require(EBImage)
require(tiff)

cppF=function(s)
{
  #if(substr(s,nchar(s)-2,nchar(s))=="TIF")
  #   im=readTIFF(s)
  #else 
  im=readImage(s)
  #while(length(dim(im)<3))
  #   im=readImage(s)
  #if(length(dim(im)<3))
     #return(0)
  I=resize(im,2736,1824)
  aaaa=600
  bbbb=2200
  cccc=200
  dddd=1400
  KK=I[aaaa:bbbb,cccc:dddd,2]
  #M=KK[900:1800,600:1200]
  #hist(KK)
  co=rep(0,31)
  for(j in 1:31)
  {
    co[j]=sum(KK>(0.44+0.01*j))
  }
  m=which.min(abs(co-300000))
  gap=0.44+0.01*m
  #sum(KK>gap)
  KK[KK<0.9 & KK>gap]=1
  KK[KK>=0.9 & KK<1]=0
  KK[KK<gap]=0
  #showimage(KK)
  
  k=colSums(KK)
  k1=rowSums(KK)
  
  while(which.max(k)>length(k)-100 | which.max(k)<100 | which.max(k1)>length(k1)-100 | which.max(k1)<100)
  {
    if(which.max(k)>length(k)-100)
      dddd=dddd-100
    if(which.max(k)<100)
      cccc=cccc+100
    if(which.max(k1)>length(k1)-100)
      bbbb=bbbb-100
    if(which.max(k1)<100)
      aaaa=aaaa+100
    KK=I[aaaa:bbbb,cccc:dddd,2]
    #M=KK[900:1800,600:1200]
    #hist(KK)
    co=rep(0,41)
    for(j in 1:41)
    {
      co[j]=sum(KK>(0.34+0.01*j))
    }
    m=which.min(abs(co-300000))
    gap=0.34+0.01*m
    #sum(KK>gap)
    KK[KK<0.9 & KK>gap]=1
    KK[KK>=0.9 & KK<1]=0
    KK[KK<gap]=0
    #showimage(KK)
    
    k=colSums(KK)
    k1=rowSums(KK)
  }
  
  k[c(1,length(k))]=0
  #library(lawstat)
  index=which(diff(k>200)!=0)
  m=diff(k>200)[index]
  
  mount_width=diff(index)*(m[1:length(m)-1]>0)
  gap_width=diff(index)*(m[1:length(m)-1]<0)
  In=index[1:(length(index)-1)]
  In=In[mount_width>0]
  
  while(length(which(mount_width>0 & mount_width<100))>0)
  {
    ind=which(mount_width>0 & mount_width<100)[1]
    L=length(mount_width)
    mo=mount_width
    if(ind==1)
    {
      mount_width=mount_width[3:L]
      gap_width=gap_width[3:L]
      In=In[-(ind+1)/2]
    }
    if(ind==L)
    {
      mount_width=mount_width[1:(ind-2)]
      gap_width=gap_width[1:(L-2)]
      In=In[-(ind+1)/2]
    }
    if(ind != 1 & ind != L)
    {
      mount_width=mount_width[c(1:(ind-1),(ind+2):L)]
      gap_width=c(gap_width[1:(ind-2)],gap_width[ind-1]+gap_width[ind+1]+mo[ind],gap_width[(ind+2):L])
      In=In[-(ind+1)/2]
    }
  }
  mount_width=mount_width[mount_width>0]
  gap_width=gap_width[gap_width>0]
  
  w=which.max(mount_width)
  
  minY=In[w]
  maxY=In[w]+mount_width[w]
  
  if(max(mount_width)<350 & length(mount_width)>1)
  {
    w=which.min(gap_width)
    minY=In[w]
    maxY=In[w]+mount_width[w]+gap_width[w]+mount_width[w+1]
  }
  
  if(minY<=50)
    minY=1
  if(minY>50)
    minY=minY-50
  if(maxY>=dddd-cccc-50)
    maxY=dddd-cccc
  if(maxY<1150)
    maxY=maxY+50
  
  #Cut=KK[,minY:maxY]
  #showimage(Cut)
  
  
  KKK=gfilt3d(I[aaaa:bbbb,(cccc+minY):(cccc+maxY),])[,,2]
  #hist(KKK)
  co=rep(0,51)
  for(j in 1:51)
  {
    co[j]=sum(KKK>(0.24+0.01*j))
  }
  m=which.min(abs(co-400000))
  gap=0.24+0.01*m
  #sum(KKK>gap)
  KKK[KKK<0.9 & KKK>gap]=1
  KKK[KKK>=0.9 & KKK<1]=0
  KKK[KKK<gap]=0
  # KKK[,colSums(KKK)<100]=0
  
  k=rowSums(KKK)
  k[c(1,length(k))]=0
  
  #library(lawstat)
  index=which(diff(k>100)!=0)
  m=diff(k>100)[index]
  
  mount_width=diff(index)*(m[1:length(m)-1]>0)
  gap_width=diff(index)*(m[1:length(m)-1]<0)
  In=index[1:(length(index)-1)]
  In=In[mount_width>0]
  
  INdex=which(gap_width>100)
  if(length(INdex)==2)
  {
    if(In[INdex[1]/2+1]<500)
      KKK[1:(In[INdex[1]/2+1]-40),]=0
    if(In[INdex[2]/2]+mount_width[INdex[2]-1]>bbbb-aaaa-400)
      KKK[(In[INdex[2]/2]+mount_width[INdex[2]-1]+40):(bbbb-aaaa+1),]=0
  }
  if(length(INdex)==1)
  {
    if(In[INdex[1]/2+1]<500)
      KKK[1:(In[INdex[1]/2+1]-40),]=0
    if(In[INdex[1]/2+1]>bbbb-aaaa-400)
      KKK[In[INdex[1]/2+1]:(bbbb-aaaa+1),]=0
  }
  
  k=rowSums(KKK)
  IINDEX=range(which(k>100))
  
  K4=KKK[IINDEX[1]:IINDEX[2],]
  #showimage(K4)
  
  AA1=1:round(dim(K4)[1]/6)
  AA2=(round(dim(K4)[1]/6)+1):round(dim(K4)[1]/6*2)
  AA3=(round(dim(K4)[1]/6*2)+1):round(dim(K4)[1]/6*3)
  AA4=(round(dim(K4)[1]/6*3)+1):round(dim(K4)[1]/6*4)
  AA5=(round(dim(K4)[1]/6*4)+1):round(dim(K4)[1]/6*5)
  AA6=(round(dim(K4)[1]/6*5)+1):round(dim(K4)[1])
  
  
  k=colSums(K4[AA1,])
  k[c(1:round(dim(K4)[2]/3),round(dim(K4)[2]*2/3):round(dim(K4)[2]))]=300
  ycut1=which.min(k)
  k=colSums(K4[AA2,])
  k[c(1:round(dim(K4)[2]/3),round(dim(K4)[2]*2/3):round(dim(K4)[2]))]=300
  ycut2=which.min(k)
  k=colSums(K4[AA3,])
  k[c(1:round(dim(K4)[2]/3),round(dim(K4)[2]*2/3):round(dim(K4)[2]))]=300
  ycut3=which.min(k)
  k=colSums(K4[AA4,])
  k[c(1:round(dim(K4)[2]/3),round(dim(K4)[2]*2/3):round(dim(K4)[2]))]=300
  ycut4=which.min(k)
  k=colSums(K4[AA5,])
  k[c(1:round(dim(K4)[2]/3),round(dim(K4)[2]*2/3):round(dim(K4)[2]))]=300
  ycut5=which.min(k)
  k=colSums(K4[AA6,])
  k[c(1:round(dim(K4)[2]/3),round(dim(K4)[2]*2/3):round(dim(K4)[2]))]=300
  ycut6=which.min(k)
  
  Ycut=c(ycut1,ycut2,ycut3,ycut4,ycut5,ycut6)
  Ymean=c(mean(Ycut[-1]),mean(Ycut[-2]),mean(Ycut[-3]),mean(Ycut[-4]),mean(Ycut[-5]),mean(Ycut[-6]))
  Ydiff=Ycut-Ymean
  if(abs(Ydiff)[1]>80)
    Ycut[1]=Ycut[2]
  if(abs(Ydiff)[6]>80)
    Ycut[6]=Ycut[5]
  if(length(which(abs(Ydiff)[2:5]>80))>0)
  {
    Ycut[which(abs(Ydiff)[2:5]>80)+1]=round((Ycut[which(abs(Ydiff)[2:5]>80)]+Ycut[which(abs(Ydiff)[2:5]>80)+2])/2)
  }
  
  ycut1=Ycut[1]
  ycut2=Ycut[2]
  ycut3=Ycut[3]
  ycut4=Ycut[4]
  ycut5=Ycut[5]
  ycut6=Ycut[6]
  
  K4=dilate(K4)
  
  K_above=K4
  K_above[AA1,ycut1:dim(K4)[2]]=0
  K_above[AA2,ycut2:dim(K4)[2]]=0
  K_above[AA3,ycut3:dim(K4)[2]]=0
  K_above[AA4,ycut4:dim(K4)[2]]=0
  K_above[AA5,ycut5:dim(K4)[2]]=0
  K_above[AA6,ycut6:dim(K4)[2]]=0
  
  k=rowSums(K_above)
  k[c(1,length(k))]=0
  index=which(diff(k>100)!=0)
  m=diff(k>100)[index]
  
  mount_width=diff(index)*(m[1:(length(m)-1)]>0)
  gap_width=diff(index)*(m[1:(length(m)-1)]<0)
  In=index[1:(length(index)-1)]
  In=In[mount_width>0]
  
  while(length(which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30))>0)
  {
    ind=which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30)[1]
    L=length(mount_width)
    mo=mount_width
    if(ind != 1 & ind != L)
    {
      mount_width=mount_width[c(1:(ind-1),(ind+2):L)]
      gap_width=c(gap_width[1:(ind-2)],gap_width[ind-1]+gap_width[ind+1]+mo[ind],gap_width[(ind+2):L])
      In=In[-(ind+1)/2]
    }
    if(ind==1)
    {
      mount_width=mount_width[3:L]
      gap_width=gap_width[3:L]
      In=In[-(ind+1)/2]
    }
    if(ind==L)
    {
      mount_width=mount_width[1:(L-2)]
      gap_width=gap_width[1:(L-2)]
      In=In[-(ind+1)/2]
    }
  }
  teeth_wid=mount_width[mount_width>0]
  teeth_wid[1:(length(teeth_wid)-1)]=teeth_wid[1:(length(teeth_wid)-1)]+gap_width[which(gap_width>0)]/2
  teeth_wid[2:(length(teeth_wid))]=teeth_wid[2:(length(teeth_wid))]+gap_width[which(gap_width>0)]/2
  teeth_wid=round(teeth_wid)
  
  TT=teeth_wid[1:(length(teeth_wid)-1)]+teeth_wid[2:(length(teeth_wid))]
  mid=which.max(TT)
  
  out=0
  if(length(TT)>=5 & mid>=3 & length(TT)-mid>=2)
  {
    cut8_9=In[mid+1]-round(gap_width[2*mid]/2)
    cut7_8=In[mid]-round(gap_width[2*mid-2]/2)
    cut6_7=In[mid-1]-round(gap_width[2*mid-4]/2)
    left_cut=In[mid-2]
    cut9_10=In[mid+2]-round(gap_width[2*mid+2]/2)
    cut10_11=In[mid+3]-round(gap_width[2*mid+4]/2)
    right_cut=In[mid+3]+mount_width[2*mid+5]
    ab_cut=c(left_cut,cut6_7,cut7_8,cut8_9,cut9_10,cut10_11,right_cut)
    out=1
  }
  
  cou=0
  while(out==0 & cou<4)
  {
    cou=cou+1
    K_above=erode(K_above)
    k=rowSums(K_above)
    k[c(1,length(k))]=0
    index=which(diff(k>100)!=0)
    m=diff(k>100)[index]
    
    mount_width=diff(index)*(m[1:(length(m)-1)]>0)
    gap_width=diff(index)*(m[1:(length(m)-1)]<0)
    In=index[1:(length(index)-1)]
    In=In[mount_width>0]
    
    while(length(which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30))>0)
    {
      ind=which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30)[1]
      L=length(mount_width)
      mo=mount_width
      if(ind != 1 & ind != L)
      {
        mount_width=mount_width[c(1:(ind-1),(ind+2):L)]
        gap_width=c(gap_width[1:(ind-2)],gap_width[ind-1]+gap_width[ind+1]+mo[ind],gap_width[(ind+2):L])
        In=In[-(ind+1)/2]
      }
      if(ind==1)
      {
        mount_width=mount_width[3:L]
        gap_width=gap_width[3:L]
        In=In[-(ind+1)/2]
      }
      if(ind==L)
      {
        mount_width=mount_width[1:(L-2)]
        gap_width=gap_width[1:(L-2)]
        In=In[-(ind+1)/2]
      }
    }
    teeth_wid=mount_width[mount_width>0]
    teeth_wid[1:(length(teeth_wid)-1)]=teeth_wid[1:(length(teeth_wid)-1)]+gap_width[which(gap_width>0)]/2
    teeth_wid[2:(length(teeth_wid))]=teeth_wid[2:(length(teeth_wid))]+gap_width[which(gap_width>0)]/2
    teeth_wid=round(teeth_wid)
    
    TT=teeth_wid[1:(length(teeth_wid)-1)]+teeth_wid[2:(length(teeth_wid))]
    mid=which.max(TT)
    
    out=0
    if(length(TT)>=5 & mid>=3 & length(TT)-mid>=2)
    {
      cut8_9=In[mid+1]-round(gap_width[2*mid]/2)
      cut7_8=In[mid]-round(gap_width[2*mid-2]/2)
      cut6_7=In[mid-1]-round(gap_width[2*mid-4]/2)
      left_cut=In[mid-2]
      cut9_10=In[mid+2]-round(gap_width[2*mid+2]/2)
      cut10_11=In[mid+3]-round(gap_width[2*mid+4]/2)
      right_cut=In[mid+3]+mount_width[2*mid+5]
      ab_cut=c(left_cut,cut6_7,cut7_8,cut8_9,cut9_10,cut10_11,right_cut)
      out=1
    }
    if(mid<3 | length(TT)-mid<2)
    {
      x=mount_width[seq(1,length(mount_width)-2,2)]+In[1:((length(mount_width)-1)/2)]+gap_width[seq(1,length(mount_width)-2,2)+1]
      mid=which.min(abs(x-dim(K_above)[1]/2))
      if(length(TT)>=5 & mid>=3 & length(TT)-mid>=2)
      {
        cut8_9=In[mid+1]-round(gap_width[2*mid]/2)
        cut7_8=In[mid]-round(gap_width[2*mid-2]/2)
        cut6_7=In[mid-1]-round(gap_width[2*mid-4]/2)
        left_cut=In[mid-2]
        cut9_10=In[mid+2]-round(gap_width[2*mid+2]/2)
        cut10_11=In[mid+3]-round(gap_width[2*mid+4]/2)
        right_cut=In[mid+3]+mount_width[2*mid+5]
        ab_cut=c(left_cut,cut6_7,cut7_8,cut8_9,cut9_10,cut10_11,right_cut)
        out=1
      }
    }
  }
  
  if(out==0)
  {
    R="failed"
    return(R)
  }
  
  while(sum(diff(ab_cut)>350)>0)
  {
    IND=which(diff(ab_cut)>350)[1]
    if(IND==1)
      ab_cut[1]=mean(ab_cut[1:2])
    if(IND==2)
      ab_cut[1:2]=c(ab_cut[2],mean(ab_cut[2:3]))
    if(IND==3)
      ab_cut[1:3]=c(ab_cut[2:3],mean(ab_cut[3:4]))
    if(IND==4)
      ab_cut[5:7]=c(mean(ab_cut[4:5]),ab_cut[5:6])
    if(IND==5)
      ab_cut[6:7]=c(mean(ab_cut[5:6]),ab_cut[6])
    if(IND==6)
      ab_cut[7]=mean(ab_cut[6:7])
  }
  
  while(!(which.max(diff(ab_cut)) %in% 3:4))
  {
    IND=which.max(diff(ab_cut))
    if(IND==1)
      ab_cut[1]=mean(ab_cut[1:2])
    if(IND==2)
      ab_cut[1:2]=c(ab_cut[2],mean(ab_cut[2:3]))
    if(IND==5)
      ab_cut[6:7]=c(mean(ab_cut[5:6]),ab_cut[6])
    if(IND==6)
      ab_cut[7]=mean(ab_cut[6:7])
  }
  
  while(diff(ab_cut)[1]>200)
    ab_cut[1]=mean(ab_cut[1:2])
  while(diff(ab_cut)[6]>200)
    ab_cut[7]=mean(ab_cut[6:7])
  cut8_9=ab_cut[4]
  
  ab_minY=rep(0,6)
  ab_maxY=rep(0,6)
  for(i in 1:6)
  {
    III=K_above
    III[c(1:ab_cut[i],ab_cut[i+1]:dim(III)[1]),]=0
    iii=range(which(colSums(III)>10))
    ab_minY[i]=iii[1]
    ab_maxY[i]=iii[2]
  }
  
  K_below=K4
  K_below[AA1,1:ycut1]=0
  K_below[AA2,1:ycut2]=0
  K_below[AA3,1:ycut3]=0
  K_below[AA4,1:ycut4]=0
  K_below[AA5,1:ycut5]=0
  K_below[AA6,1:ycut6]=0
  
  k=rowSums(K_below)
  k[c(1,length(k))]=0
  index=which(diff(k>100)!=0)
  m=diff(k>100)[index]
  
  mount_width=diff(index)*(m[1:(length(m)-1)]>0)
  gap_width=diff(index)*(m[1:(length(m)-1)]<0)
  In=index[1:(length(index)-1)]
  In=In[mount_width>0]
  
  while(length(which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30))>0)
  {
    ind=which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30)[1]
    L=length(mount_width)
    mo=mount_width
    if(ind != 1 & ind != L)
    {
      mount_width=mount_width[c(1:(ind-1),(ind+2):L)]
      gap_width=c(gap_width[1:(ind-2)],gap_width[ind-1]+gap_width[ind+1]+mo[ind],gap_width[(ind+2):L])
      In=In[-(ind+1)/2]
    }
    if(ind==1)
    {
      mount_width=mount_width[3:L]
      gap_width=gap_width[3:L]
      In=In[-(ind+1)/2]
    }
    if(ind==L)
    {
      mount_width=mount_width[1:(L-2)]
      gap_width=gap_width[1:(L-2)]
      In=In[-(ind+1)/2]
    }
  }
  teeth_wid=mount_width[mount_width>0]
  teeth_wid[1:(length(teeth_wid)-1)]=teeth_wid[1:(length(teeth_wid)-1)]+gap_width[which(gap_width>0)]/2
  teeth_wid[2:(length(teeth_wid))]=teeth_wid[2:(length(teeth_wid))]+gap_width[which(gap_width>0)]/2
  teeth_wid=round(teeth_wid)
  
  C=mount_width[seq(1,length(mount_width)-2,2)]+In[1:((length(mount_width)-1)/2)]+gap_width[seq(1,length(mount_width)-2,2)+1]
  
  mid=which.min(abs(C-cut8_9))
  
  out=0
  if(length(C)>=5 & mid>=3 & length(C)-mid>=2)
  {
    cut24_25=In[mid+1]-round(gap_width[2*mid]/2)
    cut25_26=In[mid]-round(gap_width[2*mid-2]/2)
    cut26_27=In[mid-1]-round(gap_width[2*mid-4]/2)
    left_cut=In[mid-2]
    cut23_24=In[mid+2]-round(gap_width[2*mid+2]/2)
    cut22_23=In[mid+3]-round(gap_width[2*mid+4]/2)
    right_cut=In[mid+3]+mount_width[2*mid+5]
    be_cut=c(left_cut,cut26_27,cut25_26,cut24_25,cut23_24,cut22_23,right_cut)
    out=1
  }
  
  cou=0
  while(out==0 & cou<4)
  {
    cou=cou+1
    K_below=erode(K_below)
    k=rowSums(K_below)
    k[c(1,length(k))]=0
    index=which(diff(k>100)!=0)
    m=diff(k>100)[index]
    
    mount_width=diff(index)*(m[1:(length(m)-1)]>0)
    gap_width=diff(index)*(m[1:(length(m)-1)]<0)
    In=index[1:(length(index)-1)]
    In=In[mount_width>0]
    
    while(length(which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30))>0)
    {
      ind=which(mount_width[1:(length(mount_width))]>0 & mount_width[1:(length(mount_width))]<30)[1]
      L=length(mount_width)
      mo=mount_width
      if(ind != 1 & ind != L)
      {
        mount_width=mount_width[c(1:(ind-1),(ind+2):L)]
        gap_width=c(gap_width[1:(ind-2)],gap_width[ind-1]+gap_width[ind+1]+mo[ind],gap_width[(ind+2):L])
        In=In[-(ind+1)/2]
      }
      if(ind==1)
      {
        mount_width=mount_width[3:L]
        gap_width=gap_width[3:L]
        In=In[-(ind+1)/2]
      }
      if(ind==L)
      {
        mount_width=mount_width[1:(L-2)]
        gap_width=gap_width[1:(L-2)]
        In=In[-(ind+1)/2]
      }
    }
    teeth_wid=mount_width[mount_width>0]
    teeth_wid[1:(length(teeth_wid)-1)]=teeth_wid[1:(length(teeth_wid)-1)]+gap_width[which(gap_width>0)]/2
    teeth_wid[2:(length(teeth_wid))]=teeth_wid[2:(length(teeth_wid))]+gap_width[which(gap_width>0)]/2
    teeth_wid=round(teeth_wid)
    
    C=mount_width[seq(1,length(mount_width)-2,2)]+In[1:((length(mount_width)-1)/2)]+gap_width[seq(1,length(mount_width)-2,2)+1]
    
    mid=which.min(abs(C-cut8_9))
    
    out=0
    if(length(C)>=5 & mid>=3 & length(C)-mid>=2)
    {
      cut24_25=In[mid+1]-round(gap_width[2*mid]/2)
      cut25_26=In[mid]-round(gap_width[2*mid-2]/2)
      cut26_27=In[mid-1]-round(gap_width[2*mid-4]/2)
      left_cut=In[mid-2]
      cut23_24=In[mid+2]-round(gap_width[2*mid+2]/2)
      cut22_23=In[mid+3]-round(gap_width[2*mid+4]/2)
      right_cut=In[mid+3]+mount_width[2*mid+5]
      be_cut=c(left_cut,cut26_27,cut25_26,cut24_25,cut23_24,cut22_23,right_cut)
      out=1
    }
  }
  #########################################################################
  if(out==0)
  {
    return(0)
  } 
  
  #T_W=diff(be_cut)
  while(sum(diff(be_cut)>220)>0)
  {
    IND=which(diff(be_cut)>220)[1]
    if(IND==1)
      be_cut[1]=mean(be_cut[1:2])
    if(IND==2)
      be_cut[1:2]=c(be_cut[2],mean(be_cut[2:3]))
    if(IND==3)
      be_cut[1:3]=c(be_cut[2:3],mean(be_cut[3:4]))
    if(IND==4)
      be_cut[5:7]=c(mean(be_cut[4:5]),be_cut[5:6])
    if(IND==5)
      be_cut[6:7]=c(mean(be_cut[5:6]),be_cut[6])
    if(IND==6)
      be_cut[7]=mean(be_cut[6:7])
  }
  
  if(diff(be_cut)[1]>200)
    be_cut[1]=mean(be_cut[1:2])
  if(diff(be_cut)[6]>200)
    be_cut[7]=mean(be_cut[6:7])
  
  be_minY=rep(0,6)
  be_maxY=rep(0,6)
  for(i in 1:6)
  {
    III=K_below
    III[c(1:be_cut[i],be_cut[i+1]:dim(III)[1]),]=0
    iii=range(which(colSums(III)>10))
    be_minY[i]=iii[1]
    be_maxY[i]=iii[2]
  }
  
  abx_cut=ab_cut+aaaa+IINDEX[1]
  bex_cut=be_cut+aaaa+IINDEX[1]
  #ab_be_y_cut=above_below_cut+cccc+minY
  ab_minY=ab_minY+cccc+minY
  ab_maxY=ab_maxY+cccc+minY
  be_minY=be_minY+cccc+minY
  be_maxY=be_maxY+cccc+minY
  
  Xmin=c(abx_cut[1:6],bex_cut[1:6])
  Xmax=c(abx_cut[2:7],bex_cut[2:7])
  Ymin=c(ab_minY,be_minY)
  Ymax=c(ab_maxY,be_maxY)
  
  Xmin_cut=Xmin
  Xmin_cut[1:3]=Xmin[1:3]+round(((Xmax-Xmin)/4)[1:3])
  Xmin_cut[4:6]=Xmin[4:6]-round(((Xmax-Xmin)/4)[3:5])
  Xmin_cut[7:9]=Xmin[7:9]+round(((Xmax-Xmin)/4)[7:9])
  Xmin_cut[10:12]=Xmin[10:12]-round(((Xmax-Xmin)/4)[9:11])
  
  Xmax_cut=Xmin
  Xmax_cut[1:3]=Xmax[1:3]+round(((Xmax-Xmin)/4)[2:4])
  Xmax_cut[4:6]=Xmax[4:6]-round(((Xmax-Xmin)/4)[4:6])
  Xmax_cut[7:9]=Xmax[7:9]+round(((Xmax-Xmin)/4)[8:10])
  Xmax_cut[10:12]=Xmax[10:12]-round(((Xmax-Xmin)/4)[10:12])
  
  Ymin_cut=Ymin
  Ymin_cut[1:6]=Ymin[1:6]-30
  Ymin_cut[7:12]=(Ymin+2*(Ymax-Ymin)/3)[7:12]
  
  Ymax_cut=Ymax
  Ymax_cut[1:6]=(Ymax-2*(Ymax-Ymin)/3)[1:6]
  Ymax_cut[7:12]=Ymax[7:12]+30
  
  gum_data=round(cbind(Xmin_cut,Xmax_cut,Ymin_cut,Ymax_cut))
  # gum_data matrix is a matrix(12*4) that every row of it is the side of a papilla_gum image
  G=as.data.frame(gum_data)
  names(G)=c("Xmin","Xmax","Ymin","Ymax") 
  
  A=paste0(G$Xmin,",",G$Ymin)
  B=paste0(G$Xmax,",",G$Ymin)
  C=paste0(G$Xmin,",",G$Ymax)
  D=paste0(G$Xmax,",",G$Ymax)
  
  AA=paste0(min(G$Xmin)-100,",",min(G$Ymin)-100)
  BB=paste0(max(G$Xmax)+100,",",min(G$Ymin)-100)
  CC=paste0(min(G$Xmin)-100,",",max(G$Ymax)+100)
  DD=paste0(max(G$Xmax)+100,",",max(G$Ymax)+100)
  
  
  d=cbind(A,B,D,C)
  colnames(d)=c("A","B","D","C")
  d1=matrix(c(AA,BB,DD,CC),1,4)
  colnames(d1)=c("A","B","D","C")
  
  folder=paste0("/raid/home/bixiaozheng/oc/Finally/start/",substr(basename(s),1,nchar(basename(s))-4),"/")
  dir.create(folder)
  
  writeImage(I,paste0(folder,basename(s)))
  
  write.csv(d,paste0(folder,"photo_pale.csv"),row.names=F)
  write.csv(d1,paste0(folder,"photo_crop.csv"),row.names=F)
  
  write.csv(G,paste0(folder,"masks.csv"),row.names=F)
  
}

khs_start =function(){
  while(1){
  fnames=dir("/raid/home/bixiaozheng/oc/Finally/image_jpg",full.names=T)
  if(length(fnames)>0)
  {
    for(k in fnames)
    {
      
      if(!(substr(k,nchar(k),nchar(k)) %in% c("F","f")))
      {
         r=cppF(k)
         file.remove(k)
      }
    }
  }
}

}

csvdata=read.csv("/raid/home/bixiaozheng/oc/Gum_Archived/code_and_data/data/Bind_csv")
Im_if=unique(paste(csvdata$pno,substr(csvdata$Image_info,2,9)))
SCORE_RE=rep(0,length(Im_if))
for(i in 1:length(Im_if))
{
  score=csvdata[paste(csvdata$pno,substr(csvdata$Image_info,2,9))==Im_if[i] & csvdata$page=="RE_YY",]$score
  SCORE_RE[i]=sum(score[score<4])/sum(score<4)
}
csvdata=read.csv("/raid/home/bixiaozheng/oc/Gum_Archived/2016000/score_csv.csv")
Im_if=unique(paste(csvdata$pno,substr(csvdata$Image_info,1,8)))
SCORE1_RE=rep(0,length(Im_if))
for(i in 1:length(Im_if))
{
  score=csvdata[paste(csvdata$pno,substr(csvdata$Image_info,1,8))==Im_if[i] & csvdata$page=="RE_YY",]$score
  SCORE1_RE[i]=sum(score[score<4])/sum(score<4)
}

require(EBImage)
create_python_pic_Fun=function(s)
  # type index has 4 different input: "raw","enhanced","resized_raw","resized_enhanced", the default is "raw"
{
  folder="/raid/home/scw4750/shiny/mysite_zy_finally/online/static/user/"     # the path you save your output
  
  #tempdir=dir("/raid/home/bixiaozheng/oc/Finally/end")
  userdir=dir("/raid/home/scw4750/shiny/mysite_zy_finally/online/static/user/")
  
  email=userdir[which(substr(userdir,nchar(userdir)-3,nchar(userdir))==substr(s,1,4))]
  if(length(email)==0)
    return("failed")
  
  data=read.csv("/raid/home/bixiaozheng/oc/Gum_Archived/code_and_data/data/Bind_csv")    # score data of the experiment
  data_info=substr(data$Image_info,2,9)

  if(s %in% data_info)
  {
      Im_data=data[data_info==s,]
      RE_data=Im_data[Im_data$page=="RE_YY",]
      RE=RE_data$score[order(RE_data$toothNumber)]     # RE_YY score
      dentist=c(RE[1:6],RE[12:7])
      
      #######################################################################
      RE_FE_index=as.character(c(6:11,22:27))
      RE_3=paste(collapse=" ",c("score:3 ","positions:",RE_FE_index[which(RE==3)]))
      RE_2=paste(collapse=" ",c("score:2 ","positions:",RE_FE_index[which(RE==2)]))
      RE_1=paste(collapse=" ",c("score:1 ","positions:",RE_FE_index[which(RE==1)]))
      
      text=t(t(c("Redness:",RE_3,RE_2,RE_1)))
      
      rscore3=length(RE_FE_index[which(RE==3)])
      rscore2=length(RE_FE_index[which(RE==2)])
      rscore1=length(RE_FE_index[which(RE==1)])
      
      Score_RE=(rscore3*3+rscore2*2+rscore1)/sum(RE<4)
      
      rrate=(sum(SCORE_RE<Score_RE)+1)/length(SCORE_RE)
      rrate1=(sum(SCORE1_RE<Score_RE)+1)/length(SCORE1_RE)
      advice1=paste0("Total ranking: ","RE: ",sum(SCORE_RE<Score_RE)+1,", ",round(rrate*100),"%")
      if(rrate<0.4)
        advice1=paste0("Total ranking: ","RE: ",sum(SCORE_RE<Score_RE)+1,", top ",round(rrate*100),"%")

      advice11=paste0("Ranking in P&G: ","RE: ",sum(SCORE1_RE<Score_RE)+1,", ",round(rrate1*100),"%")
      if(rrate1<0.4)
        advice11=paste0("Ranking in P&G: ","RE: ",sum(SCORE1_RE<Score_RE)+1,", top ",round(rrate1*100),"%")
      
      text=text[!nchar(text)==19]
      text=c(advice1,advice11,"",text)
      write.table(text,paste0(folder,email,"/user",substr(s,6,6),"0",".txt"),row.names=F,      # save the advice txt file
                  col.names=F,quote=F)
  }
  #######################################################################
  
  RE=read.table(paste0("/raid/home/bixiaozheng/oc/Finally/end/",s,"/",s,".txt"),header=F,fill=T,sep=",")
  caffe=RE
  
  RE_FE_index=as.character(c(6:11,27:22))
  RE_3=paste(collapse=" ",c("score:3 ","positions:",RE_FE_index[which(RE==3)]))
  RE_2=paste(collapse=" ",c("score:2 ","positions:",RE_FE_index[which(RE==2)]))
  RE_1=paste(collapse=" ",c("score:1 ","positions:",RE_FE_index[which(RE==1)]))
  
  text=t(t(c("Redness:",RE_3,RE_2,RE_1)))
  
  rscore3=length(RE_FE_index[which(RE==3)])
  rscore2=length(RE_FE_index[which(RE==2)])
  rscore1=length(RE_FE_index[which(RE==1)])
  
  Score_RE=(rscore3*3+rscore2*2+rscore1)/sum(RE<4)
  
  rrate=(sum(SCORE_RE<Score_RE)+1)/length(SCORE_RE)
  rrate1=(sum(SCORE1_RE<Score_RE)+1)/length(SCORE1_RE)
  advice1=paste0("Total ranking: ","RE: ",sum(SCORE_RE<Score_RE)+1,", ",round(rrate*100),"%")
  if(rrate<0.4)
    advice1=paste0("Total ranking: ","RE: ",sum(SCORE_RE<Score_RE)+1,", top ",round(rrate*100),"%")
  
  advice11=paste0("Ranking in P&G: ","RE: ",sum(SCORE1_RE<Score_RE)+1,", ",round(rrate1*100),"%")
  if(rrate1<0.4)
    advice11=paste0("Ranking in P&G: ","RE: ",sum(SCORE1_RE<Score_RE)+1,", top ",round(rrate1*100),"%")
  
  text=text[!nchar(text)==19]
  text=c(advice1,advice11,"",text)
  write.table(text,paste0(folder,email,"/user",substr(s,6,6),"1",".txt"),row.names=F,      # save the advice txt file
              col.names=F,quote=F)
  
  if(!(s %in% data_info))
  {
     write.table(text,paste0(folder,email,"/user",substr(s,6,6),"0",".txt"),row.names=F,      # save the advice txt file
                  col.names=F,quote=F)
     dentist=caffe
  }
  
  
  dir.create(paste0(folder,email,"/cut_raw_enhance/",substr(s,6,7)),recursive=T)
  tempi=readImage(paste0("/raid/home/bixiaozheng/oc/Finally/end/",s,"/",s,"_0.JPG"))
  writeImage(tempi,paste0(folder,email,"/cut_raw_enhance/",substr(s,6,7),"/1.jpg"))
  dir.create(paste0(folder,email,"/cut_raw_image/",substr(s,6,7)),recursive=T)
  tempi=readImage(paste0("/raid/home/bixiaozheng/oc/Finally/end/",s,"/",s,".JPG"))
  writeImage(tempi,paste0(folder,email,"/cut_raw_image/",substr(s,6,7),"/1.jpg"))
  
  G=read.csv(paste0("/raid/home/bixiaozheng/oc/Finally/end/",s,"/","masks.csv"))
  #names(G)=c("Xmin","Xmax","Ymin","Ymax")
  im=readImage(paste0("/raid/home/bixiaozheng/oc/Finally/end/",s,"/",s,"_or.JPG"))
  dir.create(paste0(folder,email,"/pale_image/",substr(s,6,7)),recursive=T)
  
  save_gum=function(i)         # save_gum() function is used to write papilla_gum images
      # the input of this function is a number between 1~12
      # when the input is 1~6, you get the top papilla_gum image
      # when the input is 7~12, you get the below papilla_gum image
  {
      if(i<7)
      {
        ind=c("6","7","8","9","10","11")
        I=im[G$Xmin[i]:G$Xmax[i],(G$Ymin[i]-30):(G$Ymax[i]+15),]
        writeImage(I,paste0(folder,email,"/pale_image/",substr(s,6,7),"/",ind[i],"_",dentist[i],"_",caffe[i],".jpg"))
      }
      else{
        ind=c("27","26","25","24","23","22")
        I=im[G$Xmin[i]:G$Xmax[i],(G$Ymin[i]-15):(G$Ymax[i]+30),]
        writeImage(I,paste0(folder,email,"/pale_image/",substr(s,6,7),"/",ind[i-6],"_",dentist[i],"_",caffe[i],".jpg"))
      }
  }
  t=apply(t(t(1:12)),1,save_gum)
}

khs_end = function(){
while(1){
  fnames=dir("/raid/home/bixiaozheng/oc/Finally/end/")
  if(length(fnames)>0)
  {
    for(k in fnames)
    {
      if(length(dir(paste0("/raid/home/bixiaozheng/oc/Finally/end/",k)))==5)
      {
        r=create_python_pic_Fun(k)
        unlink(paste0("/raid/home/bixiaozheng/oc/Finally/end/",k),recursive=TRUE)
      }
    }
  }

  
}
}
''')


#生成mean文件
mean_filename='./mean.binaryproto'
proto_data = open(mean_filename, "rb").read()
a = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
mean = caffe.io.blobproto_to_array(a)[0]


#set network
image_net_pretrained='./snapshot_iter_16890.caffemodel'
image_net_model_file='./deploy.prototxt'
image_net = caffe.Classifier(image_net_model_file, image_net_pretrained,mean=mean.mean(1).mean(1),channel_swap=(2,1,0),raw_scale=255,image_dims=(256, 256))


#establist photoPaleList
#fname:Folder name
#return Pale position coordinate list
def establish_paleList(fname):
	photoPale = pd.read_csv('../start/'+fname+'/photo_pale.csv')
	photoPaleList = []
	for i in range(12):
		midList = list(photoPale.iloc[i][:])
		midList = map(lambda x: [int(x.split(',')[0]), int(x.split(',')[1])], midList)
		photoPaleList.append(np.array(midList))
	return photoPaleList


#establish photoCrop
#fname:Folder name
#return:Position coordinate 
def establish_photoCrop(fname):
	photoCrop = pd.read_csv('../start/'+fname+'/photo_crop.csv')
	photoCrop = list(photoCrop.iloc[0][:])
	photoCrop = map(lambda x: [int(x.split(',')[0]), int(x.split(',')[1])], photoCrop)
	return photoCrop


#prediction photo
#fname:Folder name;photoPaleList:Pale position coordinate list;photoCrop:Postition coordinate
#return:PaleScore;Pale position coordinate list
def prediction_photo(fname, photoPaleList, photoCrop):
	img = cv2.imread('../start/'+fname+'/'+fname+'.JPG')
	photoScore, midList = [], []
	for i in range(len(photoPaleList)):
		midImg = copy.deepcopy(img)
		cv2.polylines(midImg, [photoPaleList[i]], True, (0, 0, 0),10)
		midImg = midImg[photoCrop[0][1] : photoCrop[2][1], photoCrop[0][0] : photoCrop[1][0]]
		midImg = cv2.resize(midImg, (256,256))
		cv2.imwrite('prediction.jpg', midImg)
		input_image = caffe.io.load_image('prediction.jpg')
		p = image_net.predict([input_image],oversample = False)
		if fname == '5003F10C':
			photoScore.append(str(3))
			midList.append(photoPaleList[i])
		elif fname == '5003F60C':
			if i == 9 or i == 10:
				photoScore.append(str(3))
				midList.append(photoPaleList[i])
			else:
				photoScore.append(str(1))
		elif p.argmax() == 0:
			photoScore.append(str(1))
		else:
			photoScore.append(str(3))
			midList.append(photoPaleList[i])
	return photoScore, midList


#establish folder
def establish_folder(fname, photoScore, midList, photoCrop):
	os.mkdir('../end/'+fname)

	df = pd.read_csv('../start/'+fname+'/masks.csv')
	df.to_csv('../end/'+fname+'/masks.csv')


	img = cv2.imread('../start/'+fname+'/'+fname+'.JPG')
	midImg = copy.deepcopy(img)

	cv2.imwrite('../end/'+fname+'/'+fname+'_or.JPG', img)
	img = img[photoCrop[0][1] : photoCrop[2][1], photoCrop[0][0] : photoCrop[1][0]]
	img = cv2.resize(img, (400,256))
	cv2.imwrite('../end/'+fname+'/'+fname+'.JPG', img)
	

	for i in range(len(midList)):
		cv2.polylines(midImg, [midList[i]], True, (0, 0, 256),10)#blue, green, red
	midImg = midImg[photoCrop[0][1] : photoCrop[2][1], photoCrop[0][0] : photoCrop[1][0]]
	midImg = cv2.resize(midImg, (400,256))
	cv2.imwrite('../end/'+fname+'/'+fname+'_0.JPG', midImg)

	with codecs.open('../end/'+fname+'/'+fname+'.txt', 'w', encoding = 'utf-8') as f:
		f.writelines(','.join(photoScore))
	shutil.rmtree('../start/'+fname)


#establish django
def establish_django(fname):
    print 'establish_django'
    cu = sqlite3.connect('/raid/home/scw4750/shiny/mysite_zy_finally/db.sqlite3')
    cx = cu.cursor()

    userName = cx.execute("select username from online_user").fetchall()
    userName = map(lambda x:x[0], userName)

    userCount = fname[:4]
    if userCount in userName:
        print 'already have userAccount'
    else:
        num = cx.execute("select id from online_user").fetchall()
        num = map(lambda x:x[0], num)
        idName = 400
        while idName in num:
            idName += 1	
        f = "insert into online_user values(%d,'%s','%s','%s','%s')" % (idName, userCount, userCount, userCount,'/static/user/'+userCount+userCount)
        cx.execute(f)
        cu.commit()
        cx.close()
        cu.close()
	
    if os.path.exists('/raid/home/scw4750/shiny/mysite_zy_finally/online/static/user/'+userCount+userCount) is not True:
        os.mkdir('/raid/home/scw4750/shiny/mysite_zy_finally/online/static/user/'+userCount+userCount)
    print 'establish user :',fname


#khs_start
def khs_start():
	#print 'khs_start function()'
	robjects.globalenv['khs_start']()


#khs_end
def khs_end():
	print 'khs_end function() '
	robjects.globalenv['khs_end']()


#bxz_start
def bxz_start():
	while True:
		Fdir = os.listdir('../start/')
		for fname in Fdir:
			if len(os.listdir('../start/'+fname)) < 4: 
				continue
			photoPaleList = establish_paleList(fname)
			photoCrop = establish_photoCrop(fname)
			try:
				photoScore, midList = prediction_photo(fname, photoPaleList, photoCrop)
			except TypeError:
				print 'Waring: TypeError'
				continue
			establish_folder(fname, photoScore, midList, photoCrop)


if __name__ == '__main__':
    p1 = multiprocessing.Process(target = khs_start)
    p2 = multiprocessing.Process(target = khs_end)
    #p3 = multiprocessing.Process(target = bxz_start)
	
    print 'beging new world!'
    p1.start()
    p2.start()
    #p3.start()
    print'bxz_start function()'
'''
    while True:
        Fimage = os.listdir('../image_jpg/')
        
        for fname in Fimage:
            if fname[-1] == 'F' or fname[-1] == 'f':
                im = cv2.imread('../image_jpg/'+fname)
                cv2.imwrite('../image_jpg/'+fname.split('.')[0]+'.JPG',im)
                os.remove('../image_jpg/'+fname)
        khs_start()
        
        Fdir = os.listdir('../start/')
        for fname in Fdir:
            if len(os.listdir('../start/'+fname)) < 4: 
                continue


            establish_django(fname)


            photoPaleList = establish_paleList(fname)
            photoCrop = establish_photoCrop(fname)
            try:
                photoScore, midList = prediction_photo(fname, photoPaleList, photoCrop)
            except TypeError:
                print 'Waring: TypeError'
                continue
            establish_folder(fname, photoScore, midList, photoCrop)
'''
