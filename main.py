from client import Bot
from load import configs, extensions
import asyncio

bots = []
loop = asyncio.get_event_loop()

for c in configs:
    if('extensions' in c):
        bot = Bot(loop=loop)
        ext = c['extensions']
        newext = []
        for e in ext:
            newext.append(extensions[e](bot, ext[e]))
        c['extensions'] = newext
        bots.append(bot)
        loop.create_task(bot.initialize(c))

try:
    loop.run_forever()
except KeyboardInterrupt:
    print('Detected interrupt, exiting')
    for bot in bots:
        print('Logging out %s' % bot.user.name)
        loop.run_until_complete(bot.logout())
finally:
    loop.close()
