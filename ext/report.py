from ext import Extension as Super
import load
import mwclient

FLAG_REPORT = 0
FLAG_UNREPORT = 1
FLAG_RESOLVE = 2

class Extension(Super):
    def __init__(self, bot, config):
        super(Extension, self).__init__(bot, config)
        self.temp = load.load_data('report')
        self.register_commands('report', 'unreport', 'resolve', 'kocka')
        self.mw = mwclient.Site('vstf.wikia.com', path='/')
        self.mw.login(config['username'], config['password'])
        for t in ['t', 'w', 's', 'p']:
            if not t in self.temp:
                if self.is_wiki_type(t):
                    self.temp[t] = []
                else:
                    self.temp[t] = {}
        self.message = False

    def report_message(self, t, p=''):
        return {
            't': '{{{{badwiki|{0}}}}}'.format('}}\n{{badwiki|'.join(self.temp['t'])),
            'w': '{{{{badwiki|{0}}}}}'.format('}}\n{{badwiki|'.join(self.temp['w'])),
            's': '== {0} ==\n{{{{Report spam|{0}|Spam|{1}|{{{{subst:REVISIONUSER}}}}|~~~~~}}}}'.format(p, '|'.join(self.temp['s'].get(p, []))),
            'p': '== {0} ==\n{{{{Report profile|{0}|Spam|{1}|{{{{subst:REVISIONUSER}}}}|~~~~~}}}}'.format(p, '|'.join(self.temp['p'].get(p, [])))
        }[t]

    async def update_report(self, msg=None):
        load.write_data('report', self.temp)
        m = """__**Report message**__\nThis message is where new reports accumulate\n"""
        if len(self.temp['t']) > 0:
            m += '**Three word wikis**```%s```' % self.report_message('t')
        if len(self.temp['w']) > 0:
            m += '**Spam wikis**```%s```' % self.report_message('w')
        if len(self.temp['s']) > 0:
            for k, v in self.temp['s'].items():
                if len(v) > 0:
                    m += """**Spam users: %s**```%s```""" % (k, self.report_message('s', k))
        if len(self.temp['p']) > 0:
            for k, v in self.temp['p'].items():
                if len(v) > 0:
                    m += '**Spam profiles: %s**```%s```' % (k, self.report_message('p', k))
        if not self.message:
            self.message = await self.bot.send_message(self.bot.get_channel(self.config['bind_channel']), m)
        else:
            await self.bot.edit_message(self.message, new_content=m)
        if(msg):
            await self.reply(msg, 'Reports updated!', True)


    def is_wiki_type(self, t):
        return t in ['t', 'w']

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

    async def command_kocka(self, message, params):
        if(message.author == self.bot.master):
            params.append('')
            page = self.mw.Pages['Report:' + {
                'w': 'Wiki',
                's': 'Spam',
                't': 'Three word wikis',
                'p': 'User profile headers'
            }[params[0]]]
            text = page.text()
            text += '\n' + self.report_message(params[0], params[1])
            page.save(text, summary='Adding reports')
            await self.base_report(message, params, FLAG_RESOLVE)
