import asyncio

class Extension(object):
    def __init__(self, bot, config):
        self.config = config
        self.bot = bot
        self.delete = config.get('delete', None)

    def register_commands(self, *commands):
        self.commands = commands

    def join_params(self, params):
        return ' '.join(params)

    async def reply(self, message, reply_with, mention=False, delete=True):
        if(mention):
            reply_with = '%s: %s' % (message.author.mention, reply_with)
        msg = await self.bot.send_message(message.channel, reply_with)
        if(delete and self.delete):
            async def delete_message():
                await asyncio.sleep(self.delete)
                await self.bot.delete_message(message)
                await self.bot.delete_message(msg)
            asyncio.ensure_future(delete_message())

    async def call_command(self, message, command, args):
        if(command in self.commands):
            await getattr(self, 'on_%s' % command)(message, args)
