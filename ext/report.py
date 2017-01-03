from ext import Extension as Super
import load

FLAG_REPORT = 0
FLAG_UNREPORT = 1
FLAG_RESOLVE = 2

class Extension(Super):
    def __init__(self, bot, config):
        super(Extension, self).__init__(bot, config)
        self.temp = load.load_data('report')
        self.register_commands('report', 'unreport', 'resolve')
        for t in ['tww', 'w', 's', 'p']:
            if not t in self.temp:
                if self.is_wiki_type(t):
                    self.temp[t] = []
                else:
                    self.temp[t] = {}
        self.message = False

    async def update_report(self, msg=None):
        load.write_data('report', self.temp)
        m = """__**Report message**__
This message is where new reports accumulate
"""
        if len(self.temp['tww']) > 0:
            m += '**Three word wikis**```{{{{badwiki|{0}}}}}```'.format('}}\n{{badwiki|'.join(self.temp['tww']))
        if len(self.temp['w']) > 0:
            m += '**Spam wikis**```{{{{badwiki|{0}}}}}```'.format('}}\n{{badwiki|'.join(self.temp['w']))
        if len(self.temp['s']) > 0:
            for k, v in self.temp['s'].items():
                if len(v) > 0:
                    m += """**Spam users: {0}**```
== {0} ==
{{{{Report spam|{0}|Spam|{1}|{{{{subst:REVISIONUSER}}}}|~~~~~}}}}
```""".format(k, '|'.join(v))
        if len(self.temp['p']) > 0:
            for k, v in self.temp['p'].items():
                if len(v) > 0:
                    m += """**Spam profiles: {0}**```
== {0} ==
{{{{Report profile|{0}|Spam|{1}|{{{{subst:REVISIONUSER}}}}|~~~~~}}}}
```""".format(k, '|'.join(v))
        if not self.message:
            self.message = await self.bot.send_message(self.bot.get_channel(self.config['bind_channel']), m)
        else:
            await self.bot.edit_message(self.message, new_content=m)
        if(msg):
            await self.reply(msg, 'Reports updated!', True)


    def is_wiki_type(self, t):
        return t in ['tww', 'w']

    def is_spam_type(self, t):
        return t in ['s', 'p']

    def modify_array(self, array, el, flag):
        # Python y u do dis
        def temp(array):
            del array[:]
        [
            lambda: array.append(el),
            lambda: array.remove(el),
            lambda: temp(array)
        ][flag]()

    async def base_report(self, message, params, flag):
        params.append('')
        t = params[0].lower()
        if self.is_wiki_type(t):
            self.modify_array(self.temp[t], params[1].lower(), flag)
            await self.update_report(message)
        elif self.is_spam_type(t):
            wiki = params[1].lower()
            if not wiki in self.temp[t]:
                self.temp[t][wiki] = []
            self.modify_array(self.temp[t][wiki], ' '.join(params[2:]).strip(), flag)
            await self.update_report(message)
        else:
            await self.reply(message, 'Invalid report type!', True)

    async def command_report(self, message, params):
        await self.base_report(message, params, FLAG_REPORT)

    async def command_unreport(self, message, params):
        await self.base_report(message, params, FLAG_UNREPORT)

    async def command_resolve(self, message, params):
        await self.base_report(message, params, FLAG_RESOLVE)
