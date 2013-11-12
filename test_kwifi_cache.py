#!/usr/bin/env python
#
#  Test that kwifiprompt / kanoconnect wireless cache works.
#  There is no need to have a wireless network setup to run these tests
#

import unittest
from kwififuncs import KwifiCache

fake_essid1 = 'one_fake_network'
fake_essid2 = 'two_fake_network'
fake_essid3 = 'three_fake_network'
fake_encryption = True
fake_key = 'mysecretkey'

class TestKwifiprompt(unittest.TestCase):

    def setUp(self):
        self.wcache = KwifiCache(cache_file='/tmp/test_kwifi_cache.conf')

    def test_save_network(self):
        r = self.wcache.save (fake_essid1, fake_encryption, fake_key)
        self.assertTrue (r, True)

    def test_get_cached(self):
        r = self.wcache.save (fake_essid2, fake_encryption, fake_key)
        self.assertEqual (r, True)

        r = self.wcache.get (fake_essid2)
        self.assertEqual (r['essid'], fake_essid2)
        self.assertEqual (r['encryption'], fake_encryption)
        self.assertEqual (r['enckey'], fake_key)

    def test_get_not_cached(self):
        r = self.wcache.get ('i do not exist')
        self.assertEqual (r, None)

    def test_get_latest(self):
        r = self.wcache.save (fake_essid3, fake_encryption, fake_key)
        self.assertEqual (r, True)

        r = self.wcache.get_latest ()
        self.assertEqual (r['essid'], fake_essid3)
        self.assertEqual (r['encryption'], fake_encryption)
        self.assertEqual (r['enckey'], fake_key)

if __name__ == '__main__':
    unittest.main()
