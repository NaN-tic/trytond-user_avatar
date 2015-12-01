# This file is part of the user_avatar module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class UserAvatarTestCase(ModuleTestCase):
    'Test User Avatar module'
    module = 'user_avatar'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        UserAvatarTestCase))
    return suite
