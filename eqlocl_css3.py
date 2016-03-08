#!/usr/bin/env python

import json

import pisces.schema.css3 as css3

class Event(css3.Event):
    __tablename__ = 'event'

def add(t, path, value):
    """
    convert line to nested dictionary entries.
        e.g., "arrival.sitename.1 = WR1" to { "arrival": { "sitename": { "1": { "value": "WR1" } } } }

    :param t: dictionary
    :param path: list of the name of the variable, e.g., ['magnitude', 'sitename', '0'] or ['version']
    :param value: the variable value
    :return:
    """
    for node in path:
        key = node.strip()
        t.setdefault(key, {})
        t = t[key]

    t['value'] = value

# load and parse eqlocl file
eqlocl = {}
with open('Eqlocl.txt', 'rb') as eqlocl_file:
    for line in eqlocl_file:
        if line.strip():  # non-empty
            key, value = line.split('=')
            add(t=eqlocl, path=key.split('.'), value=value.strip())

# # open origin
# with open('out.event', 'r') as evi_in:
#     for line in evi_in:
#         event = Event.from_string(line)
#         print(event.lddate)

print json.dumps(eqlocl, sort_keys=True, indent=4)

