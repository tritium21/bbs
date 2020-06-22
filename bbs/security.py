import hashlib

import aiohttp
from yarl import URL

from passlib.context import CryptContext
from password_strength import PasswordPolicy

PASSWORD_CONTEXT = CryptContext(schemes=['argon2'], deprecated='auto')

PASSWORD_POLICY = PasswordPolicy.from_names(strength=0.66)

async def is_valid(password):
    breached = not (await is_breached(password))
    strong = PASSWORD_POLICY.test(password) == []
    return all([breached, strong])

async def is_breached(password):
    value = hashlib.sha1(password.encode("utf8")).hexdigest().upper()
    url = URL("https://api.pwnedpasswords.com/range") / value[:5]
    async with aiohttp.ClientSession() as client:
        async with client.get(url, headers={'User-Agent': "bbs.security (Python)"}) as resp:
            response = await resp.text()
    entries = {h: int(c) for h, c in (v.split(':') for v in response.upper().split("\r\n"))}
    return value[5:] in entries
