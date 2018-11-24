from discord import Client, Game
from errors import ConfigurationError
import asyncio

USE_ALL = 0
USE_MASTER = 1
USE_NONE = 2

class Bot(Client):
    async def initialize(self, config):
        self.config = config
        self.prefix = config.get('prefix', '!')
        self.separator = config.get('separator', ' ')
        self.extensions = config.get('extensions')
        self.selfbot = config.get('selfbot', False)
        if('token' in config):
            await self.start(config['token'])
        elif('user' in config and 'password' in config):
            await self.start(config['user'], config['password'])
        else:
            raise ConfigurationError('Login credentials not supplied')

    async def on_ready(self):
        self.master = self.config.get('master', (await self.application_info()).owner)
        print('Running on %s account' % self.user.name)
        await self.dispatch_listener('client', 'ready')
        if('game' in self.config):
            conf = self.config['game']
            await self.change_presence(status=Game(name=conf['name'], type=int(conf.get('streaming', 0)), url=conf.get('url', 'https://github.com/KockaAdmiralac/KockaBot')))

    async def on_message(self, message):
        if(
            (self.selfbot and message.author.id != self.master.id) or
            not message.content.startswith(self.prefix)
        ):
            return
        arr = message.content[len(self.prefix):].split(self.separator)
        command = arr[0]
        params = arr[1:]
        for e in self.extensions:
            await e.call_command(message, command, params)
        await self.dispatch_listener('message', 'create', message)

    async def dispatch_listener(self, controller, listener, *args):
        for e in self.extensions:
                await e.call_listener(controller, listener, args)

    # CON
    # SIS
    # TEN
    # CY

    async def on_message_delete(self, message):
        await self.dispatch_listener('message', 'delete', message)

    async def on_message_edit(self, old, new):
        await self.dispatch_listener('message', 'update', old, new)

    async def on_reaction_add(self, reaction, user):
        await self.dispatch_listener('reaction', 'create', reaction, user)

    async def on_reaction_remove(self, reaction, user):
        await self.dispatch_listener('reaction', 'delete', reaction, user)

    async def on_reaction_clear(self, message, reactions):
        await self.dispatch_listener('reaction', 'clear', message, reactions)

    async def on_channel_create(self, channel):
        await self.dispatch_listener('channel', 'create', channel)

    async def on_channel_delete(self, channel):
        await self.dispatch_listener('channel', 'delete', channel)

    async def on_channel_update(self, old, new):
        await self.dispatch_listener('channel', 'update', old, new)

    async def on_member_join(self, member):
        await self.dispatch_listener('member', 'create', member)

    async def on_member_remove(self, member):
        await self.dispatch_listener('member', 'delete', member)

    async def on_member_update(self, before, after):
        await self.dispatch_listener('member', 'update', before, after)

    async def on_server_join(self, server):
        await self.dispatch_listener('server', 'create', server)

    async def on_server_remove(self, server):
        await self.dispatch_listener('server', 'delete', server)

    async def on_server_update(self, old, new):
        await self.dispatch_listener('server', 'update', old, new)

    async def on_server_role_create(self, role):
        await self.dispatch_listener('role', 'create', role)

    async def on_server_role_delete(self, role):
        await self.dispatch_listener('role', 'delete', role)

    async def on_server_role_update(self, old, new):
        await self.dispatch_listener('role', 'update', old, new)

    async def on_server_emojis_update(self, old, new):
        await self.dispatch_listener('emoji', 'update', old, new)

    async def on_server_available(self, server):
        await self.dispatch_listener('availability', 'create', server)

    async def on_server_unavailable(self, server):
        await self.dispatch_listener('availability', 'delete', server)

    async def on_voice_state_update(self, old, new):
        await self.dispatch_listener('voice_state', 'update', old, new)

    async def on_member_ban(self, member):
        await self.dispatch_listener('ban', 'create', member)

    async def on_member_unban(self, member):
        await self.dispatch_listener('ban', 'delete', member)

    async def on_typing(self, channel, user, time):
        await self.dispatch_listener('member', 'typing', channel, user, time)

    async def on_group_join(self, channel, user):
        await self.dispatch_listener('group', 'join', channel, user)

    async def on_group_remove(self, channel, user):
        await self.dispatch_listener('group', 'leave', channel, user)
