from discord import Client, Game
from errors import ConfigurationError
import asyncio

USE_ALL = 0
USE_MASTER = 1
USE_NONE = 2

class Bot(Client):
    def initialize(self, config):
        self.config = config
        self.prefix = config.get('prefix', '!')
        self.separator = config.get('separator', ' ')
        self.extensions = config.get('extensions')
        self.use = config.get('use', USE_MASTER)
        if('token' in config):
            self.run(config['token'])
        elif('user' in config and 'password' in config):
            self.run(config['user'], config['password'])
        else:
            raise ConfigurationError('Login credentials not supplied')

    async def on_ready(self):
        self.master = self.config.get('master', (await self.application_info()).owner)
        print('Running on %s account' % self.user.name)
        if('game' in self.config):
            conf = self.config['game']
            await self.change_presence(game=Game(name=conf['name'], type=int(conf.get('streaming', 0))))

    async def on_message(self, message):
        if(
            self.use == USE_NONE or (
                self.use == USE_MASTER and
                message.author.id == self.master.id
            ) or
            not message.content.startswith(self.prefix)
        ):
            arr = message.content[len(self.prefix):].split(self.separator)
            command = arr[0]
            params = arr[1:]
            for e in self.extensions:
                await e.call_command(message, command, params)
        pass
