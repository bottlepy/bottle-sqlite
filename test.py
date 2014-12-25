# -*- coding: utf-8 -*-
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

    def test_text_factory(self):
        # set text factory to str, unicode (default) would cause 
        # PrammingError: You must not use 8-bit bytestrings .. exception
        self.app.install(sqlite.Plugin(keyword='db2',text_factory=str))

        @self.app.get('/')
        def test(db, db2):
            char = 'ööö'
            db2.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL)")
            db2.execute("INSERT INTO todo (id,task) VALUES ('1',:TEST)", { "TEST": char })
            count = len(db2.execute("SELECT * FROM todo").fetchall())
            self.assertEqual(count, 1)

        self._request('/')

    def test_text_factory_fail(self):
        self.app.install(sqlite.Plugin(keyword='db3',text_factory=unicode))

        @self.app.get('/')
        def test(db, db3):
            char = 'ööö'
            db3.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL)")
            try:
                db3.execute("INSERT INTO todo (id,task) VALUES ('1',:TEST)", { "TEST": char })
            except sqlite3.ProgrammingError as e:
                pass

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
