import asyncio

import telnetlib3

import bbs.models
from bbs.command_processor import MainProcessor
from bbs.readline import Readline

async def login(reader):
    username = await reader.prompt('username: ')
    user = await bbs.models.User.get_user(username)
    with reader.no_echo():
        password = await reader.prompt('\r\npassword: ')
    if user is None:
        return None
    if user.verify(password):
        return user
    return None

async def shell(reader, writer):
    reader, writer = Readline.wrap_streams(reader, writer)
    user = None
    while not user:
        user = await login(reader)
        if user == reader.BREAK:
            await writer.drain()
            writer.close()
            return
        writer.write('\r\n')
    writer.write(f'Greetings {user}!\r\n')
    writer.write(f'Your home directory is {await (await user.home).full_path()}\r\n')
    writer.write((await MainProcessor(user, reader, writer).process()) + '\r\n')
    await writer.drain()
    writer.close()

async def start_telnet(host='', port=6023):
    return await telnetlib3.create_server(
        host=host,
        port=port,
        shell=shell,
    )