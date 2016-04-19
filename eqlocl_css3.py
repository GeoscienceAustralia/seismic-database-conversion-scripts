#!/usr/bin/env python
"""
Developed by: Jonathan Mettes - March 2016

* open GAED database in the form of flat CSS3 files (.event, .origin, .origerr, .netmag, .remark)
* traverses through directories looking for eqlocl files (text files starting with ASC or MUN)
* for each eqlocl file, find closest eqlocl arrivals to a GAED origin
   - don't make any changes to origin if arrival is very close to origin (said to be the same origin)
   - otherwise if its very close, create a new origin for this arrival
   - insert new parameters for tables (preserve existing data)
   - log any unassociated files
"""
import json
import glob
from datetime import datetime, timedelta
from css_types2 import origin30, origerr30, netmag30
from geopy.distance import vincenty
import logging
import sys

logging.basicConfig(stream=sys.stdout, filename='log.txt', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

GAED_ORIGIN_FILE = 'out.origin'
GAED_NETMAG_FILE = 'out.netmag'
EQLOCL_ROOT = 'eqlocl/'


def julday(dt):
    tt = dt.timetuple()
    return tt.tm_year * 1000 + tt.tm_yday

def add(t, path, v):
    """
    convert line to nested dictionary entries.
        e.g., "arrival.sitename.1 = WR1" becomes { "arrival": { "sitename": { "1": { "value": "WR1" } } } }

    :param t: dictionary
    :param path: list of the variable name which is originally '.'-delimited
           e.g., ['magnitude', 'sitename', '0'] or ['version']
    :param v: the variable value
    :return:
    """
    for node in path:
        k = node.strip()
        t.setdefault(k, {})
        t = t[k]

    t['value'] = v

def get_epoch(dt):
    return (dt - datetime(1970, 1, 1)).total_seconds()

def getval(eqlocl, var):
    if var in eqlocl and len(eqlocl[var]['value'].strip()) > 0:
        return eqlocl[var]['value'].strip()
    else:
        return None

def main():
    # GAED
    origins = []
    with open(GAED_ORIGIN_FILE, 'r') as ori_in:
        for line in ori_in:
            ori = origin30()
            ori.from_string(line)
            origins.append(ori)

    netmags = []
    with open(GAED_NETMAG_FILE, 'r') as nmg_in:
        for line in nmg_in:
            nmg = netmag30()
            nmg.from_string(line)
            netmags.append(nmg)

    # set ids to ones after the last largest
    # will increment when inserting new entries
    orid = max(origins, key=lambda origin: origin.orid).orid + 1
    mlid = max(origins, key=lambda origin: origin.mlid).mlid + 1
    mbid = max(origins, key=lambda origin: origin.mbid).mbid + 1
    msid = max(origins, key=lambda origin: origin.msid).msid + 1

    # will traverse directories and parse only text files starting with GA, agso, ASC or MUN
    # (to avoid parsing random files)
    for filename in glob.glob(EQLOCL_ROOT + '/**/[GA|agso|ASC|MUN]*.txt'):
        eqlocl = {}
        with open(filename, 'r') as eqlocl_file:
            for line in eqlocl_file:
                if line.strip():  # non-empty
                    key, value = line.split('=')
                    add(t=eqlocl, path=key.split('.'), v=value.strip())

        if 'time' not in eqlocl['arrival']:  # this file has no arrivals
            logging.info('no arrivals in ' + filename + ', skipping')
            continue

        try:
            # get eqlocl date
            # some eqlocl files have empty year/month/day fields. skip these files
            # purposely omit second field, because we want to use the arrival's seconds, not the eqlocl file's second
            eq_date = datetime(year=int(eqlocl['year']['value']),
                               month=int(eqlocl['month']['value']),
                               day=int(eqlocl['day']['value']),
                               hour=int(eqlocl['hour']['value']),
                               minute=int(eqlocl['minute']['value']))
        except:
            logging.info('cannot parse  invalid date in ' + filename + ', skipping')
            continue

        for id in eqlocl['arrival']['time']:
            # arrival time is: eqlocl time (excluding its seconds) + arrival second (and fractional second)
            arrival_seconds, arrival_frac_secs = eqlocl['arrival']['time'][id]['value'].split('.')  # arrival offset
            arrival_offset = timedelta(seconds=int(arrival_seconds),
                                       microseconds=int(arrival_frac_secs))
            arrival_epoch = get_epoch(eq_date + arrival_offset)

            # find the origin with the closest time to this arrival
            # that is, find the origin with the smallest difference in time from the arrival time
            closest_origin = min(origins, key=lambda origin: abs(origin.time - arrival_epoch))

            # how close in time is the arrival to the origin time
            time_diff = abs(closest_origin.time - arrival_epoch)

            # make Eqlocl lat & lon same precision as CSS3.0
            eqlocl_lat = "%9.4f" % float(eqlocl['latitude']['value'].strip())
            eqlocl_lon = "%9.4f" % float(eqlocl['longitude']['value'].strip())

            # how close together is the lat/long between the origin and arrival
            pos_diff = abs(vincenty((float(closest_origin.lat), float(closest_origin.lon)), (eqlocl_lat, eqlocl_lon)))

            if time_diff <= 2.0 and pos_diff <= 0.1:  # close
                if time_diff <= 0.1 and pos_diff <= 0.01:  # very close, so same origin
                    print('same origin', id)
                    # don't change origin information
                else:
                    # new origin entry, but same event
                    ori = origin30(lat=float(eqlocl_lat),
                                   lon=float(eqlocl_lon),
                                   time=arrival_epoch,  # shouldn't use arrival seconds? then use seconds of eqlocl
                                   orid=orid,  # next largest orid in origin table
                                   evid=closest_origin.evid,
                                   jdate=julday(eq_date),

                                   # ndp=,
                                   # grn=,
                                   # srn=,
                                   # etype=,
                                   # depdp=,
                                   # algorithm=,
                                   # auth=,
                                   # commid=,
                                   # lddate=
                                   )


                    # origin.auth
                    auth = list("              ")
                    if getval(eqlocl, 'source') is not None:
                        auth[0:3] = getval(eqlocl, 'source')

                    # revision might be spelled as 'revison'
                    if 'revision' in eqlocl and getval(eqlocl['revision'], 'year') is not None:
                        year = getval(eqlocl['revision'], 'year')  # get '016' from 2016
                    elif 'revison' in eqlocl and getval(eqlocl['revison'], 'year') is not None:
                         year = getval(eqlocl['revison'], 'year')  # get '016' from 2016
                    auth[4:7] = year[1:4]

                    if 'revision' in eqlocl and getval(eqlocl['revision'], 'month') is not None:
                        month = getval(eqlocl['revision'], 'month')
                    elif 'revison' in eqlocl and getval(eqlocl['revison'], 'month') is not None:
                        month = getval(eqlocl['revison'], 'month')

                    if 'revision' in eqlocl and getval(eqlocl['revision'], 'day') is not None:
                        day = getval(eqlocl['revision'], 'day')
                    elif 'revison' in eqlocl and getval(eqlocl['revison'], 'day') is not None:
                        day = getval(eqlocl['revison'], 'day')

                    day_of_year = datetime(year=int(year.strip()),
                                           month=int(month.strip()),
                                           day=int(day.strip())).timetuple().tm_yday
                    auth[7:10] = str(day_of_year)

                    if getval(eqlocl, 'username') is not None:
                        auth[12:14] = getval(eqlocl, 'username')

                    ori.auth = ''.join(auth)

                    # origin.algorithm
                    algorithm = "EQLOCL"
                    if getval(eqlocl, 'currentModel') is not None:
                        algorithm += " " + getval(eqlocl, 'currentModel')
                    ori.algorithm = algorithm

                    # origin.depth
                    if getval(eqlocl, 'depth') is not None:
                        ori.depth = float(getval(eqlocl, 'depth'))

                    # origin.dtype
                    if getval(eqlocl, 'depthcode') is not None:
                        ori.dtype = getval(eqlocl, 'depthcode')

                    # origin.ml, origin.mb, origin.ms
                    if 'preferredMagnitude' in eqlocl and \
                            'type' in eqlocl['preferredMagnitude'] and \
                            'value' in eqlocl['preferredMagnitude']:
                        mag_type = getval(eqlocl['preferredMagnitude'], 'type')
                        mag_value = float(getval(eqlocl['preferredMagnitude'], 'value'))

                        if mag_type == 'ML':
                            ori.ml = mag_value
                            ori.mlid = mlid
                            mlid += 1
                        elif mag_type == 'MB':
                            ori.mb = mag_value
                            ori.mbid = mbid
                            mbid += 1
                        elif mag_type == 'MS' or mag_type == 'MW':
                            ori.ms = mag_value
                            ori.msid = msid
                            msid += 1


                    if getval(eqlocl, 'NumTriggers') is not None:
                        ori.nass = int(getval(eqlocl, 'NumTriggers'))

                    if getval(eqlocl, 'NumUndeferredTriggers') is not None:
                        ori.ndef = int(getval(eqlocl, 'NumUndeferredTriggers'))

                    logging.info('adding new origin from arrival in ' + filename + '\n' +
                                 ori.create_css_string())

                    orid += 1

                # Insert new parameters for origerr, arrival, assoc, remark, netmag tables
                # do a check to see if parameters empty in tables: fill in with new data (preserve old data)

if __name__ == '__main__':
    main()

# print json.dumps(eqlocl, indent=4)
#
