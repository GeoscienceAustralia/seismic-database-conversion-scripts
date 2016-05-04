#!/usr/bin/env python
"""
Read in GGCat CSV file and convert each line into CSS3.0 entries

Developed: March 2016 - Jonathan Mettes
"""
import csv
import os
from css_types import event30, remark30, origerr30, origin30, netmag30
from datetime import datetime


GGCAT_FILE = "sample_data/GGcat_big_2000.csv"


def mk_int(s):
    s = s.strip()
    return int(float(s)) if len(s) > 0 else None


def mk_float(s):
    s = s.strip()
    return float(s) if len(s) > 0 else None


def ignore_empty(d):
    n = {}
    for k, v in d.iteritems():
        if v:
            n[k] = v
    return n


def julday(dt):
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday


def etype_str(etype, depend):
    """
    etype is formatted to have type of event type (e.g., coal blast, local earthquake) on the left
    and then have the association (e.g., mainshock, aftershock, foreshock) on the right
    it is padded with '_', with a maximum total length of 7
    for example: l____ms
    """
    return '{etype}{s:_^{padding}}{depend}'.format(etype=etype,
                                                   depend=depend,
                                                   s='',
                                                   padding=7 - (len(etype) + len(depend)))


event_types = {'blast': 'qb', 'coal': 'cb', 'local': 'l', 'tele': 't', 'unsure': 'uq'}
depends = {'Aftershock': 'as', 'Foreshock': 'fs', 'Mainshock': 'ms', 'Swarm': 'ss', 'None': 'eq', 'Unsure': 'eq'}
depth_types = {'D': 'f', 'C': 'r', 'G': 'g', 'N': 'n', 'pP': 'd', 'B': 'd'}
mags = ['ML', 'mb', 'MS', 'Mw']

# TODO try,catch for files
with open(GGCAT_FILE, 'rb') as csvfile, \
        open('out.event', 'w') as evi_out,\
        open('out.remark', 'w') as rem_out, \
        open('out.origerr', 'w') as oer_out, \
        open('out.origin', 'w') as ori_out, \
        open('out.netmag', 'w') as nmg_out:
    reader = csv.DictReader(csvfile)

    id = 1
    mlid = 0
    mbid = 0
    msid = 0
    magid = 0
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
        evi = event30(evid=id,
                      evname=row['Place'][:15],
                      prefor=id,
                      auth=row['Source'][:15],
                      commid=id)
        evi_out.write(evi.create_css_string())

        # Remark
        rem = remark30(commid=id,
                       lineno=1,  # expecting only 1 line per remark, not multiple
                       remark=row['Magnitude text'][:80])
        rem_out.write(rem.create_css_string())

        # Origerr
        oer_dict = {'orid': id,
                    'commid': id,
                    'sdobs':  mk_float(row['RMS']),
                    'smajax': mk_float(row['Semi Major']),
                    'sminax': mk_float(row['Semi Minor']),
                    'strike': mk_float(row['Smaj Azim']),
                    'sdepth': mk_float(row['Depth Unc']),
                    'stime':  mk_float(row['Time Unc'])}

        oer = origerr30(**ignore_empty(oer_dict))

        oer_out.write(oer.create_css_string())

        # Origin
        ori_dict = {
            'orid': id,
            'evid': id,
            'time': (dt - datetime(1970, 1, 1)).total_seconds(),  # epoch
            'jdate': julday(dt),
            'etype': etype_str(event_types[row['Type'].strip()] if row['Type'].strip() in event_types
                               else '',
                               depends[row['Dependence'].strip()] if row['Dependence'].strip() in depends
                               else ''),
            'algorithm': 'GGCat',
            'auth': row['Source'],
            'commid': id,
            'lat': mk_float(row['Latitude']) * -1.0,  # GGCat doesn't have -ve lat for south
            'lon': mk_float(row['Longitude']),
            'depth': mk_float(row['Depth']),
            'ndef': mk_int(row['Arrivals']),
            'dtype': depth_types[row['Depth Code'].strip()] if row['Depth Code'].strip() and
                                                               row['Depth Code'].strip() in depth_types else None
        }
        ori = origin30(**ignore_empty(ori_dict))

        mag_type = row['Mag Type'].upper()
        if mag_type == 'ML':
            mlid += 1
            ori.mlid = mlid
            magid = mlid
            ori.ml = mk_float(row['Mag Value'])
        elif mag_type == 'MB':
            mbid += 1
            ori.mbid = mbid
            magid = mbid
            ori.mb = mk_float(row['Mag Value'])
        elif mag_type == 'MS' or mag_type == 'MW':
            msid += 1
            ori.msid = msid
            magid = msid
            ori.ms = mk_float(row['Mag Value'])

        ori_out.write(ori.create_css_string())

        # Netmag
        nmg = netmag30(magid=magid,
                       net=row['Source'],
                       orid=id,
                       magtype=mag_type,
                       magnitude=mk_float(row['Mag Value']),
                       auth=row['Source'],
                       )

        nmg_out.write(nmg.create_css_string())

        id += 1

# print out all the converted CSS strings
print("Event:")
event = event30()
with open('out.event', 'r') as evi_in:
    for line in evi_in:
        event.from_string(line)
        print(event.create_css_string()),

print("Remark:")
remark = remark30()
with open('out.remark', 'r') as rem_in:
    for line in rem_in:
        remark.from_string(line)
        print remark.create_css_string(),

print("Origerr:")
origerr = origerr30()
with open('out.origerr', 'r') as oer_in:
    for line in oer_in:
        origerr.from_string(line)
        print origerr.create_css_string(),

print("Origin:")
origin = origin30()
with open('out.origin', 'r') as ori_in:
    for line in ori_in:
        origin.from_string(line)
        print origin.create_css_string(),

print("Netmag:")
netmag = netmag30()
with open('out.netmag', 'r') as nmg_in:
    for line in nmg_in:
        netmag.from_string(line)
        print netmag.create_css_string(),
