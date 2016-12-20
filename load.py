import json
import os
import sys
import importlib

sys.path.insert(1, 'ext')

def load_json(filename):
    f = open(filename)
    c = ''
    s = f.read()
    while(s != ''):
        c += s
        s = f.read()
    return json.loads(c)

def load_directory(dir):
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]

def load_data(file):
    try:
        return load_json('data/%s.json' % file)
    except FileNotFoundError:
        write_data(file, {})
        return {}

def write_data(file, contents):
    f = open('data/%s.json' % file, 'w')
    f.write(json.dumps(contents))
    f.close()

extensions = {}
for e in load_directory('ext'):
    e = e[:-3]
    module = importlib.import_module(e)
    extensions[e] = getattr(module, 'Extension')

configs = [load_json('config/%s' % c) for c in load_directory('config')]
