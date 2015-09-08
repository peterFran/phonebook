__author__ = 'petermeckiffe'
import os
import phonebook
import unittest
import tempfile
import json


class PhonebookTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, phonebook.app.config['DATABASE'] = tempfile.mkstemp()
        phonebook.app.config['TESTING'] = True
        self.app = phonebook.app.test_client()
        phonebook.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(phonebook.app.config['DATABASE'])

    def test_empty_db(self):
        data = json.loads(self.app.get('/').data.decode('utf-8'))
        assert [] == data

    def test_search_entry(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Hitch',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Norris',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='John',
            surname='Meckiffe',
            telephone='07972124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        data = self.app.get('/search/Meckiffe').data.decode('utf-8')
        assert [{'id':4,'forename': 'Peter', 'surname': 'Meckiffe', \
                 'telephone': "07872124086", 'address': '3 Wren Close, Winch'}, \
                {'id':3,'forename': 'John', 'surname': 'Meckiffe', \
                 'telephone': "07972124086", 'address': '3 Wren Close, Winch'}] == json.loads(data)

    def test_search_with_case_insensitivity_and_shortened_word(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Hitch',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Norris',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='John',
            surname='Meckiffe',
            telephone='07972124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        data = self.app.get('/search/meckiffe').data.decode('utf-8')
        assert [{'id':4,'forename': 'Peter', 'surname': 'Meckiffe', \
                 'telephone': "07872124086", 'address': '3 Wren Close, Winch'}, \
                {'id':3,'forename': 'John', 'surname': 'Meckiffe', \
                 'telephone': "07972124086", 'address': '3 Wren Close, Winch'}] == json.loads(data)
        data = self.app.get('/search/ckiff').data.decode('utf-8')
        assert [{'id':4,'forename': 'Peter', 'surname': 'Meckiffe', \
                 'telephone': "07872124086", 'address': '3 Wren Close, Winch'}, \
                {'id':3,'forename': 'John', 'surname': 'Meckiffe', \
                 'telephone': "07972124086", 'address': '3 Wren Close, Winch'}] == json.loads(data)

    def test_add_entry(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        confirmation = json.loads(self.app.get('/').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'
        assert confirmation['surname'] == 'Meckiffe'
        assert confirmation['telephone'] == '07872124086'
        assert confirmation['address'] == '3 Wren Close, Winch'

    def test_db_increment(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        confirmation = json.loads(self.app.get('/').data.decode('utf-8'))
        assert len(confirmation) == 1
        assert confirmation[0]['id'] == 1
        post_result = self.app.post('/add', data=dict(
            forename='Jonny',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        confirmation = json.loads(self.app.get('/').data.decode('utf-8'))
        assert len(confirmation) == 2
        assert (confirmation[0]['id'] == 2 and confirmation[1]['id'] == 1) or (
        confirmation[1]['id'] == 2 and confirmation[0]['id'] == 1)

    def test_uniqueness(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        assert len(json.loads(self.app.get('/').data.decode('utf-8'))) == 1

    def test_optional_address(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == ""
        confirmation = json.loads(self.app.get('/').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'
        assert confirmation['surname'] == 'Meckiffe'
        assert confirmation['telephone'] == '07872124086'
        assert confirmation['address'] == ''

if __name__ == '__main__':
    unittest.main()
