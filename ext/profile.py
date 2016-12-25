from discord import Role
from ext import Extension as Super
from urllib.parse import quote
import load
import re
import requests

class Extension(Super):
    def __init__(self, bot, config):
        super(Extension, self).__init__(bot, config)
        self.data = load.load_data('profile')
        self.register_commands('profile', 'verify')
        self.mention_regex = re.compile('<@!?(\d+)>')
        self.domain = config.get('domain', 'ut')
        self.initialized = False

    def user_profile(self, user):
        return '<http://%s.wikia.com/wiki/Special:Contribs/%s>' % (self.domain, quote(user))

    async def command_profile(self, message, params):
        key = self.mention_regex.findall(params[0])[0]
        if key in self.data:
            await self.reply(message, 'User profile: %s' % self.user_profile(self.data[key]), False, False)
        else:
            await self.reply(message, 'User profile for %s not found' % params[0])

    def initialize(self):
        if(self.initialized):
            pass
        self.bind_channel = self.bot.get_channel(self.config['bind_channel'])
        self.clear_channel = self.bot.get_channel(self.config['clear_channel'])
        self.role = [r for r in self.bind_channel.server.roles if r.id == self.config['role']][0]
        self.initialized = True

    async def command_verify(self, message, params):
        self.initialize()
        # Check permissions
        if message.channel != self.bind_channel:
            pass
        # Parsing parameters
        id = self.mention_regex.findall(params[0])[0]
        user = self.join_params(params[1:])
        # Adding to database
        self.data[id] = user
        load.write_data('profile', self.data)
        # Give role to the person
        await self.bot.add_roles(message.server.get_member(id), self.role)
        # Posting to webhook
        requests.post('https://discordapp.com/api/webhooks/%s/%s' % (self.config['webhook_id'], self.config['webhook_token']), json={ 'content': '<@!%s> - [%s](%s)' % (id, user, self.user_profile(user)) })
        # Clearing the channel
        msg = await self.bot.get_message(self.clear_channel, self.config['welcome_msg'])
        delete = await self.bot.purge_from(self.clear_channel, after=msg)
        # Responding
        await self.reply(message, 'Added %s to database!' % params[0], True)

    async def on_member_create(self, member):
        self.initialize()
        if(member.id in self.data):
            await self.bot.add_roles(member, self.role)
        else:
            await self.bot.send_message(self.clear_channel, self.config['welcome'] % member.mention)
