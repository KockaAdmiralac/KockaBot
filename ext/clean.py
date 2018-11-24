from ext import Extension as Super
import load

class Extension(Super):
    def __init__(self, bot, config):
        super(Extension, self).__init__(bot, config)
        self.data = load.load_data('clean')
        self.register_commands('clean', 'setclean')
        self.cache = {}

    async def command_clean(self, message, params):
        channel = message.channel
        msg = None
        if len(params) == 0:
            cid = str(channel.id)
            if cid in self.data:
                msg = self.data[cid]
        else:
            msg = int(params[0])
        if msg:
            if msg in self.cache:
                msg = self.cache[msg]
            else:
                msg = await channel.get_message(msg)
                if msg:
                    self.cache[msg.id] = msg
                else:
                    await self.reply(message, 'Unknown message ID', True)
                    return
            await channel.purge(after=msg)
            await self.reply(message, 'Channel cleaned!', True)
        else:
            await self.reply(message, 'Could you specify the message ID of the message you want to delete?', True)

    async def command_setclean(self, message, params):
        if len(params) == 0:
            await self.reply(message, 'No message ID specified!', True)
        else:
            self.data[str(message.channel.id)] = int(params[0])
            load.write_data('clean', self.data)
            await self.reply(message, 'Message ID set!', True)
