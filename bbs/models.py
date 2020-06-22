from enum import IntEnum
import pathlib

from tortoise.models import Model
from tortoise import fields, Tortoise, run_async

from bbs.security import PASSWORD_CONTEXT


class ContentType(IntEnum):
    text = 0
    directory = 1


class Document(Model):
    ROOT = '@__ROOT__@'
    USERS = 'users'

    id = fields.IntField(pk=True)
    segment = fields.CharField(255)
    content_type = fields.IntEnumField(ContentType, default=ContentType.directory)
    parent: fields.ForeignKeyNullableRelation["Document"] = fields.ForeignKeyField(
        "models.Document", on_delete=fields.CASCADE, related_name="children", null=True
    )
    children: fields.ReverseRelation["Document"]
    # owner: fields.ForeignKeyNullableRelation["User"] = fields.ForeignKeyField(
    #     "models.User", related_name="documents", null=True
    # )
    content = fields.TextField(null=True)

    async def full_path(self):
        segments = []
        obj = self
        while obj.segment != self.ROOT:
            segments.append(obj.segment)
            obj = await obj.parent
        return pathlib.PurePosixPath('/', *reversed(segments))

    @classmethod
    async def get_root(cls):
        return await cls.get(segment=cls.ROOT)

    @classmethod
    async def get_users(cls):
        return await cls.get(segment=cls.USERS)

    @classmethod
    async def create_roots(cls):
        root = await cls.create(segment=cls.ROOT)
        users = await cls.create(segment=cls.USERS, parent=root)
        await root.save()
        await users.save()

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255, unique=True, index=True)
    password = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    is_admin = fields.BooleanField()
    can_chat = fields.BooleanField()

    # documents: fields.ReverseRelation["Document"]
    home: fields.OneToOneNullableRelation["Document"] = fields.OneToOneField(
        'models.Document', on_delete=fields.CASCADE, null=True
    )

    @classmethod
    async def new_user(cls, username, password, email, can_chat, is_admin):
        password = PASSWORD_CONTEXT.hash(password)
        user = await cls.create(
            username=username,
            password=password,
            email=email,
            can_chat=can_chat,
            is_admin=is_admin,
        )
        user_root = await Document.get_users()
        user_dir = await Document.create(
            segment=user.username,
            parent=user_root,
        )
        user.home = user_dir
        user_dir.owner = user
        await user_dir.save()
        await user.save()
        return user

    @classmethod
    async def get_user(cls, username):
        user = await cls.filter(username=username).first()
        return user

    def verify(self, password):
        return PASSWORD_CONTEXT.verify(password, self.password)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.username=}, password=..., {self.email=}, {self.is_admin=}, {self.can_chat=})>"

    def __str__(self):
        return self.username

async def models_init(new=False):
    db = await Tortoise.init(db_url='sqlite://test.db', modules={'models': [__name__]})
    if new:
        await Tortoise.generate_schemas()
        await Document.create_roots()
        users = zip('admin user guest'.split(), [True, True, False], [True, False, False])
        for username, can_chat, is_admin in users:
            user = await User.new_user(
                username=username,
                password='password',
                email=f'{username}@bbs.sdamon.com',
                can_chat=can_chat,
                is_admin=is_admin,
            )
    return db

async def models_cleanup():
    await Tortoise.close_connections()

if __name__ == '__main__':
    import asyncio
    async def newinit():
        try:
            await models_init(True)
        finally:
            await models_cleanup()
    asyncio.run(newinit())