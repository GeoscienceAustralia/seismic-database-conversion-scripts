#! /usr/local/bin/python2.4
import sys,os,string,time

# Script defining CSS structures
#
# From Spiro Spiliopoulos to Mark Leonard November 2015
# December 2015 & January 2016 Mark Leonard added a few new table types
#

class origin30:
   def __init__(self, lat=-999.0, lon=-999.0, depth=-999.0, time=-9999999999.999, orid=1, evid=1, jdate=-1, nass=-1,
                ndef=-1, etype="-", depdp=-999.0, dtype="-", mb=-999.0, mbid=-1, ms=-999.0, msid=-1, mlid=-1,
                algorithm="-", auth="-", commid=-1, lddate="-"):
      self.lat = lat
      self.lon = lon
      self.depth = depth
      self.time = time
      self.orid = orid
      self.evid = evid
      self.jdate = jdate
      self.nass = nass
      self.ndef = ndef
      self.ndp=-1
      self.grn=-1
      self.srn=-1
      self.etype = etype
      self.depdp = depdp
      self.dtype = dtype
      self.mb = mb
      self.mbid = mbid
      self.ms = ms
      self.msid = msid
      self.ml=-999.0
      self.mlid = mlid
      self.algorithm = algorithm
      self.auth = auth
      self.commid = commid
      self.lddate = lddate
#
#  Write CSS3.0 origin structure to standard output.
   def write(self):
      print'%9.4f %9.4f %9.4f %17.5f %8d %8d %8d %4d %4d %4d %8d %8d %-7s %9.4f %-1s %7.2f %8d %7.2f %8d %7.2f %8d %-15s %-15s %8d %-17s\n' %(self.lat, self.lon, self.depth, self.time, self.orid, self.evid, self.jdate, self.nass, self.ndef, self.ndp, self.grn, self.srn, self.etype, self.depdp, self.dtype, self.mb, self.mbid, self.ms, self.msid, self.ml, self.mlid, self.algorithm, self.auth, self.commid, self.lddate)

   def create_css_string(self):
      ostring='%9.4f %9.4f %9.4f %17.5f %8d %8d %8d %4d %4d %4d %8d %8d %-7s %9.4f %-1s %7.2f %8d %7.2f %8d %7.2f %8d %-15s %-15s %8d %-17s\n' %(self.lat, self.lon, self.depth, self.time, self.orid, self.evid, self.jdate, self.nass, self.ndef, self.ndp, self.grn, self.srn, self.etype, self.depdp, self.dtype, self.mb, self.mbid, self.ms, self.msid, self.ml, self.mlid, self.algorithm, self.auth, self.commid, self.lddate)
      return ostring
#
#  Write CSS3.0 origin structure to a file.
   def write_to_file(self,prefix):
      if '.origin' in prefix:
          filename=prefix
      else:
          filename=prefix+'.origin'
      fp=open(filename,'w')
      string='%9.4f %9.4f %9.4f %17.5f %8d %8d %8d %4d %4d %4d %8d %8d %-7s %9.4f %-1s %7.2f %8d %7.2f %8d %7.2f %8d %-15s %-15s %8d %-17s\n' % (self.lat,self.lon,self.depth,self.time,self.orid,self.evid,self.jdate,self.nass,self.ndef, self.ndp, self.grn, self.srn, self.etype, self.depdp, self.dtype, self.mb, self.mbid, self.ms, self.msid, self.ml, self.mlid, self.algorithm, self.auth, self.commid, self.lddate)
      fp.write(string)
      fp.close()

#
#  Parse an IMS origin line and fill the CSS3.0 structure.
   def parse_IMS_origin(self,line):
      row=string.split(line)
      self.lat=float(row[2])
      self.lon=float(row[3])
      self.depth=float(row[4])
      if row[5] == 'f':
         fixed_depth=1
         self.dtype='f'
      else:
         fixed_depth=0
      if fixed_depth:
         self.mb=float(row[10])
         self.nass=long(row[7])
         self.ndef=long(row[6])
      else:
         self.mb=float(row[9])
         self.nass=long(row[6])
         self.ndef=long(row[5])
      stime=line[0:21]
      year=long(stime[0:4])
      month=long(stime[5:7])
      day=long(stime[8:10])
      hour=long(stime[11:13])
      min=long(stime[14:16])
      second=long(stime[17:19])
      tsecond=long(stime[20:21])*0.1
      time_tuple=(year,month,day,hour,min,second,0,0,0)
      self.time=time.mktime(time_tuple)+10.0*3600.0+tsecond
#     Orid
      self.orid=long(line[115:122])

   def rd_origin_record(self,line):
      row=string.split(line)
      self.lat=float(row[0])
      self.lon=float(row[1])
      self.depth=float(row[2])
      self.time=float(row[3])
      self.orid=long(row[4])
      self.evid=long(row[5])
      self.jdate=long(row[6])
      self.nass=long(row[7])
      self.ndef=long(row[8])
      self.ndp=long(row[9])
      self.grn=long(row[10])
      self.srn=long(row[11])
      self.etype=row[12]
      self.depdp=float(row[13])
      self.dtype=row[14]
      self.mb=float(row[15])
      self.mbid=long(row[16])
      self.ms=float(row[17])
      self.msid=long(row[18])
      self.ml=float(row[19])
      self.mlid=long(row[20])
      self.algorithm=row[21]
      self.auth=row[22]
      self.commid=long(row[23])
      self.lddate=row[24]

      if self.jdate<100000:
          year=int(float(self.jdate)/10)
          day=self.jdate-10*year
          self.jdate=1000*year+day
      elif self.jdate<1000000:
          year=int(float(self.jdate)/100)
          day=self.jdate-100*year
          self.jdate=1000*year+day

   def from_string(self, line):
      self.lat = float(line[0:9])
      self.lon = float(line[10:19])
      self.depth = float(line[20:29])
      self.time = float(line[30:47])
      self.orid = long(line[48:56])
      self.evid = long(line[57:65])
      self.jdate = long(line[66:74])
      self.nass = long(line[75:79])
      self.ndef = long(line[80:84])
      self.ndp = long(line[85:89])
      self.grn = long(line[90:98])
      self.srn = long(line[99:107])
      self.etype = line[108:115]
      self.depdp = float(line[116:125])
      self.dtype = line[126:127]
      self.mb = float(line[128:135])
      self.mbid = long(line[136:144])
      self.ms = float(line[145:152])
      self.msid = long(line[153:161])
      self.ml = float(line[162:169])
      self.mlid = long(line[170:178])
      self.algorithm = line[179:194]
      self.auth = line[195:210]
      self.commid = long(line[211:219])
      self.lddate = line[220:237]



#
# end of origin30 class


class origin28:
   def __init__(self):
      self.date=-1
      self.time=-9999999999.999
      self.lat=-999.0
      self.lon=-999.0
      self.depth=-999.0
      self.mb=-999.0
      self.ms=-999.0
      self.mo=-999.0
      self.maxint=-1
      self.nass=-1
      self.ndef=-1
      self.ndp=-1
      self.nmb=-1
      self.nms=-1
      self.depdp=-999.0
      self.orid=1
      self.evid=1
      self.grn=-1
      self.srn=-1
      self.ltype="-"
      self.dtype="-"
      self.etype="-"
      self.auth="-"
      self.moauth="-"
      self.intscl="-"
      self.remark="-"

   def write(self):
      print'%8d %15.3f %9.4f %9.4f %9.4f %6.2f %6.2f %7.2f %2d %4d %4d %4d %4d %4d %9.4f %8d %8d %3d %3d %-4s %-1s %-7s %-15s %-15s %-1s %-30s' %(self.date, self.time, self.lat, self.lon, self.depth, self.mb, self.ms, self.mo, self.maxint, self.nass, self.ndef, self.ndp, self.nmb, self.nms, self.depdp, self.orid, self.evid, self.grn, self.srn, self.ltype, self.dtype, self.etype, self.auth, self.moauth, self.intscl, self.remark)
#
#  Write CSS2.8 origin structure to a file.
   def write_to_file(self,prefix):
      if '.origin' in prefix:
          filename=prefix
      else:
          filename=prefix+'.origin'
      fp=open(filename,'w')
      string='%8d %15.3f %9.4f %9.4f %9.4f %6.2f %6.2f %7.2f %2d %4d %4d %4d %4d %4d %9.4f %8d %8d %3d %3d %-4s %-1s %-7s %-15s %-15s %-1s %-30s' % (self.date, self.time, self.lat, self.lon, self.depth, self.mb, self.ms, self.mo, self.maxint, self.nass, self.ndef, self.ndp, self.nmb, self.nms, self.depdp, self.orid, self.evid, self.grn, self.srn, self.ltype, self.dtype, self.etype, self.auth, self.moauth, self.intscl, self.remark)
      fp.write(string)
      fp.close()

#
#  end of origin28 class


class arrival30:
   def __init__(self):
      self.sta="-"
      self.time=-9999999999.0
      self.arid=-1
      self.jdate=-1
      self.stassid=-1
      self.chanid=-1
      self.chan="-"
      self.iphase="-"
      self.stype="-"
      self.deltim=-1.0
      self.azimuth=-1.0
      self.delaz=-1.0
      self.slow=-1.0
      self.delslo=-1.0
      self.ema=-1.0
      self.rect=-1.0
      self.amp=-1.00
      self.per=-1.0
      self.logat=-999.0
      self.clip="-"
      self.fm="-"
      self.snr=-1.0
      self.qual="-"
      self.auth="-"
      self.commid=-1
      self.lddate="-"


   def wrtarrival(self):
      print'%-6s %17.5f %8d %8d %8d %8d %-8s %-8s %-1s %6.3f %7.2f %7.2f %7.2f %7.2f %7.2f %7.3f %10.1f %7.2f %7.2f %-1s %-2s %10.2f %-1s %-15s %8d %-17s\n' % (self.sta, self.time, self.arid, self.jdate, self.stassid, self.chanid, self.chan, self.iphase, self.stype, self.deltim, self.azimuth, self.delaz, self.slow, self.delslo, self.ema, self.rect, self.amp, self.per, self.logat, self.clip, self.fm, self.snr, self.qual, self.auth, self.commid, self.lddate)

   def create_css_string(self):
      astring='%-6s %17.5f %8d %8d %8d %8d %-8s %-8s %-1s %6.3f %7.2f %7.2f %7.2f %7.2f %7.2f %7.3f %10.1f %7.2f %7.2f %-1s %-2s %10.2f %-1s %-15s %8d %-17s\n' % (self.sta, self.time, self.arid, self.jdate, self.stassid, self.chanid, self.chan, self.iphase, self.stype, self.deltim, self.azimuth, self.delaz, self.slow, self.delslo, self.ema, self.rect, self.amp, self.per, self.logat, self.clip, self.fm, self.snr, self.qual, self.auth, self.commid, self.lddate)
      return astring

   def rd_arrival_record(self,line):
      row=string.split(line)
      self.sta=row[0]
      self.time=float(row[1])
      self.arid=long(row[2])
      self.jdate=long(row[3])
      self.stassid=long(row[4])
      self.chanid=long(row[5])
      self.chan=row[6]
      self.iphase=row[7]
      self.stype=row[8]
      self.deltim=float(row[9])
      self.azimuth=float(row[10])
      self.delaz=float(row[11])
      self.slow=float(row[12])
      self.delslo=float(row[13])
      self.ema=float(row[14])
      self.rect=float(row[15])
      self.amp=float(row[16])
      self.per=float(row[17])
      self.logat=float(row[18])
      self.clip=row[19]
      self.fm=row[20]
      self.snr=float(row[21])
      self.qual=row[22]
      self.auth=row[23]
      self.commid=long(row[24])
      self.lddate=row[25]



#
# end of arrival30 class


class assoc30:
   def __init__(self):
      self.arid=-1
      self.orid=-1
      self.sta="-"
      self.phase="-"
      self.belief=0.0
      self.delta=-1.0
      self.seaz=-999.0
      self.esaz=-999.0
      self.timeres=-999.0
      self.timedef="-"
      self.azres=-999.0
      self.azdef="-"
      self.slores=-999.0
      self.slodef="-"
      self.emares=-999.0
      self.wgt=-1.0
      self.vmodel="-"
      self.commid=-1
      self.lddate="-"


   def wrtassoc(self):
      print'%8d %8d %-6s %-8s %4.2f %8.3f %7.2f %7.2f %8.3f %-1s %7.1f %-1s %7.2f %-1s %7.1f %6.3f %-15s %8d %-17s\n'% (self.arid, self.orid, self.sta, self.phase, self.belief, self.delta, self.seaz, self.esaz, self.timeres, self.timedef, self.azres, self.azdef, self.slores, self.slodef, self.emares, self.wgt, self.vmodel, self.commid, self.lddate)

   def create_css_string(self):
      astring='%8d %8d %-6s %-8s %4.2f %8.3f %7.2f %7.2f %8.3f %-1s %7.1f %-1s %7.2f %-1s %7.1f %6.3f %-15s %8d %-17s\n' % (self.arid, self.orid, self.sta, self.phase, self.belief, self.delta, self.seaz, self.esaz, self.timeres, self.timedef, self.azres, self.azdef, self.slores, self.slodef, self.emares, self.wgt, self.vmodel, self.commid, self.lddate)
      return astring

   def rd_assoc_record(self,line):
      row=string.split(line)
      self.arid=long(row[0])
      self.orid=long(row[1])
      self.sta=row[2]
      self.phase=row[3]
      self.belief=float(row[4])
      self.delta=float(row[5])
      self.seaz=float(row[6])
      self.esaz=float(row[7])
      self.timeres=float(row[8])
      self.timedef=row[9]
      self.azres=float(row[10])
      self.azdef=row[11]
      self.slores=float(row[12])
      self.slodef=row[13]
      self.emares=float(row[14])
      self.wgt=float(row[15])
      self.vmodel=row[16]
      self.commid=long(row[17])
      self.lddate=row[18]

#
# end of assoc30 class


# Define css3.0 wfdisc structure class.
class wfdisc30:
   def __init__(self):
      self.sta="-"
      self.chan="-"
      self.time=-9999999999.0
      self.wfid=-1
      self.chanid=-1
      self.jdate=-1
      self.endtime=-9999999999.0
      self.nsamp=-1
      self.samprate=-1.0
      self.calib=-1.0
      self.calper=-1.0
      self.instype="-"
      self.segtype="-"
      self.datatype="-"
      self.clip="-"
      self.dir="-"
      self.dfile="-"
      self.foff=-1.0
      self.commid=-1
      self.lddate="-"

   def wrtwfdisc(self):
##      print'%-6s %-8s %17.5f %8d %8d %8d %17.5f %8d %11.7f %16.6f %16.6f %-6s %-1s %-2s %-1s %-64s %-32s %10d %8d %-17s' % (self.sta, self.chan, self.time, self.wfid, self.chanid, self.jdate, self.endtime, self.nsamp, self.samprate, self.calib, self.calper, self.instype, self.segtype, self.datatype, self.clip, self.dir, self.dfile, self.foff, self.commid, self.lddate)
      a = '%-6s %-8s %17.5f %8d %8d %8d %17.5f %8d %11.7f %16.6f %16.6f %-6s %-1s %-2s %-1s %-64s %-32s %10d %8d %-17s\n' % (self.sta, self.chan, self.time, self.wfid, self.chanid, self.jdate, self.endtime, self.nsamp, self.samprate, self.calib, self.calper, self.instype, self.segtype, self.datatype, self.clip, self.dir, self.dfile, self.foff, self.commid, self.lddate)
      return a

   def rd_wfdisc_record(self,line):
      row=string.split(line)
      self.sta=row[0]
      self.chan=row[1]
      self.time=float(row[2])
      self.wfid=long(row[3])
      self.chanid=long(row[4])
      self.jdate=long(row[5])
      self.endtime=float(row[6])
      self.nsamp=long(row[7])
      self.samprate=float(row[8])
      self.calib=float(row[9])
      self.calper=float(row[10])
      self.instype=row[11]
      self.segtype=row[12]
      self.datatype=row[13]
      self.clip=row[14]
      self.dir=row[15]
      self.dfile=row[16]
      self.foff=long(row[17])
      self.commid=long(row[18])
      self.lddate=row[19]


   def rd_record_safe(self,line):

      self.sta=line[0:6].strip()

      self.chan=line[7:15].strip()

      str=line[16:33].strip()
      try:
         self.time=float(str)
      except:
         sys.exit('fatal error: invalid time field in wfdisc record '+str+' '+self.sta)

      str=line[34:42].strip()
      try:
         self.wfid=long(str)
      except:
         print 'warning: invalid wfid field in wfdisc record '+str+' '+self.sta

      str=line[43:51].strip()
      try:
         self.chanid=long(str)
      except:
         print 'warning: invalid chanid field in wfdisc record '+str+' '+self.sta

      str=line[52:60].strip()
      try:
         self.jdate=long(str)
      except:
         print 'warning: invalid jdate field in wfdisc record '+str+' '+self.sta

      str=line[61:78].strip()
      try:
         self.endtime=float(str)
      except:
         print 'warning: invalid endtime field in wfdisc record '+str+' '+self.sta

      str=line[79:87].strip()
      try:
         self.nsamp=long(str)
      except:
         sys.exit('fatal error: invalid nsamp field in wfdisc record '+str+' '+self.sta)

      str=line[88:99].strip()
      try:
         self.samprate=float(str)
      except:
         sys.exit('fatal error: invalid samprate field in wfdisc record '+str+' '+self.sta)

      str=line[100:116].strip()
      try:
         self.calib=float(str)
      except:
         sys.exit('fatal error: invalid calib field in wfdisc record '+str+' '+self.sta)

      str=line[117:133].strip()
      try:
         self.calper=float(str)
      except:
         sys.exit('fatal error: invalid calper field in wfdisc record '+str+' '+self.sta)

      self.instype=line[134:140].strip()
      self.segtype=line[141:142].strip()
      self.datatype=line[143:145].strip()
      self.clip=line[146:147].strip()
      self.dir=line[148:212].strip()
      self.dfile=line[213:245].strip()

      str=line[246:256].strip()
      try:
         self.foff=long(str)
      except:
         sys.exit('fatal error: invalid foff field in wfdisc record '+str+' '+self.sta)

      str=line[257:265].strip()
      try:
         self.commid=long(str)
      except:
         print 'warning: invalid commid field in wfdisc record '+str+' '+self.sta

      self.lddate=line[266:283].strip()


#
# end of wfdisc30 class


# Define CSS2.8 table

class wfdisc28:
   def __init__(self):
      self.date=-1
      self.time=-9999999999.0
      self.sta="-"
      self.chan="-"
      self.nsamp=-1
      self.smprat=-1.0
      self.calib=-1.0
      self.calper=-1.0
      self.instyp="-"
      self.segtyp="-"
      self.dattyp="s4"
      self.clip="-"
      self.chid=-1
      self.wfid=-1
      self.dir="-"
      self.file="-"
      self.foff=-1
      self.adate=-1
      self.remark="-"

   def wrtwfdisc(self):
      print'%8d %15.3f %-6s %-2s %8d %11.7f %9.6f %7.4f %-6s %-1s %-2s %-1s %8d %8d %-30s %-20s %10d %8d %-30s' % (self.date, self.time, self.sta[0:6], self.chan[0:2], self.nsamp, self.smprat, self.calib, self.calper, self.instyp[0:6], self.segtyp[0:1], self.dattyp[0:2], self.clip[0:1], self.chid, self.wfid, self.dir[0:30], self.file[0:20], self.foff, self.adate, self.remark[0:30])

   def rd_wfdisc_record(self,line):
      row=string.split(line)
      self.sta=row[2]
      self.chan=row[3]
      self.time=float(row[1])
      self.wfid=long(row[12])
      self.chid=long(row[13])
      self.date=long(row[0])
      self.nsamp=long(row[4])
      self.smprat=float(row[5])
      self.calib=float(row[6])
      self.calper=float(row[7])
      self.dattyp=row[10]
      self.instyp=row[8]
      self.dir=row[14]
      self.file=row[15]
      self.foff=long(row[16])


   def rd_record_safe(self,line):

      str=line[0:8].strip()
      try:
         self.date=long(str)
      except:
         print 'warning: invalid date field in wfdisc record '+str+' '+self.sta

      str=line[9:24].strip()
      try:
         self.time=float(str)
      except:
         sys.exit('fatal error: invalid time field in wfdisc record '+str+' '+self.sta)

      self.sta=line[25:31].strip()

      self.chan=line[32:34].strip()

      str=line[35:43].strip()
      try:
         self.nsamp=long(str)
      except:
         sys.exit('fatal error: invalid nsamp field in wfdisc record '+str+' '+self.sta)

      str=line[44:55].strip()
      try:
         self.smprat=float(str)
      except:
         sys.exit('fatal error: invalid smprat field in wfdisc record '+str+' '+self.sta)

      str=line[56:65].strip()
      try:
         self.calib=float(str)
      except:
         sys.exit('fatal error: invalid calib field in wfdisc record '+str+' '+self.sta)

      str=line[66:73].strip()
      try:
         self.calper=float(str)
      except:
         sys.exit('fatal error: invalid calper field in wfdisc record '+str+' '+self.sta)

      self.instyp=line[74:80].strip()
      self.segtyp=line[81:82].strip()
      self.dattyp=line[83:85].strip()
      self.clip=line[86:87].strip()

      str=line[88:96].strip()
      try:
         self.chid=long(str)
      except:
         print 'warning: invalid chid field in wfdisc record '+str+' '+self.sta

      str=line[97:105].strip()
      try:
         self.wfid=long(str)
      except:
         print 'warning: invalid wfid field in wfdisc record '+str+' '+self.sta


      self.dir=line[106:136].strip()
      self.file=line[137:157].strip()

      str=line[158:168].strip()
      try:
         self.foff=long(str)
      except:
         sys.exit('fatal error: invalid foff field in wfdisc record '+str+' '+self.sta)

      str=line[169:177].strip()
      try:
         self.adate=long(str)
      except:
         print 'warning: invalid adate field in wfdisc record '+str+' '+self.sta

      self.remark=line[178:208].strip()

#
# end of wfdisc28 class


class origerr30:
   def __init__(self, orid=-1, sxx=-1.0, syy=-1.0, szz=-1.0, stt=-1.0, sxy=-1.0, sxz=-1.0, syz=-1.0, stx=-1.0, sty=-1.0,
                stz=-1.0, sdobs=-1.0, smajax=-1.0, sminax=-1.0, strike=-1.0, sdepth=-1.0, stime=-1.0, conf=0.0,
                commid=-1, lddate="-"):
      self.orid = orid
      self.sxx = sxx
      self.syy = syy
      self.szz = szz
      self.stt = stt
      self.sxy = sxy
      self.sxz = sxz
      self.syz = syz
      self.stx = stx
      self.sty = sty
      self.stz = stz
      self.sdobs = sdobs
      self.smajax = smajax
      self.sminax = sminax
      self.strike = strike
      self.sdepth = sdepth
      self.stime = stime
      self.conf = conf
      self.commid = commid
      self.lddate = lddate


   def wrtorigerr(self):
      print'%8d %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %9.4f %9.4f %9.4f %6.2f %9.4f %8.2f %5.3f %8d %-17s\n' % (self.orid, self.sxx, self.syy, self.szz, self.stt, self.sxy, self.sxz, self.syz, self.stx, self.sty, self.stz, self.sdobs, self.smajax, self.sminax, self.strike, self.sdepth, self.stime, self.conf, self.commid, self.lddate)

   def create_css_string(self):
      ostring='%8d %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %9.4f %9.4f %9.4f %6.2f %9.4f %8.2f %5.3f %8d %-17s\n' % (self.orid, self.sxx, self.syy, self.szz, self.stt, self.sxy, self.sxz, self.syz, self.stx, self.sty, self.stz, self.sdobs, self.smajax, self.sminax, self.strike, self.sdepth, self.stime, self.conf, self.commid, self.lddate)
      return ostring

   def rd_origerr_record(self,line):
      row=string.split(line)
      self.orid=long(row[0])
      self.sxx=float(row[1])
      self.syy=float(row[2])
      self.szz=float(row[3])
      self.stt=float(row[4])
      self.sxy=float(row[5])
      self.sxz=float(row[6])
      self.syz=float(row[7])
      self.stx=float(row[8])
      self.sty=float(row[9])
      self.stz=float(row[10])
      self.sdobs=float(row[11])
      self.smajax=float(row[12])
      self.sminax=float(row[13])
      self.strike=float(row[14])
      self.sdepth=float(row[14])
      self.stime=float(row[16])
      self.conf=float(row[17])
      self.commid=long(row[18])
      self.lddate=row[19]

   def from_string(self, line):
       self.orid = long(line[0:8].strip())
       self.sxx = float(line[9:24].strip())
       self.syy = float(line[25:40].strip())
       self.szz = float(line[41:56].strip())
       self.stt = float(line[57:72].strip())
       self.sxy = float(line[73:88].strip())
       self.sxz = float(line[89:104].strip())
       self.syz = float(line[105:120].strip())
       self.stx = float(line[121:136].strip())
       self.sty = float(line[137:152].strip())
       self.stz = float(line[153:168].strip())
       self.sdobs = float(line[169:178].strip())
       self.smajax = float(line[179:188].strip())
       self.sminax = float(line[189:198].strip())
       self.strike = float(line[199:205].strip())
       self.sdepth = float(line[206:215].strip())
       self.stime = float(line[216:224].strip())
       self.conf = float(line[225:230].strip())
       self.commid = long(line[231:239].strip())
       self.lddate = line[240:257].strip()

class origerr28:
   def __init__(self):
      self.orid=-1
      self.sdobs=-999.0
      self.sxx=-999.0
      self.syy=-999.0
      self.szz=-999.0
      self.stt=-999.0
      self.sxy=-999.0
      self.sxz=-999.0
      self.syz=-999.0
      self.stx=-999.0
      self.sty=-999.0
      self.stz=-999.0
      self.sdmb=-1.0
      self.sdms=-1.0
      self.sddp=-1.0
      self.sdzdp=-1.0
      self.remark='-'

   def wrtorigerr(self):
      print'%8d %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %9.4f %-30s' % (self.orid, self.sdobs, self.sxx, self.syy, self.szz, self.stt, self.sxy, self.sxz, self.syz, self.stx, self.sty, self.stz, self.sdmb, self.sdms, self.sddp, self.sdzdp, self.remark)

#
# end origerr class

class wftag30:

   def __init__(self):
      self.tagname="-"
      self.tagid=-1
      self.wfid=-1
      self.lddate="-"

   def rd_wftag_record(self,line):
      row=line.split
      self.tagname=row[0]
      self.tagid=long(row[1])
      self.wfid=long(row[2])
      self.lddate=row[3]

   def write_wftag_record(self,fp):
      fp.write('%-8s %8d %8d %-17s \n' % (self.tagname,self.tagid,self.wfid,self.lddate))

#
# end wftag class


class site30:

   def __init__(self):
      self.sta='-'
      self.ondate=-1
      self.offdate=-1
      self.lat=-999.0
      self.lon=-999.0
      self.elev=-999.0
      self.staname='-'
      self.statype='-'
      self.refsta='-'
      self.dnorth=0.0
      self.deast=0.0
      self.lddate='-'

   def rd_site_record(self,line):
      self.sta=line[0:6].strip()
      self.ondate=long(line[7:15])
      self.offdate=long(line[16:24])
      self.lat=float(line[25:34])
      self.lon=float(line[35:44])
      self.elev=float(line[45:54])
      self.staname=line[55:105].strip()
      self.statype=line[106:110].strip()
      self.refsta=line[111:117].strip()
      self.dnorth=float(line[118:127])
      self.deast=float(line[128:137])
      self.lddate=line[138:155].strip()

   def write_record(self,fp):
      fp.write('%-6s %8d %8d %9.4f %9.4f %9.4f %-50s %-4s %-6s %9.4f %9.4f %-17s  \n' % (self.sta,self.ondate,self.offdate,self.lat,self.lon,self.elev,self.staname,self.statype,self.refsta,self.dnorth,self.deast,self.lddate))

   def record_string(self):
      rec='%-6s %8d %8d %9.4f %9.4f %9.4f %-50s %-4s %-6s %9.4f %9.4f %-17s  \n' % (self.sta,self.ondate,self.offdate,self.lat,self.lon,self.elev,self.staname,self.statype,self.refsta,self.dnorth,self.deast,self.lddate)
      return rec
#
# end site30 class

class sitechan30:

   def __init__(self):
      self.sta='-'
      self.chan='-'
      self.ondate=-1
      self.chanid=-1
      self.offdate=-1
      self.ctype='-'
      self.edepth=0.0
      self.hang=0.0
      self.vang=0.0
      self.descrip='-'
      self.lddate='-'

   def rd_record(self,line):
      self.sta=line[0:6].strip()
      self.chan=line[7:15].strip()
      self.ondate=long(line[16:24].strip())
      self.chanid=long(line[25:33].strip())
      self.offdate=long(line[34:42].strip())
      self.ctype=line[43:47].strip()
      self.edepth=float(line[48:57].strip())
      self.hang=float(line[58:64].strip())
      self.vang=float(line[65:71].strip())
      self.descrip=line[72:122].strip()
      self.lddate=line[123:140].strip()

   def rd_record_freeform(self,line):
      row=line.split()
      self.sta=row[0].strip()
      self.chan=row[1].strip()
      self.ondate=long(row[2].strip())
      self.chanid=long(row[3].strip())
      self.offdate=long(row[4].strip())
      self.ctype=row[5].strip()
      self.edepth=float(row[6].strip())
      self.hang=float(row[7].strip())
      self.vang=float(row[8].strip())
      self.descrip=row[9].strip()
      self.lddate=row[10].strip()

   def write_record(self,fp):
      fp.write('%-6s %-8s %8d %8d %-4s %9.4f %6.1f %6.1f %-50s %-17s\n' % (self.sta,self.chan,self.ondate,self.chanid,self.offdate,self.ctype,self.edepth,self.hang,self.vang,self.descrip,self.lddate))

   def record_string(self):
      rec='%-6s %-8s %8d %8d %-4s %9.4f %6.1f %6.1f %-50s %-17s\n' % (self.sta,self.chan,self.ondate,self.chanid,self.offdate,self.ctype,self.edepth,self.hang,self.vang,self.descrip,self.lddate)
      return rec

# end sitechan30 class

class sensor30:

   def __init__(self):
      self.sta='-'
      self.chan='-'
      self.time=-9999999999.0
      self.endtime=-9999999999.0
      self.inid=-1
      self.chanid=-1
      self.jdate=-1
      self.calratio=1.0
      self.calper=1.0
      self.tshift=0.0
      self.instant='y'
      self.lddate='-'

   def rd_record(self,line):
      self.sta=line[0:6].strip()
      self.chan=line[7:15].strip()
      self.time=float(line[16:33].strip())
      self.endtime=float(line[34:51].strip())
      self.inid=long(line[52:60].strip())
      self.chanid=long(line[61:69].strip())
      self.jdate=long(line[70:78].strip())
      self.calratio=float(line[79:95].strip())
      self.calper=float(line[96:112].strip())
      self.tshift=float(line[113:119].strip())
      self.instant=line[120:121].strip()
      self.lddate=line[122:139].strip()

   def rd_record_freeform(self,line):
      row=line.split()
      self.sta=row[0]
      self.chan=row[1]
      self.time=float(row[2])
      self.endtime=float(row[3])
      self.inid=long(row[4])
      self.chanid=long(row[5])
      self.jdate=long(row[6])
      self.calratio=float(row[7])
      self.calper=float(row[8])
      self.tshift=float(row[9])
      self.instant=row[10]
      self.lddate=row[11]


   def write_record(self,fp):
      fp.write('%-6s %-8s %17.5f %17.5f %8d %8d %8d %16.6f %16.6f %6.2f %1s %-17s\n' % (self.sta,self.chan,self.time,self.endtime,self.inid,self.chanid,self.jdate,self.calratio,self.calper,self.tshift,self.instant,self.lddate))

   def record_string(self):
      rec='%-6s %-8s %17.5f %17.5f %8d %8d %8d %16.6f %16.6f %6.2f %1s %-17s\n' % (self.sta,self.chan,self.time,self.endtime,self.inid,self.chanid,self.jdate,self.calratio,self.calper,self.tshift,self.instant,self.lddate)
      return rec
#
# end sensor30 class

class instrument30:

   def __init__(self):
      self.inid=-1
      self.insname='-'
      self.instype='-'
      self.band='-'
      self.digital='-'
      self.samprate=-999.99
      self.ncalib=-999.99
      self.ncalper=-999.99
      self.dir='-'
      self.dfile='-'
      self.rsptype='-'
      self.lddate='-'

   def rd_record(self,line):
      self.inid=long(line[0:8].strip())
      self.insname=line[9:59].strip()
      self.instype=line[62:66].strip()
      self.band=line[67:68].strip()
      self.digital=line[69:70].strip()
      self.samprate=float(line[71:82].strip())
      self.ncalib=float(line[83:99].strip())
      self.ncalper=float(line[100:116].strip())
      self.dir=line[117:181].strip()
      self.dfile=line[182:214].strip()
      self.rsptype=line[215:221].strip()
      self.lddate=line[222:239].strip()


   def rd_record_freeform(self,line):
      row=line.split()
      self.inid=long(row[0])
      self.insname=row[1]
      self.instype=row[2]
      self.band=row[3]
      self.digital=row[4]
      self.samprate=float(row[5])
      self.ncalib=float(row[6])
      self.ncalper=float(row[7])
      self.dir=row[8]
      self.dfile=row[9]
      self.rsptype=row[10]
      self.lddate=row[11]

   def write_record(self,fp):
      fp.write('%8d %-50s %-6s %-1s %-1s %11.7f %16.6f %16.6f %-64s %-32s %-6s %-17s\n' % (self.inid,self.insname,self.instype,self.band,self.digital,self.samprate,self.ncalib,self.ncalper,self.dir,self.dfile,self.rsptype,self.lddate))

   def record_string(self):
      rec='%8d %-50s %-6s %-1s %-1s %11.7f %16.6f %16.6f %-64s %-32s %-6s %-17s\n' % (self.inid,self.insname,self.instype,self.band,self.digital,self.samprate,self.ncalib,self.ncalper,self.dir,self.dfile,self.rsptype,self.lddate)
      return rec
#
# Added  by Mark Leonard December 2015
#
# netmag30 structure
class netmag30:
    def __init__(self):
        self.magid = -1
        self.net = "-"
        self.orid = -1
        self.evid = -1
        self.magtype = "-"
        self.nsta = -1
        self.magnitude = -999.0
        self.uncertainty = -990.0
        self.auth = "-"
        self.commid = -1
        self.lddate = "-"

    #def create_css_string(self):
    #  ostring='%8d %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %15.4f %9.4f %9.4f %9.4f %6.2f %9.4f %8.2f %5.3f %8d %-17s\n' % (self.orid, self.sxx, self.syy, self.szz, self.stt, self.sxy, self.sxz, self.syz, self.stx, self.sty, self.stz, self.sdobs, self.smajax, self.sminax, self.strike, self.sdepth, self.stime, self.conf, self.commid, self.lddate)
     # return ostring
    def create_css_string(self):
        nstring='%8d %-8s %8d %8d %-6s %8d %7.2f %7.2f %-15s %8d %-17s\n' % (self.magid, self.net, self.orid, self.evid, self.magtype, self.nsta, self.magnitude, self.uncertainty, self.auth, self.commid, self.lddate)
        return nstring
# end netmag30 class
        #
# event30 structure
class event30:
    def __init__(self, evid=-1, evname="-", prefor=-1, auth="-", commid=-1, lddate="-"):
        self.evid = evid
        self.evname = evname
        self.prefor = prefor
        self.auth = auth
        self.commid = commid
        self.lddate = lddate

    def create_css_string(self):
        # print(self.evid, self.evname, self.prefor, self.auth, self.commid, self.lddate)
        astring='%8d %-15s %8d %-15s %8d %-17s\n' % (self.evid, self.evname, self.prefor, self.auth, self.commid, self.lddate)
        return astring

    def from_string(self, line):
        self.evid = long(line[0:8].strip())
        self.evname = line[9:24].strip()
        self.prefor = long(line[25:33].strip())
        self.auth = line[34:49].strip()
        self.commid = long(line[50:58].strip())
        self.lddate = line[59:76].strip()

# end event30 class
#
# remark30 structure
class remark30:
    def __init__(self, commid=-1, lineno=1, remark='-', lddate='-'):
        self.commid = commid
        self.lineno = lineno
        self.remark = remark
        self.lddate = lddate

    def create_css_string(self):
        astring='%8d %8d %-80s %-17s\n' % (self.commid, self.lineno, self.remark, self.lddate)
        return astring

    def from_string(self, line):
        self.commid = long(line[0:8].strip())
        self.lineno = long(line[9:17].strip())
        self.remark = line[18:98].strip()
        self.lddate = line[99:116].strip()
# end remark30 class