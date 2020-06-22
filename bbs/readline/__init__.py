import asyncio
import contextlib

from bbs.readline.readlike import edit, keys

class Readline:
    BREAK = object()

    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer
        self._echo = True
        self._readtask = None
        self._readlock = asyncio.Lock()

    async def prompt(self, prompt):
        self.write(prompt)
        return await self.readline()

    @classmethod
    def wrap_streams(cls, reader, writer):
        inst = cls(reader, writer)
        return inst, inst

    @contextlib.contextmanager
    def no_echo(self):
        old_echo = self._echo
        self._echo = False
        yield
        self._echo = old_echo

    async def get_position(self):
        if self._readlock.locked():
            self._readtask.cancel()
        async with self._readlock:
            self._writer.write('\x1b[6n')
            resp = ''
            ch = ''
            while ch != 'R':
                ch = await self._reader.read(1)
                resp += ch
            return (
                tuple(int(x) for x in resp[2:-1].split(';'))
            )

    def echo(self, data):
        if self._echo:
            return self._writer.echo(data)

    def write(self, data):
        return self._writer.write(data)

    def writelines(self, data):
        return self._writer.writelines(data)

    def can_write_eof(self):
        return self._writer.can_write_eof()
    
    def write_eof(self):
        return self._writer.write_eof()

    def transport(self):
        return self._writer.transport()

    def get_extra_info(self, name, default=None):
        return self._writer.get_extra_info(name, default)

    async def drain(self):
        return await self._writer.drain()
    
    def close(self):
        return self._writer.close()

    def is_closing(self):
        return self._writer.is_closing()
    
    async def wait_closed(self):
        return await self._writer.wait_closed()

    async def read(self, n=-1):
        return await self._reader.read(n)

    async def readexactly(self, n):
        return await self._reader.readexactly(n)

    async def readuntil(self, separator='\n'):
        return await self._reader.readuntil(separator)

    async def readline(self, *, offset=None):
        _keys = keys()
        escape = ''
        char = ''
        line = ''
        col = 0
        if offset is None:
            _, offset = await self.get_position()
        else:
            offset = offset
        while True:
            async with self._readlock:
                self._readtask = asyncio.create_task(self.read(1))
                try:
                    char = await self._readtask
                except asyncio.CancelledError:
                    continue
            if char in '\x04\x03':
                return self.BREAK
            if escape:
                if char == '\x1b':
                    print(f"unknown escape - previous keypress: {escape!r}")
                    escape = '\x1b'
                    continue
                escape += char
                if escape not in _keys:
                    continue
                char, escape = escape, ''
            if char == '\x1b':
                escape += char
                continue
            if char == '\r':
                return line
            line, col = edit(line, col, char)
            self.echo(f'\x1b[{offset}G\x1b[0K{line}\x1b[{col+offset}G')

    def at_eof(self):
        return self._reader.at_eof()

    async def __aiter__(self):
        while not self.at_eof():
            yield await self.readline()