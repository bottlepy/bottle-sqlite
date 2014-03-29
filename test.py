import os
import unittest
import sqlite3
import tempfile

import bottle
from bottle.ext import sqlite


class SQLiteTest(unittest.TestCase):

    def setUp(self):
        self.app = bottle.Bottle(catchall=False)
        _, dbfile = tempfile.mkstemp(suffix='.sqlite')
        self.plugin = self.app.install(sqlite.Plugin(dbfile=dbfile))

        self.conn = sqlite3.connect(dbfile)
        self.conn.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL)")
        self.conn.commit()

    def tearDown(self):
        os.unlink(self.plugin.dbfile)

    def test_with_keyword(self):
        @self.app.get('/')
        def test(db):
            self.assertEqual(type(db), type(sqlite3.connect(':memory:')))
        self._request('/')

    def test_without_keyword(self):
        @self.app.get('/')
        def test_1():
            pass
        self._request('/')

        @self.app.get('/2')
        def test_2(**kw):
            self.assertFalse('db' in kw)
        self._request('/2')

    def test_install_conflicts(self):
        self.app.install(sqlite.Plugin(keyword='db2'))

        @self.app.get('/')
        def test(db, db2):
            pass

        # I have two plugins working with different names
        self._request('/')

    def test_raise_sqlite_integrity_error(self):
        @self.app.get('/')
        def test(db):
            # task can not be null, raise an IntegrityError
            db.execute("INSERT INTO todo (id) VALUES (1)")

        # TODO: assert HTTPError 500
        self._request('/')
        self.assert_records(0)

    def test_autocommit(self):
        @self.app.get('/')
        def test(db):
            self._insert_into(db)

        self._request('/')
        self.assert_records(1)

    def test_not_autocommit(self):
        @self.app.get('/', sqlite={'autocommit': False})
        def test(db):
            self._insert_into(db)

        self._request('/')
        self.assert_records(0)

    def test_commit_on_redirect(self):
        @self.app.get('/')
        def test(db):
            self._insert_into(db)
            bottle.redirect('/')

        self._request('/')
        self.assert_records(1)

    def test_commit_on_abort(self):
        @self.app.get('/')
        def test(db):
            self._insert_into(db)
            bottle.abort()

        self._request('/')
        self.assert_records(0)

    def _request(self, path, method='GET'):
        return self.app({'PATH_INFO': path, 'REQUEST_METHOD': method},
                        lambda x, y: None)

    def _insert_into(self, db):
        sql = "INSERT INTO todo (task) VALUES ('PASS')"
        db.execute(sql)

    def assert_records(self, count):
        cursor = self.conn.execute("SELECT COUNT(*) FROM todo")
        self.assertEqual((count,), cursor.fetchone())

if __name__ == '__main__':
    unittest.main()
