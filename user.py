#This file is part user_avatar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.transaction import Transaction
from trytond.config import config
from mimetypes import guess_type
from PIL import Image
import os
import hashlib

__all__ = ['User']
__metaclass__ = PoolMeta

AVATAR_SIZE = 150
IMAGE_TYPES = ['image/jpeg', 'image/png',  'image/gif']


class User:
    __name__ = 'res.user'
    avatar = fields.Function(fields.Binary('Avatar', filename='avatar_filename',
        help='Avatar User Image'), 'get_avatar', setter='set_avatar')
    avatar_filename = fields.Char('Avatar File Name',
        help='Avatar File Name')

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._preferences_fields.extend([
                'avatar',
                'avatar_filename',
                ])
        cls._context_fields.insert(0, 'avatar')
        cls._context_fields.insert(0, 'avatar_filename')
        cls._error_messages.update({
            'not_file_mime': ('Not know file mime "%(file_name)s"'),
            'not_file_mime_image': ('"%(file_name)s" file mime is not an image ' \
                '(jpg, png or gif)'),
            'image_size': ('Thumb "%(file_name)s" size is larger than "%(size)s"Kb'),
        })

    def get_avatar(self, name):
        db_name = Transaction().database.name
        filename = self.avatar_filename
        if not filename:
            return None
        filename = os.path.join(config.get('database', 'path'), db_name,
            'user', 'avatar', filename[0:2], filename[2:4], filename)

        value = None
        try:
            with open(filename, 'rb') as file_p:
                value = fields.Binary.cast(file_p.read())
        except IOError:
            pass
        return value

    @classmethod
    def set_avatar(cls, users, name, value):
        if value is None:
            return
        if not value:
            cls.write(users, {
                'avatar_filename': None,
                })
            return
    
        db_name = Transaction().database.name
        user_dir = os.path.join(
            config.get('database', 'path'), db_name, 'user', 'avatar')

        if not value:
            cls.write(users, {
                'avatar_filename': None,
                })
            return

        for user in users:
            file_name = user['avatar_filename']

            file_mime, _ = guess_type(file_name)
            if not file_mime:
                cls.raise_user_error('not_file_mime', {
                        'file_name': file_name,
                        })
            if file_mime not in IMAGE_TYPES:
                cls.raise_user_error('not_file_mime_image', {
                        'file_name': file_name,
                        })

            _, ext = file_mime.split('/')
            digest = '%s.%s' % (hashlib.md5(value).hexdigest(), ext)
            subdir1 = digest[0:2]
            subdir2 = digest[2:4]
            directory = os.path.join(user_dir, subdir1, subdir2)
            filename = os.path.join(directory, digest)

            if not os.path.isdir(directory):
                os.makedirs(directory, 0775)
            os.umask(0022)
            with open(filename, 'wb') as file_p:
                file_p.write(value)

            # square and thumbnail thumb image
            thumb_size = AVATAR_SIZE, AVATAR_SIZE
            try:
                im = Image.open(filename)
            except:
                if os.path.exists(filename):
                    os.remove(filename)
                cls.raise_user_error('not_file_mime_image', {
                        'file_name': file_name,
                        })

            width, height = im.size
            if width > height:
               delta = width - height
               left = int(delta/2)
               upper = 0
               right = height + left
               lower = height
            else:
               delta = height - width
               left = 0
               upper = int(delta/2)
               right = width
               lower = width + upper

            im = im.crop((left, upper, right, lower))
            im.thumbnail(thumb_size, Image.ANTIALIAS)
            im.save(filename)

            cls.write([user], {
                'avatar_filename': digest,
                })
