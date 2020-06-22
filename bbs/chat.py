import asyncio

from colorama import Fore, Back, Style

class Chat:
    def __init__(self):
        self._users = {}

    def names(self):
        return list(user.username for user in self._users.keys())

    async def send(self, message):
        for recipient, client in self._users.items():
            await client.recv(message)

    async def connect(self, user, reader, writer):
        if not user.can_chat and not user.is_admin:
            return 'You are banned from chat.'
        await self.system_message(f"{user.username} has joined chat")
        self._users[user] = client = ChatClient(self, user, reader, writer)
        await client.chat()
        self._users.pop(user)
        await self.system_message(f"{user.username} has left chat")
        return 'Goodbye.'

    async def system_message(self, message):
        await self.send(f"{Fore.RED}{Style.DIM}*** {message}{Style.RESET_ALL}")

class ChatClient:
    def __init__(self, server, user, reader, writer):
        self.server = server
        self.user = user
        self.reader = reader
        self.writer = writer
    
    async def chat(self):
        prompt = 'chat> '
        self.writer.write(prompt)
        while True:
            line = await self.reader.readline()
            if line is self.reader.BREAK:
                break
            line = line.rstrip()
            if line.startswith('/exit'):
                self.writer.write('\r\n')
                break
            elif line.startswith('/me '):
                _, _, remainder = line.partition(' ')
                line = f"{Fore.GREEN}{Style.DIM}* {self.user.username} {remainder}{Style.RESET_ALL}"
            elif line.startswith('/admin '):
                if self.user.is_admin:
                    _, _, remainder = line.partition(' ')
                    await self.server.system_message(remainder)
                else:
                    await self.print_error("You do not have permission for that command")
                line = ''
            elif line.startswith('/names'):
                names = self.server.names()
                await self.print_info("Users currently in chat:")
                for name in names:
                    await self.print_info(f"  {name}")
                line = ''
            elif line.strip():
                line = f"<{self.user.username}> {line}"
            if line.strip():
                await self.send(line)
            self.writer.write('\r\x1b[2K' + prompt)

    async def print_error(self, message):
        await self.print(f"{Fore.RED}{Style.DIM}!!! {message}{Style.RESET_ALL}")

    async def print_info(self, message):
        await self.print(f"{Fore.BLUE}** {message}{Style.RESET_ALL}")

    async def send(self, message):
        await self.server.send(message)

    async def print(self, message):
        self.writer.write(f'\x1b7\n\x1b[1A\x1b[1L{message}\x1b8')

    async def recv(self, message):
        await self.print(message)



_chat = Chat()
def get_chat():
    return _chat