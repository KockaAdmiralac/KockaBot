from client import Bot
from load import configs, extensions

bots = []

for c in configs:
    if('extensions' in c):
        bot = Bot()
        ext = c['extensions']
        newext = []
        for e in ext:
            newext.append(extensions[e](bot, ext[e]))
        c['extensions'] = newext
        bots.append(bot)
        bot.initialize(c)
