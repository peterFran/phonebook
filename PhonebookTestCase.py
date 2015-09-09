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
        get_request = self.app.get('/list')
        data = json.loads(get_request.data.decode('utf-8'))
        assert get_request.status_code == 200
        assert [] == data

    def test_search_entry(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Hitch',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Norris',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='John',
            surname='Meckiffe',
            telephone='07972124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        get_request = self.app.get('/search/Meckiffe')
        data = get_request.data.decode('utf-8')
        assert get_request.status_code == 200
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
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Norris',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='John',
            surname='Meckiffe',
            telephone='07972124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
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
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'
        assert confirmation['surname'] == 'Meckiffe'
        assert confirmation['telephone'] == '07872124086'
        assert confirmation['address'] == '3 Wren Close, Winch'

    def test_update_entry(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Petert',
            surname='Meckiffet',
            telephone='07872124085',
            address='3 Wren Close, Wincht',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Success"
        assert update_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Petert'
        assert confirmation[0]['surname'] == 'Meckiffet'
        assert confirmation[0]['telephone'] == '07872124085'
        assert confirmation[0]['address'] == '3 Wren Close, Wincht'

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Peterz',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Success"
        assert update_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Peterz'
        assert confirmation[0]['surname'] == 'Meckiffet'
        assert confirmation[0]['telephone'] == '07872124085'
        assert confirmation[0]['address'] == '3 Wren Close, Wincht'

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Petery',
            surname='Meckiffey',
        ), follow_redirects=True)
        print(update_result.data.decode('utf-8'))
        assert update_result.data.decode('utf-8') == "Success"
        assert update_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Petery'
        assert confirmation[0]['surname'] == 'Meckiffey'
        assert confirmation[0]['telephone'] == '07872124085'
        assert confirmation[0]['address'] == '3 Wren Close, Wincht'

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Peterl',
            surname='Meckiffel',
            telephone='07872124089',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Success"
        assert update_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Peterl'
        assert confirmation[0]['surname'] == 'Meckiffel'
        assert confirmation[0]['telephone'] == '07872124089'
        assert confirmation[0]['address'] == '3 Wren Close, Wincht'

        update_result = self.app.put('/update', data=dict(
            forename='Peterl',
            surname='Meckiffel',
            telephone='07872124089',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Please provide a valid ID"
        assert update_result.status_code == 400

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Peterl',
            surname='Meckiffel',
            telephone='0787',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Please enter valid phone number"
        assert update_result.status_code == 400

    def test_db_increment(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1
        assert confirmation[0]['id'] == 1
        post_result = self.app.post('/add', data=dict(
            forename='Jonny',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 2
        assert (confirmation[0]['id'] == 2 and confirmation[1]['id'] == 1) or (
        confirmation[1]['id'] == 2 and confirmation[0]['id'] == 1)

    def test_uniqueness(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.status_code == 401
        assert len(json.loads(self.app.get('/list').data.decode('utf-8'))) == 1

    def test_optional_address(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'
        assert confirmation['surname'] == 'Meckiffe'
        assert confirmation['telephone'] == '07872124086'
        assert confirmation['address'] == ''

    def test_delete_id(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        post_result = self.app.post('/add', data=dict(
            forename='Rob',
            surname='Mack',
            telephone='12345678987',
            address='3 Oldham St',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 200
        delete_assert = self.app.delete('/delete/1')
        assert delete_assert.data.decode('utf-8') == "Success"
        assert delete_assert.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1
        assert confirmation[0]['forename'] == 'Rob'
        assert confirmation[0]['surname'] == 'Mack'
        assert confirmation[0]['telephone'] == '12345678987'
        assert confirmation[0]['address'] == '3 Oldham St'

    def test_invalid_number(self):
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='j123',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Please enter valid phone number"
        assert post_result.status_code == 400




if __name__ == '__main__':
    unittest.main()
