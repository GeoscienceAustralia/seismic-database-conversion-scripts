#! /usr/bin/env python
# Python script for reading GG's catalogue
#

import sys, csv, string
from obspy.core import UTCDateTime
import numpy as np
import pprint
import css_types

pp = pprint.PrettyPrinter(indent=4)

InOrigin = False
InEvent = False
InArrival = False
InNetmag = False
orid=0
evid=0
mbid=0
msid=0
mlid=0
commid=0
evi=css_types.event30()
ori=css_types.origin30()
oer=css_types.origerr30()
rem=css_types.remark30()
#nmg=css_types.netmag30()
#arr=css_types.arrival30()
fp_evi=open("GGcat_big_2000.event","w")
fp_ori=open("GGcat_big_2000.origin","w")
fp_oer=open("GGcat_big_2000.origerr","w")
#fp_mag=open("GGcat_big_2000.netmag","w")
fp_rem=open("GGcat_big_2000.remark","w")

nevents = 0
etypes = {'blast':'qb','coal':'cb','local':'l','tele':'t','unsure':'uq'}
depends = {'Aftershock':'as','Foreshock':'fs','Mainshock':'ms','Swarm':'ss','None':'eq','Unsure':'eq'}
status = ['Possible','Preferred','Probable'] 
depthtypes = {'D':'f','C':'r','G':'g','N':'n','pP':'d','B':'d'}
mags = ['ML','mb','MS','Mw']
#ifile  = open('GGcat_for_GA_2010-06-08.csv', "rb")
ifile  = open('GGcat_big_2000.csv', "rb")
reader = csv.reader(ifile)

s1 = 0
s2 = 0
s3 = 0
for row in reader:
    evi=css_types.event30()
    ori=css_types.origin30()
    oer=css_types.origerr30()
    rem=css_types.remark30()
    if row[0] == 'Source': # Skip first line
        continue
    orid = orid + 1
    evid = evid + 1
    commid = commid + 1
   
#
# Do the event structure
    evi.evid = evid
    if len(row[30].strip()) > 0:
        evi.evname = '%-15s' %(row[30][:15])
    evi.prefor = orid
    evi.auth = row[0]
    evi.commid = commid
    astring=evi.create_css_string()
    fp_evi.write(astring)

#
# Do the origin structure
    ori.lat = float(row[13]) * -1.0  # GGCat doesn't have -ve lat for south
    ori.lon = float(row[12])
    if len(row[14].strip()) > 0:
        ori.depth = float(row[14])
    year = int(float(row[4]))
    mnth = int(float(row[5]))
    day  = int(float(row[6]))
    hour = int(float(row[7]))
    min  = int(float(row[8]))
    if len(row[9].strip()) > 0:
        fsec = float(row[9])
    else:
        fsec= 0.0
    sec  = int(fsec)
    micro_sec = int((fsec % 1) * 1000000)
    print(micro_sec)
    epoch = UTCDateTime(year,mnth,day,hour,min,sec, micro_sec).timestamp
    ori.time = epoch
    ori.orid = orid
    ori.evid = evid
    ori.jdate=1000*UTCDateTime(epoch).year+UTCDateTime(epoch).julday
    tmp_ndef = row[23]
    if tmp_ndef.isdigit():
        ori.ndef = int(tmp_ndef)
# Use the first couple of characters of ori.etype to store the type of event
# (e.g. coal blast, local earthquake, teleseismic, nuclear blast )
# Use last couple of characters of ori.etype to store association
# (e.g. mainshock, aftershock, foreshock) 

#flags='_______'
#flag_len = len(flags)
#array_format=list(flags)
#array_format[0:len(type)]=type
#array_format[flag_len-len(ass):flag_len]=ass
#print array_format
#back_to_string=''.join(array_format)
#print back_to_string

    stmp = '_______'
    stmp_len = len(stmp)
    array_tmp=list(stmp)
    for etype in etypes:
        if etype == row[1]:
            array_tmp[0:len(etypes[etype])]=etypes[etype] 
            #stmp =  '%-7s' %(etypes[etype])
    for depend in depends:
        if depend == row[2]:
            array_tmp[stmp_len-len(depends[depend]):stmp_len]=depends[depend]
            #sstmp = stmp[:-len(depends[depend])]+depends[depend]
    ori.etype = ''.join(array_tmp)
    for depthtype in depthtypes:
        if depthtype == row[15]:
            ori.dtype =  depthtypes[depthtype]
    type_mag = row[16] 
    for mag in mags:
        if mag[1:].upper == type_mag[1:].upper:
#            ori.mag = tmp_mag
            if mag == mags[0]:
                ori.ml = float(row[17])
                mlid =+ 1
                ori.mlid = mlid
            elif mag == mags[1]:
                ori.mb = float(row[17])
                mbid =+ 1
                ori.mbid = mbid
            elif mag == mags[2]:
                ori.ms = float(row[17])
                msid =+ 1
                ori.msid = msid
            elif mag == mags[3]:
                ori.ms = float(row[17])
                msid =+ 1
                ori.msid = msid
    
    ori.algotithm = 'GGCat'
    ori.auth = row[0]
    ori.commid = commid
    astring=ori.create_css_string()
    fp_ori.write(astring)
# Finished origin

# origerr structure
    oer.orid = orid
    stmp = row[24]
    
    if len(row[24].replace(' ','')) > 0:
        print float(row[24])
        oer.sdobs = float(row[24])
    if len(row[19].replace(' ','')) > 0:
        oer.majax = float(row[19])
    if len(row[20].replace(' ','')) > 0:
        oer.minax = float(row[20])
    if len(row[21].replace(' ','')) > 0:
        oer.strike = float(row[21])
    if len(row[22].replace(' ','')) > 0:
        oer.sdepth = float(row[22])
    if len(row[18].replace(' ','')) > 0:
        oer.stime = float(row[18])
    astring=oer.create_css_string()
    print astring
    fp_oer.write(astring)
#Finished origerr

# remark structure  
    rem.commid = commid
    rem.remark = row[31]
    astring=rem.create_css_string()
    fp_rem.write(astring)
# Finished remark
            
    
    