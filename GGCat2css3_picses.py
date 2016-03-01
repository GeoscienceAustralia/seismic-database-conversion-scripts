#!/usr/bin/env python

import csv
import os
import pisces.schema.css3 as css3
from datetime import datetime

class Event(css3.Event):
    __tablename__ = 'event'


class Remark(css3.Remark):
    __tablename__ = 'remark'


class Origerr(css3.Origerr):
    __tablename__ = 'origerr'


class Origin(css3.Origin):
    __tablename__ = 'origin'


def mk_int(s):
    s = s.strip()
    return int(float(s)) if len(s) > 0 else None


def mk_float(s):
    s = s.strip()
    return float(s) if len(s) > 0 else None


def julday(dt):
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday


def etype_str(etype, depend):
    # etype is formatted to have type of event type (e.g., coal blast, local earthquake) on the left
    # and then have the association (e.g., mainshock, aftershock, foreshock) on the right
    # it is padded with '_', with a maximum total length of 7
    # for example: l____ms
    return '{etype}{s:_^{padding}}{depend}'.format(etype=etype,
                                                   depend=depend,
                                                   s='',
                                                   padding=7 - (len(etype) + len(depend)))


event_types = {'blast': 'qb', 'coal': 'cb', 'local': 'l', 'tele': 't', 'unsure': 'uq'}
depends = {'Aftershock': 'as', 'Foreshock': 'fs', 'Mainshock': 'ms', 'Swarm': 'ss', 'None': 'eq', 'Unsure': 'eq'}
depth_types = {'D': 'f', 'C': 'r', 'G': 'g', 'N': 'n', 'pP': 'd', 'B': 'd'}
mags = ['ML', 'mb', 'MS', 'Mw']

# TODO try,catch for files
with open('GGcat_big_2000.csv', 'rb') as csvfile, \
        open('out.event', 'w') as evi_out, open('out.remark', 'w') as rem_out, \
        open('out.origerr', 'w') as oer_out, open('out.origin', 'w') as ori_out:
    reader = csv.DictReader(csvfile)

    id = 1
    mlid = 0
    mbid = 0
    msid = 0
    for row in reader:
        if row['Source'] == "Source":  # skip first line
            continue

        dt = datetime(mk_int(row['Year']),
                      mk_int(row['Month']),
                      mk_int(row['Day']),
                      mk_int(row['Hour']),
                      mk_int(row['Minute']),
                      mk_int(row['Second']) or 0,
                      int(((mk_float(row['Second']) or 0) % 1) * 1000000))  # microsecond

        # Event
        evi = Event(evid=id,
                    evname=row['Place'],
                    prefor=id,
                    auth=row['Source'],
                    commid=id,
                    lddate=dt)
        evi_out.write(str(evi) + os.linesep)

        # Remark
        rem = Remark(commid=id,
                     lineno=1,  # expecting only 1 line per remark, not multiple
                     remark=row['Magnitude text'],
                     lddate=dt)
        rem_out.write(str(rem) + os.linesep)

        # Origerr
        oer = Origerr(orid=id,
                      sdobs=mk_float(row['RMS']),
                      smajax=mk_float(row['Semi Major']),
                      sminax=mk_float(row['Semi Minor']),
                      strike=0.000000,
                      sdepth=mk_float(row['Depth Unc']),
                      stime=mk_float(row['Time Unc']),
                      conf=0.5,  # no confidence value is available
                      commid=id,
                      lddate=dt)
        oer_out.write(str(oer) + os.linesep)

        # Origin
        ori = Origin(orid=id,
                     evid=id,
                     lat=mk_float(row['Latitude']) * -1.0,  # GGCat doesn't have -ve lat for south
                     lon=mk_float(row['Longitude']),
                     depth=mk_float(row['Depth']),
                     time=(dt - datetime(1970, 1, 1)).total_seconds(),  # epoch
                     jdate=julday(dt),
                     ndef=mk_int(row['Arrivals']),
                     etype=etype_str(event_types[row['Type'].strip()] if row['Type'].strip() in event_types
                                      else '',
                                      depends[row['Dependence'].strip()] if row['Dependence'].strip() in depends
                                      else ''),
                     dtype=depth_types[row['Depth Code'].strip()] if row['Depth Code'].strip() in depth_types else None,
                     algorithm='GGCat',
                     auth=row['Source'],
                     commid=id,
                     lddate=dt)

        mag_type = row['Mag Type'].upper()
        if mag_type == 'ML':
            mlid += 1
            ori.mlid = mlid
            ori.ml = mk_float(row['Mag Value'])
        elif mag_type == 'MB':
            mbid += 1
            ori.mbid = mbid
            ori.mb = mk_float(row['Mag Value'])
        elif mag_type == 'MS' or mag_type == 'MW':
            msid += 1
            ori.msid = msid
            ori.ms = mk_float(row['Mag Value'])

        ori_out.write(str(ori) + os.linesep)

        id += 1

print("Event:")
with open('out.event', 'r') as evi_in:
    for line in evi_in:
        print Event.from_string(line)

print("Remark:")
with open('out.remark', 'r') as rem_in:
    for line in rem_in:
        print Remark.from_string(line)

print("Origerr:")
with open('out.origerr', 'r') as oer_in:
    for line in oer_in:
        print Origerr.from_string(line)

print("Origin:")
with open('out.origin', 'r') as ori_in:
    for line in ori_in:
        print Origin.from_string(line)

# Notes:
# - evname in Pisces is 32 wide, in the spec it's 15
# - lddate is datetime %y-%m-%d %H:%M:%S in Pisces, in spec it's either a17 date, or %17.5f epoch time, in new spec it says any valid ORACLE date range??


# Example event output:
#
#        1 Off Exmouth Gulf, WA                    1 EHB                         1 00-10-11 19:27:16
#        2 South of Australia, Southern Oce        2 EHB                         2 00-12-25 13:24:24
#        3 Tennant Creek, NT                       3 EHB                         3 01-09-14 15:18:30
#        4 Burakin, WA                             4 ISC                         4 01-09-28 02:54:52
#        5 Ravensthorpe, WA                        5 ISC                         5 01-10-19 17:43:20
#        6 South of Australia                      6 EHB                         6 01-12-12 17:52:40
#        7 South of Australia                      7 EHB                         7 01-12-13 07:28:11
#        8 Burakin, WA                             8 AUST                        8 02-03-05 01:47:38
#        9 Mt Redvers, NT                          9 AUST                        9 04-02-11 09:17:59
#       10 141 km W of Strahan, Tas               10 MEL                        10 06-12-14 17:23:07
#       11 SSE of Esperance, Southern Ocean       11 ADE                        11 10-04-05 11:23:00

# Example remark output
#
#        1        1 mb 5.1 ISC 49 MS 4.4 ISC 15 Mw 5.1 HRVD                                          -                    00-10-11 19:27:16
#        2        1 mb 5.6 ISC 33 MS 5.5 ISC 107 Mw 5.7 HRVD                                         -                    00-12-25 13:24:24
#        3        1 -                                                                                -                    01-09-14 15:18:30
#        4        1 ML 5.0 AUST mb 5.0 ISC 25 MS 3.3 ISC 2                                           -                    01-09-28 02:54:52
#        5        1 mb 5.1 ISC 31 MS 4.4 ISC 11                                                      -                    01-10-19 17:43:20
#        6        1 -                                                                                -                    01-12-12 17:52:40
#        7        1 -                                                                                -                    01-12-13 07:28:11
#        8        1 ML 5.0 AUST                                                                      -                    02-03-05 01:47:38
#        9        1 -                                                                                -                    04-02-11 09:17:59
#       10        1 ML 5.0 MEL 7                                                                     -                    06-12-14 17:23:07
#       11        1 ML 5.1 ADE                                                                       -                    10-04-05 11:23:00

# Example origerr output
#
#       1 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    0.8800    7.2000    4.3000   0.00    4.4000  -1.00 0.500        1 00-10-11 19:27:16
#       2 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    0.8800    4.7000    3.7000   0.00    2.6000  -1.00 0.500        2 00-12-25 13:24:24
#       3 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    1.0400   -1.0000   -1.0000   0.00   -1.0000  -1.00 0.500        3 01-09-14 15:18:30
#       4 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    1.3300    3.7000    3.3000   0.00   -1.0000   0.26 0.500        4 01-09-28 02:54:52
#       5 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    1.2500    4.6000    3.3000   0.00   -1.0000   0.25 0.500        5 01-10-19 17:43:20
#       6 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    1.0300   -1.0000   -1.0000   0.00   -1.0000  -1.00 0.500        6 01-12-12 17:52:40
#       7 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    1.0400   -1.0000   -1.0000   0.00   -1.0000  -1.00 0.500        7 01-12-13 07:28:11
#       8 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000   -1.0000    2.2000    1.9000   0.00    5.5000   0.60 0.500        8 02-03-05 01:47:38
#       9 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000   -1.0000    8.9000    7.2000   0.00   25.0000   2.90 0.500        9 04-02-11 09:17:59
#      10 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000    1.0800    6.7000    6.5000   0.00   11.0000   1.00 0.500       10 06-12-14 17:23:07
#      11 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000 -100000000.0000   -1.0000   -1.0000   -1.0000   0.00   -1.0000  -1.00 0.500       11 10-04-05 11:23:00
