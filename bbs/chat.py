import asyncio

from colorama import Fore, Back, Style

class Chat:
    def __init__(self):
        self._users = {}

    async def send(self, user, message):
        for recipient, client in self._users.items():
            await client.recv(user, message)

    async def connect(self, user, reader, writer):
        if not user.can_chat and not user.is_admin:
            return 'You are banned from chat.'
        await self.send(
            user,
            f"{Fore.RED}{Style.DIM}*** {user.username} has joined chat{Style.RESET_ALL}"
        )
        self._users[user] = client = ChatClient(self, user, reader, writer)
        await client.chat()
        self._users.pop(user)
        await self.send(
            user,
            f"{Fore.RED}{Style.DIM}*** {user.username} has left chat{Style.RESET_ALL}"
        )
        return 'Goodbye.'

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
            if line.startswith('/exit'):
                self._writer.write('\r\n')
                break
            elif line.startswith('/me '):
                _, _, remainder = line.partition(' ')
                line = f"{Fore.GREEN}{Style.DIM}* {self._user.username} {remainder}{Style.RESET_ALL}"
            else:
                line = f"<{self._user.username}> {line}"
            if line:
                await self.send(line)
            self._writer.write('\r\x1b[2K' + prompt)

    async def send(self, message):
        await self._server.send(self._user, message)

    async def print(self, message):
        self._writer.write(f'\x1b7\n\x1b[1A\x1b[1L{message}\x1b8')

    async def recv(self, user, message):
        await self.print(message)



_chat = Chat()
def get_chat():
    return _chat