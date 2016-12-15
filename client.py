from discord import Client
from errors import ConfigurationError
import asyncio

class Bot(Client):
    def initialize(self, config):
        self.config = config
        if(config['token']):
            self.run(config['token'])
        elif(config.user and config.password):
            self.run(config['user'], config['password'])
        else:
            raise ConfigurationError('Login credentials not supplied')

    async def on_ready(self):
        print('Running on %s account' % self.user.name)

    async def on_message(self, message):
        # TODO: Implement
        pass
