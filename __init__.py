#This file is part user_avatar module for Tryton.
#The COPYRIGHT file at the top level of this repository contains 
#the full copyright notices and license terms.
from trytond.pool import Pool
from .user import *

def register():
    Pool.register(
        User,
        module='user_avatar', type_='model')
