import asyncio

class Chat:
    def __init__(self):
        self._users = {}

    async def send(self, user, message):
        for recipient, client in self._users.items():
            if recipient == user:
                continue
            await client.send(f"<{user.username}> {message}\r\n")

    async def connect(self, user, reader, writer):
        if not user.can_chat and not user.is_admin:
            return 'You are banned from chat.'
        self._users[user] = client = ChatClient(self, user, reader, writer)
        await client.chat()
        self._users.pop(user)
        return ''

class ChatClient:
    def __init__(self, server, user, reader, writer):
        self._server = server
        self._user = user
        self._reader = reader
        self._writer = writer
    
    async def chat(self):
        prompt = 'chat> '
        self._writer.write(prompt)
        while True:
            line = await self._reader.readline()
            if line is self._reader.BREAK:
                break
            line = line.rstrip()
            if line == '/exit':
                self._writer.write('\r\n')
                break
            elif line:
                await self._server.send(self._user, line)
                await self.send(f'<{self._user.username}> {line}')
            self._writer.write('\r\x1b[2K' + prompt)

    async def send(self, message):
        row, col = await self._reader.get_position()
        self._writer.write(f'\x1b7\n\x1b[1A\x1b[1L{message}\x1b8')


_chat = Chat()
def get_chat():
    return _chat