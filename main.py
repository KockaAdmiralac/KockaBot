from client import Bot
from load import configs, extensions

bots = []

for c in configs:
    if('extensions' in c):
        ext = c['extensions']
        newext = []
        for e in ext:
            newext.append(extensions[e](ext[e]))
        c['extensions'] = newext
        bot = Bot()
        bots.append(Bot())
        bot.initialize(c)
