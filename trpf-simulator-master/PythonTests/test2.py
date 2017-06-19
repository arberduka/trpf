import shlex, os

properties = {
'routes': {},
'thresholds': []
}

properties['routes'] = {trip: [] for trip in range(10)}
print(properties['routes'])
properties['thresholds'] = [None for trip in range(10)]
properties['thresholds'].append('Overall')
print(properties['thresholds'])
