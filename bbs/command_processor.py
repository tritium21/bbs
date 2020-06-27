import shlex

from colorama import Fore, Back, Style

from bbs.chat import get_chat

class Exit(BaseException):
    pass

class BaseProcessor:
    def __init__(self, user, reader, writer, prompt='>>> '):
        self._user = user
        self._reader = reader
        self._writer = writer
        self._prompt = prompt
    
    async def allowed(self):
        return True

    def prompt(self, prompt=None):
        if prompt is None:
            prompt = self._prompt
        self._writer.write(prompt)

    def writeline(self, line=''):
        line = line.rstrip('\r\n')
        self._writer.write(line)
        self._writer.write('\r\n')

    def parseline(self, line):
        line = line.strip()
        cmd, _, args = line.partition(' ')
        return cmd.strip().lower(), shlex.split(args.strip())

    async def default(self, *args):
        return "Unknown command."

    async def dispatch(self, line):
        cmd, args = self.parseline(line)
        func = getattr(self, f'do_{cmd}', self.default)
        return await func(*args)

    async def do_help(self, *args):
        """
        Print this help
        """
        commands = [
            (c[3:], getattr(self, c).__doc__.strip())
            for c in dir(self.__class__)
            if c.startswith('do_')
        ]
        body = '\r\n'.join(
            f"  {cmd:<12} {doc}"
            for cmd, doc
            in commands
        )
        return (f"{Fore.BLUE}Available Commands:\r\n{body}{Style.RESET_ALL}")

    async def do_exit(self, *args):
        """
        Exit this menu
        """
        raise Exit

    async def process(self):
        if not await self.allowed():
            return 'You do not have permission to use this feature'
        self.writeline(await self.do_help())
        while True:
            self.prompt()
            line = await self._reader.readline()
            if line is self._reader.BREAK:
                break
            self.writeline()
            line = line.strip('\r\n')
            try:
                self.writeline(
                    await self.dispatch(line)
                )
            except Exit:
                break
        return 'Goodbye.'

class MainProcessor(BaseProcessor):
    async def do_chat(self, *args):
        """
        Enter text chat
        """
        return await get_chat().connect(self._user, self._reader, self._writer)

    async def do_admin(self, *args):
        """
        Enter admin console
        """
        return await AdminProcessor(self._user, self._reader, self._writer).process()

class AdminProcessor(BaseProcessor):
    async def allowed(self):
        return self._user.is_admin

    async def do_admin_stuff(self, *args):
        """
        Do something admin-like, that hasn't been made yet
        """
        return "NOT IMPLEMENTED"