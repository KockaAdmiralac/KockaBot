from ext import Extension as Super
from urllib.parse import quote
import load
import re
import requests

class Extension(Super):
    def __init__(self, bot, config):
        super(Extension, self).__init__(bot, config)
        self.data = load.load_data('profile')
        self.register_commands('profile', 'addprofile', 'clear')
        self.mention_regex = re.compile('<@!?(\d+)>')
        self.domain = config.get('domain', 'ut')

    def call_webhook(self, discord, wikia):
        if(not 'webhook' in self.config):
            pass
        conf = self.config['webhook']
        requests.post('https://discordapp.com/api/webhooks/%s/%s' % (conf['id'], conf['token']), json={ 'content': '<@!%s> - [%s](%s)' % (discord, wikia, self.user_profile(wikia)) })

    def user_profile(self, user):
        return '<http://%s.wikia.com/wiki/Special:Contribs/%s>' % (self.domain, quote(user))

    async def on_profile(self, message, params):
        key = self.mention_regex.findall(params[0])[0]
        if(key in self.data):
            await self.reply(message, 'User profile: %s' % self.user_profile(self.data[key]))
        else:
            await self.reply(message, 'User profile for %s not found' % params[0])

    async def on_addprofile(self, message, params):
        id = self.mention_regex.findall(params[0])[0]
        user = self.join_params(params[1:])
        self.data[id] = user
        await self.reply(message, 'Added %s to database!' % params[0], True)
        self.call_webhook(id, user)

    async def on_clear(self, message, params):
        if(not 'clear' in self.config):
            pass
        conf = self.config['clear']
        channel = self.bot.get_channel(conf['channel'])
        msg = await self.bot.get_message(channel, conf['id'])
        delete = await self.bot.purge_from(channel, after=msg)
        await self.reply(message, 'Messages purged!', True)
