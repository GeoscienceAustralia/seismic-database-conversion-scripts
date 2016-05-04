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


def mk_float(s):
    if s is not None:
        s = s.strip()
        if len(s) > 0:
            return float(s)
    return None


def mk_int(s):
    if s is not None:
        s = s.strip()
        if len(s) > 0:
            return int(s)
    return None


def get_epoch(dt):
    return (dt - datetime(1970, 1, 1)).total_seconds()


def load_db(file, dbtype, method_str):
    """
    Parses each line in file by processing it through a method of the dtype object

    :param file: which file to parse
    :param dbtype: the class for the data type
    :param method_str: the method (from the data type class) to use for parsing
    :return: an array of objects from the dtype class, with data parsed from each line
    """
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


class EqLocl(object):
    def __init__(self):
        self.db = {}

    def add(self, path, value):
        cols = path.split('.')
        if cols[-1].isdigit():
            self.db.setdefault(cols[0], {})
            self.db[cols[0]].setdefault(cols[2], {})
            self.db[cols[0]][cols[2]][cols[1]] = value
        else:
            self.db[path] = value

    def get(self, path):
        if path in self.db and len(self.db[path]) > 0:
            return self.db[path]
        else:
            return None

    def parse(self, filename):
        with open(filename, 'r') as eqlocl_file:
            for line in eqlocl_file:
                if line.strip():  # non-empty
                    key, value = line.split('=')

                    self.add(path=key.strip(), value=value.strip())


    def debug(self):
        print(json.dumps(self.db, indent=4))

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
        eq = EqLocl()
        eq.parse(filename)

        if len(eq.get('arrival') or 0) < 1:  # this file has no arrivals
            logging.info('no arrivals in ' + filename + ', skipping')
            continue

        try:
            # get eqlocl date
            # some eqlocl files have empty year/month/day fields. skip these files
            # purposely omit seconds field, because we want to use the arrival's seconds, not the eqlocl file's second

            eq_date = datetime(year=int(eq.get('year')),
                               month=int(eq.get('month')),
                               day=int(eq.get('day')),
                               hour=int(eq.get('hour')),
                               minute=int(eq.get('minute')))
        except:
            logging.info('cannot parse  invalid date in ' + filename + ', skipping')
            continue

        for id in eq.db['arrival']:

            # arrival time is: eqlocl time (excluding its seconds) + arrival second (and fractional second)
            arrival = eq.db['arrival'][id]
            arrival_seconds, arrival_frac_secs = arrival['time'].split('.')
            arrival_offset = timedelta(seconds=int(arrival_seconds),
                                       microseconds=int(arrival_frac_secs))
            arrival_epoch = get_epoch(eq_date + arrival_offset)

            # find the origin with the closest time to this arrival
            # that is, find the origin with the smallest difference in time from the arrival time
            closest_origin = min(origins, key=lambda origin: abs(origin.time - arrival_epoch))

            # how close in time is the arrival to the origin time
            time_diff = abs(closest_origin.time - arrival_epoch)

            # make Eqlocl lat & lon same precision as CSS3.0
            eqlocl_lat = "%9.4f" % float(eq.db['latitude'].strip())
            eqlocl_lon = "%9.4f" % float(eq.db['longitude'].strip())

            # how close together is the lat/long between the origin and arrival
            pos_diff = abs(vincenty((float(closest_origin.lat), float(closest_origin.lon)), (eqlocl_lat, eqlocl_lon)))

            if time_diff <= 2.0 and pos_diff <= 0.1:  # close
                if time_diff <= 0.1 and pos_diff <= 0.01:  # very close, so same origin
                    # don't change origin information
                    logging.info('found same origin ' + str(closest_origin.orid) + ' in ' + filename)

                    # store origin id of closest match for use in further .origerr, .netmag, etc. tables
                    originid = closest_origin.orid

                else:  # new origin entry, but same event

                    year = eq.get('revision.year') or eq.get('revison.year')
                    month = eq.get('revision.month') or eq.get('revison.month')
                    day = eq.get('revision.day') or eq.get('revison.day')
                    day_of_year = datetime(year=int(year.strip()),
                                           month=int(month.strip()),
                                           day=int(day.strip())).timetuple().tm_yday

                    ori = origin30(lat=float(eqlocl_lat),
                                   lon=float(eqlocl_lon),
                                   time=arrival_epoch,  # shouldn't use arrival seconds? then use seconds of eqlocl
                                   orid=orid,  # next largest orid in origin table
                                   evid=closest_origin.evid,
                                   jdate=julday(eq_date),
                                   commid=originid,
                                   depth=mk_float(eq.get('depth')),
                                   dtype=eq.get('depthcode'),
                                   nass=mk_int(eq.get('NumTriggers')),
                                   ndef=mk_int(eq.get('NumUndeferredTriggers')),
                                   auth='{0}  {1}{2}   {3}'.format((eq.get('source') or '   '), year[1:4],
                                                                   str(day_of_year)[0:4],
                                                                   eq.get('username')[0:4]),
                                   algorithm="EQLOCL " + eq.get('currentModel') or ''
                                   )

                    mag_type = eq.get('preferredMagnitude.type')
                    mag_value = float(eq.get('preferredMagnitude.value'))

                    if mag_type and mag_value:
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

                    logging.info('Adding new origin from arrival in ' + filename + '\n' +
                                 ori.create_css_string())

                    origins.append(ori)

                    originid = orid  # store last origin id for use in .origerr, .netmag, etc. tables
                    orid += 1

                # Insert new parameters for origerr, arrival, assoc, remark, netmag tables

                code = eq.get('accuracyCode')
                oer = origerr30(orid=originid,  # either last orid, or closest 'same' origin id
                                stime=float(eq.get('uncertainty.time')),
                                sminax=float(eq.get('uncertainty.east')),
                                smajax=float(eq.get('uncertainty.north')),
                                strike=float(eq.get('uncertainty.depth')),
                                conf=accuracy_codes[code.lower()] if code and code.lower() in accuracy_codes else None,
                                sdobs=mk_float(eq.get('standardDeviation'))
                                )

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
                rem = remark30(commid=originid,
                               remark=(eq.get('nearestPlace.name') or '') +
                                      (eq.get('nearestPlace.state') or '') or None)

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

        # eq.debug()

    # write out all the newly associated files (with additions & modifications)
    origin_out.write(''.join(map(lambda o: o.create_css_string(), origins)))
    origerr_out.write(''.join(map(lambda o: o.create_css_string(), origerrs)))
    remark_out.write(''.join(map(lambda o: o.create_css_string(), remarks)))

if __name__ == '__main__':
    main()


# print json.dumps(eqlocl, indent=4)
#
