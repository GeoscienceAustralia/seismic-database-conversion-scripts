#!/usr/bin/env python

import json
import glob
from datetime import datetime, timedelta
from css_types2 import origin30
from geopy.distance import vincenty

GAED_ORIGIN_FILE = 'out.origin'
EQLOCL_ROOT = 'eqlocl/'


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

# GAED
origins = []
with open(GAED_ORIGIN_FILE, 'r') as ori_in:
    for line in ori_in:
        ori = origin30()
        ori.from_string(line)
        origins.append(ori)


for filename in glob.glob(EQLOCL_ROOT + '/**/[ASC|MUN]*.txt'):
    eqlocl = {}
    with open(filename, 'rb') as eqlocl_file:
        for line in eqlocl_file:
            if line.strip():  # non-empty
                key, value = line.split('=')
                add(t=eqlocl, path=key.split('.'), v=value.strip())

    if 'time' not in eqlocl['arrival']:  # this file has no arrivals
        print('no arrivals in ' + filename + ', skipping')
        continue

    try:
        eq_date = datetime(year=int(eqlocl['year']['value']),
                        month=int(eqlocl['month']['value']),
                        day=int(eqlocl['day']['value']),
                        hour=int(eqlocl['hour']['value']),
                        minute=int(eqlocl['minute']['value']))
    except:
        print('cannot parse  invalid date in ' + filename + ', skipping')
        continue

    for id in eqlocl['arrival']['time']:
        # arrival time is: eqlocl time (excluding its seconds) + arrival second (and fractional second)
        arrival_seconds, arrival_frac_secs = eqlocl['arrival']['time'][id]['value'].split('.')  # arrival offset
        arrival_offset = timedelta(seconds=int(arrival_seconds),
                                   microseconds=int(arrival_frac_secs))
        arrival_epoch = ((eq_date + arrival_offset) - datetime(1970, 1, 1)).total_seconds()

        # find the closest origin time to this arrival
        # that is, find the origin with the smallest difference in time from the arrival time
        closest = min(origins, key=lambda origin: abs(origin.time - arrival_epoch))

        time_diff = abs(closest.time - arrival_epoch)

        # make Eqlocl lat & lon same precision as CSS3.0
        eq_lat = "%9.4f" % float(eqlocl['latitude']['value'].strip())
        eq_lon = "%9.4f" % float(eqlocl['longitude']['value'].strip())

        pos_diff = abs(vincenty((float(closest.lat), float(closest.lon)), (eq_lat, eq_lon)))

        if time_diff <= 2.0 and pos_diff <= 0.1:  # close
            if time_diff <= 0.1 and pos_diff <= 0.01:  # same origin
                print('same origin', id)
            else:
                print('new origin')

            # Insert origerr, arrival, assoc, remark, netmag tables


# print json.dumps(eqlocl, indent=4)
#
