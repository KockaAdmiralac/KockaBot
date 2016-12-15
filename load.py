from ext import extensions
import json
import os

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

configs = [load_json('config/%s' % c) for c in load_directory('config')]
