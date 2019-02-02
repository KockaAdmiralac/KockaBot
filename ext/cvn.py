from aiohttp import ClientSession as HTTP
from discord import File
from ext import Extension as Super
from tempfile import NamedTemporaryFile
from threading import Thread
import asyncio
import load

class Extension(Super):
    def __init__(self, bot, config):
        super(Extension, self).__init__(bot, config)
        self.data = load.load_data('cvn')
        self.register_commands('links', 'cancelprocess')
        self.confirm = False
        self.loop = asyncio.new_event_loop()
        self.namespaces = list(range(0, 16)) + [110, 111, 502, 503, 828, 1201, 2001]

    async def command_cancelprocess(self, message, params):
        if self.confirm:
            self.confirm = False
            await self.reply(message, 'The process has been cancelled.')
        else:
            await self.reply(message, 'There was no process scheduled.')

    async def command_links(self, message, params):
        if len(params) == 0:
            await self.reply(message, 'No wiki provided!')
            return
        wiki = params[0]
        if self.confirm:
            self.api = 'http://%s.wikia.com/api.php' % wiki
            self.start_process(self.links_process(wiki, message))
        else:
            await self.reply(message, 'This command is going to search for links on <http://%s.wikia.com>. Enter the command again to confirm or `!cancelprocess` to cancel.' % params[0], True)
        self.confirm = not self.confirm

    async def links_process(self, wiki, message):
        async with HTTP(loop=self.loop) as session:
            self.session = session
            self.titlelen = None
            self.titles = []
            self.bot.loop.create_task(self.update_links(message))
            await self.links_allpages()
            self.titlelen = len(self.titles)
            self.lock = asyncio.Lock()
            self.links = []
            self.task = await self.links_extlinks()
            while self.task:
                self.task = await self.task
            try:
                file = NamedTemporaryFile('wb', delete=False)
                filename = file.name
                file.write('\n'.join(self.links).encode('utf-8'))
                file.close()
                file = open(filename, 'rb')
                self.bot.loop.create_task(self.send_file(file, message.channel, 'links-%s.txt' % wiki))
            except:
                file.close()

    async def links_allpages(self, ns=0, apfrom=None):
        apfrom = apfrom or ''
        res = await self.http(self.api, {
            'action': 'query',
            'list': 'allpages',
            'aplimit': 'max',
            'apnamespace': self.namespaces[ns],
            'apfrom': apfrom,
            'apfilterredir': 'nonredirects',
            'format': 'json'
        })
        if res and ('query' in res):
            self.titles += map((lambda p: p['title']), res['query']['allpages'])
            if 'query-continue' in res:
                await self.links_allpages(ns, res['query-continue']['allpages']['apfrom'])
            elif len(self.namespaces) != ns + 1:
                await self.links_allpages(ns + 1)

    async def links_extlinks(self, eloffset=None, titles=None):
        eloffset = eloffset or 0
        if not titles:
            async with self.lock:
                titles = self.titles[:50]
                del self.titles[:50]
        if len(titles) == 0:
            return
        res = await self.http(self.api, {
            'action': 'query',
            'prop': 'extlinks',
            'ellimit': 'max',
            'eloffset': eloffset,
            'titles': '|'.join(titles),
            'format': 'json'
        })
        if res and ('query' in res) and ('pages' in res['query']):
            for k, p in res['query']['pages'].items():
                if 'extlinks' in p:
                    links = map(lambda a: a['*'], p['extlinks'])
                    self.links += links
            if 'query-continue' in res:
                return self.links_extlinks(res['query-continue']['extlinks']['eloffset'], titles)
        return self.links_extlinks()

    async def update_links(self, invocation, message=None):
        if not message:
            message = await invocation.channel.send('Initializing...')
        await asyncio.sleep(5)
        if self.titlelen == None:
            await message.edit(content='**Stage #1:** *Fetching titles...*\n%d titles fetched' % len(self.titles))
        elif len(self.titles) != 0:
            await message.edit(content='**Stage #2:** *Fetching links...*\n%d/%d titles left to check, %d links found' % (len(self.titles), self.titlelen, len(self.links)))
        else:
            await message.delete()
            await self.reply(invocation, 'Links fetched, uploading file...', True)
            return
        await self.update_links(invocation, message)

    async def send_file(self, file, channel, filename):
        await channel.send(file=File(file, filename=filename))
        file.close()

    async def http(self, url, params):
        async with self.session.get(url, params=params) as response:
            return await response.json()

    def start_process(self, generator):
        self.thread = Thread(target=self.thread_main, args=(generator,))
        self.thread.start()

    def thread_main(self, generator):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(generator)
