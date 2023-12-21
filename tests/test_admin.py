from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.http import Http404
from django.test import RequestFactory
from django.test.testcases import TestCase
from update_cache import admin
from update_cache.cache.cache import make_cache_key, missing
from update_cache.models import CacheEntry
from pyquery import PyQuery

from testapp import cached_functions


class TestCacheEntryAdmin(TestCase):

    def setUp(self):
        super().setUp()
        self.site = AdminSite()
        self.user = User.objects.create_superuser('admin')
        self.request_factory = RequestFactory()

    def test_changelist(self):
        request = self.request_factory.get('/')
        request.user = self.user
        cached_functions.create_random_strings(1)
        cached_functions.create_random_strings(2)
        cached_functions.create_random_numbers(1)
        ma = admin.CacheEntryAdmin(CacheEntry, self.site)
        response = ma.changelist_view(request)
        response.render()
        self.assertEqual(response.status_code, 200)

        doc = PyQuery(response.content)
        rows = PyQuery(doc.find("#result_list tbody tr"))
        self.assertEqual(len(rows), 3)

        cache_keys = [
            make_cache_key(
                cached_functions.create_random_strings,
                ((1,), {})
            ),
            make_cache_key(
                cached_functions.create_random_strings,
                ((2,), {})
            ),
            make_cache_key(
                cached_functions.create_random_numbers,
                ((1,), {})
            )
        ]
        row = PyQuery(rows[0])
        cache_key_cell = PyQuery(PyQuery(row.find("th"))[0])
        self.assertEqual(cache_key_cell.text(), cache_keys[2])
        row = PyQuery(rows[1])
        cache_key_cell = PyQuery(PyQuery(row.find("th"))[0])
        self.assertEqual(cache_key_cell.text(), cache_keys[1])
        row = PyQuery(rows[2])
        cache_key_cell = PyQuery(PyQuery(row.find("th"))[0])
        self.assertEqual(cache_key_cell.text(), cache_keys[0])

    def test_changeview(self):
        request = self.request_factory.get('/')
        request.user = self.user
        cached_functions.create_random_strings(1)
        ma = admin.CacheEntryAdmin(CacheEntry, self.site)
        cache_key = make_cache_key(
            cached_functions.create_random_strings,
            ((1,), {})
        )
        response = ma.change_view(request, cache_key)
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_changeview_not_found(self):
        request = self.request_factory.get('/')
        request.user = self.user
        ma = admin.CacheEntryAdmin(CacheEntry, self.site)
        with self.assertRaises(Http404):
            ma.change_view(request, 'foo')

    def test_invalidate(self):
        result = cached_functions.create_random_strings(1)
        cache_key = make_cache_key(
            cached_functions.create_random_strings,
            ((1,), {})
        )
        data = {
            '_selected_action': [cache_key]
        }
        request = self.request_factory.post('/', data)
        request.user = self.user
        ma = admin.CacheEntryAdmin(CacheEntry, self.site)
        with mock.patch.object(ma, 'message_user'):
            ma.invalidate(request, CacheEntry.objects.all())
        cache = cached_functions.create_random_strings.cache
        value = cache.get_active(cache_key, missing)
        self.assertEqual(value, missing)
        value = cache.get_expired(cache_key, missing)
        self.assertEqual(value.result, result)

    def test_delete(self):
        cached_functions.create_random_strings(1)
        cache_key = make_cache_key(
            cached_functions.create_random_strings,
            ((1,), {})
        )
        data = {
            '_selected_action': [cache_key]
        }
        request = self.request_factory.post('/', data)
        request.user = self.user
        ma = admin.CacheEntryAdmin(CacheEntry, self.site)
        with mock.patch.object(ma, 'message_user'):
            ma.delete(request, CacheEntry.objects.all())
        cache = cached_functions.create_random_strings.cache
        value = cache.get_active(cache_key, missing)
        self.assertEqual(value, missing)
        value = cache.get_expired(cache_key, missing)
        self.assertEqual(value, missing)
        self.assertEqual(CacheEntry.objects.count(), 0)
