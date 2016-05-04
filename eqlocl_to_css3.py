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
from css_types import origin30, origerr30, netmag30, remark30
from geopy.distance import vincenty
import logging
import sys

logging.basicConfig(stream=sys.stdout, filename='log.txt', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

GAED_ORIGIN_FILE = 'out.origin'
GAED_NETMAG_FILE = 'out.netmag'
GAED_ORIGERR_FILE = 'out.origerr'
GAED_REMARK_FILE = 'out.remark'

ORIGIN_OUT = 'eqlocl.origin'
NETMAG_OUT = 'eqlocl.netmag'
ORIGERR_OUT = 'eqlocl.origerr'
REMARK_OUT = 'eqlocl.remark'

# the root directory to start searching for eqlocl files
EQLOCL_ROOT = 'sample_data/'

# will traverse directories and parse only text files starting with GA, agso, ASC or MUN
# (to avoid parsing random files)
FILE_NAME_PATTERN = '/**/[GA|agso|ASC|MUN]*.txt'

accuracy_codes = {'a': 0.95, 'b': 0.8, 'c': 0.7, 'd': 0.6, 'e': 0.5}

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


def load_db(file, dbtype, method_str):
    db = []
    with open(file, 'r') as db_in:
        for line in db_in:
            obj = dbtype()
            method = getattr(obj, method_str)
            method(line)
            db.append(obj)

    return db


def fill_empty(new=None,
               old=None,
               empty_ref=None,
               key=None):
    """
    goes through each property in object and compares it with an empty object as reference
    if the property is the same, it must be empty
    if the new object has a different property value, then it must not be empty so use it

    :param new: the new object taken from eqlocl data
    :param old: existing object from GAED
    :param empty_ref: an empty CSS3 object initialised with default values (e.g., orid=-1)
    :param key: the key name (e.g., commid, orid)
    :return: tuple of old object with changed values, and modifications made
    """
    modified = ''
    if getattr(old, key) == getattr(new, key):  # only do if same record
        for attr, value in old.__dict__.iteritems():
            if value == getattr(empty_ref, attr) \
                    and getattr(new, attr) != getattr(empty_ref, attr):  # old empty, new one isn't
                setattr(old, attr, getattr(new, attr))

                # add message for each change made
                modified += attr + ' from ' + str(value) + ' to ' + \
                            str(getattr(new, attr)) + ', '

    return old, modified


def main():
    # load GAED
    origins = load_db(GAED_ORIGIN_FILE, origin30, 'from_string')
    origerrs = load_db(GAED_ORIGERR_FILE, origerr30, 'from_string')
    netmags = load_db(GAED_NETMAG_FILE, netmag30, 'from_string')
    remarks = load_db(GAED_REMARK_FILE, remark30, 'from_string')

    origin_out = file(ORIGIN_OUT, 'w')
    origerr_out = file(ORIGERR_OUT, 'w')
    netmag_out = file(NETMAG_OUT, 'w')
    remark_out = file(REMARK_OUT, 'w')

    # used for its default values for comparison
    emptyoer = origerr30()

    # set ids to ones after the last largest, will increment when inserting new entries
    originid = orid = max(origins, key=lambda origin: origin.orid).orid + 1
    mlid = max(origins, key=lambda origin: origin.mlid).mlid + 1
    mbid = max(origins, key=lambda origin: origin.mbid).mbid + 1
    msid = max(origins, key=lambda origin: origin.msid).msid + 1

    # go through each file in EQLOCL path that matches the file name pattern (e.g., contains 'MUN' and ends in '.txt')
    for filename in glob.glob(EQLOCL_ROOT + FILE_NAME_PATTERN):
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

            # if time_diff <= 200 and pos_diff <= 200:  # close
            if time_diff <= 2.0 and pos_diff <= 0.1:  # close
                # if time_diff <= 200 and pos_diff <= 200:  # very close, so same origin
                if time_diff <= 0.1 and pos_diff <= 0.01:  # very close, so same origin
                    # don't change origin information
                    logging.info('found same origin ' + str(closest_origin.orid) + ' in ' + filename)

                    # store origin id of closest match for use in further .origerr, .netmag, etc. tables
                    originid = closest_origin.orid

                else:
                    # new origin entry, but same event
                    ori = origin30(lat=float(eqlocl_lat),
                                   lon=float(eqlocl_lon),
                                   time=arrival_epoch,  # shouldn't use arrival seconds? then use seconds of eqlocl
                                   orid=orid,  # next largest orid in origin table
                                   evid=closest_origin.evid,
                                   jdate=julday(eq_date),
                                   commid=originid,

                                   # ndp=,
                                   # grn=,
                                   # srn=,
                                   # etype=,
                                   # depdp=,
                                   # algorithm=,
                                   # auth=,
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

                    # auth should now be 'SRC YYYDOY'
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

                    # origin.nass
                    if getval(eqlocl, 'NumTriggers') is not None:
                        ori.nass = int(getval(eqlocl, 'NumTriggers'))

                    # origin.ndef
                    if getval(eqlocl, 'NumUndeferredTriggers') is not None:
                        ori.ndef = int(getval(eqlocl, 'NumUndeferredTriggers'))

                    logging.info('Adding new origin from arrival in ' + filename + '\n' +
                                 ori.create_css_string())

                    origins.append(ori)

                    originid = orid  # store last origin id for use in .origerr, .netmag, etc. tables
                    orid += 1

                # Insert new parameters for origerr, arrival, assoc, remark, netmag tables
                oer = origerr30(orid=originid,  # either last orid, or closest 'same' origin id
                                stime=float(getval(eqlocl['uncertainty'], 'time')),
                                sminax=float(getval(eqlocl['uncertainty'], 'east')),
                                smajax=float(getval(eqlocl['uncertainty'], 'north')),
                                strike=float(getval(eqlocl['uncertainty'], 'depth')),
                                )

                # origerr.conf
                if getval(eqlocl, 'accuracyCode') is not None:
                    code = getval(eqlocl, 'accuracyCode').lower()
                    if code in accuracy_codes:
                        oer.conf = accuracy_codes[code]

                # origerr.sdobs
                if getval(eqlocl, 'standardDeviation') is not None:
                    oer.sdobs = float(getval(eqlocl, 'standardDeviation'))

                if originid > len(origerrs):  # new record
                    origerrs.append(oer)
                    logging.info('Adding new origerr ' + str(oer.orid) + oer.create_css_string())
                else:
                    # fill in old record with new data (preserve old non-empty data)
                    origerrs[originid - 1], modified = fill_empty(old=origerrs[originid - 1],
                                                                  new=oer,
                                                                  empty_ref=origerr30(),
                                                                  key='orid')
                    if modified:
                        logging.info('Modified origerr orid=' + str(originid) + ': ' + modified)

                # remark.remark
                rem = remark30(commid=originid)
                remark = ''

                if 'nearestPlace' in eqlocl:
                    if getval(eqlocl['nearestPlace'], 'name') is not None:
                        remark = getval(eqlocl['nearestPlace'], 'name')

                    if getval(eqlocl['nearestPlace'], 'state') is not None:
                        remark[:-1] = getval(eqlocl['nearestPlace'], 'state')

                if originid > len(remarks):
                    remarks.append(rem)
                    logging.info('Adding new remark' + str(rem.commid) + rem.create_css_string())
                else:
                    remarks[originid - 1], modified = fill_empty(old=remarks[originid - 1],
                                                                 new=rem,
                                                                 empty_ref=remark30(),
                                                                 key='commid')
                    if modified:
                        logging.info('Modified remark commid=' + str(originid) + ': ' + modified)

    # write out all the newly associated files (with additions & modifications)
    origin_out.write(''.join(map(lambda o: o.create_css_string(), origins)))
    origerr_out.write(''.join(map(lambda o: o.create_css_string(), origerrs)))
    remark_out.write(''.join(map(lambda o: o.create_css_string(), remarks)))

if __name__ == '__main__':
    main()

# print json.dumps(eqlocl, indent=4)
#
