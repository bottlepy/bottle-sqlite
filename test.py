import unittest
import sqlite3
import bottle
from bottle.ext import sqlite


class SQLiteTest(unittest.TestCase):
    def setUp(self):
        self.app = bottle.Bottle(catchall=False)

    def test_with_keyword(self):
        self.plugin = self.app.install(sqlite.Plugin())

        @self.app.get('/')
        def test(db):
            self.assertEqual(type(db), type(sqlite3.connect(':memory:')))
        self._request('/')

    def test_without_keyword(self):
        self.plugin = self.app.install(sqlite.Plugin())

        @self.app.get('/')
        def test_1():
            pass
        self._request('/')

        @self.app.get('/2')
        def test_2(**kw):
            self.assertFalse('db' in kw)
        self._request('/2')

    def test_install_conflicts(self):
        self.app.install(sqlite.Plugin())
        self.app.install(sqlite.Plugin(keyword='db2'))

        @self.app.get('/')
        def test(db, db2):
            pass

        # I have two plugins working with different names
        self._request('/')

    def test_raise_sqlite_integrity_error(self):
        self.plugin = self.app.install(sqlite.Plugin())

        @self.app.get('/')
        def test(db):
            raise sqlite3.IntegrityError()
        self._request('/')

    def _request(self, path, method='GET'):
        self.app({'PATH_INFO': path, 'REQUEST_METHOD': method},
                 lambda x, y: None)

if __name__ == '__main__':
    unittest.main()
