__author__ = 'petermeckiffe'
import os
import phonebook
import unittest
import tempfile
import json
import urllib


class PhonebookTestCase(unittest.TestCase):
    # Set up a testing app each time a test case runs
    def setUp(self):

        self.db_fd, phonebook.app.config['DATABASE'] = tempfile.mkstemp()
        phonebook.app.config['TESTING'] = True
        self.app = phonebook.app.test_client()
        phonebook.init_db()

    # Reset the testing db after each test
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(phonebook.app.config['DATABASE'])

    # Test that the DB is empty (basic test)
    def test_empty_db(self):
        # Using Flask internal app request testing mechanism, test that the db is empty
        get_request = self.app.get('/list')
        data = json.loads(get_request.data.decode('utf-8'))
        assert get_request.status_code == 200
        assert [] == data

    def test_search_entry(self):
        # Add 4 entries, make sure they are created with 201 RC
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Hitch',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Norris',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        post_result = self.app.post('/add', data=dict(
            forename='John',
            surname='Meckiffe',
            telephone='07972124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201

        # Search for name Meckiffe, and ensure that only the two we want come back
        get_request = self.app.get('/search/Meckiffe')
        data = get_request.data.decode('utf-8')
        assert get_request.status_code == 200
        assert [{'id':4,'forename': 'Peter', 'surname': 'Meckiffe', \
                 'telephone': "07872124086", 'address': '3 Wren Close, Winch'}, \
                {'id':3,'forename': 'John', 'surname': 'Meckiffe', \
                 'telephone': "07972124086", 'address': '3 Wren Close, Winch'}] == json.loads(data)

    def test_search_with_case_insensitivity_and_shortened_word(self):
        # Create the same 4 entries as the previous test
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Hitch',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Norris',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
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
        assert post_result.status_code == 201
        # Check that both entries also come back when we supply a lower case M and when we shorten the word.
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
        # Check that if we add an entry and then list all entries, we get the same details passed back to us.
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'
        assert confirmation['surname'] == 'Meckiffe'
        assert confirmation['telephone'] == '07872124086'
        assert confirmation['address'] == '3 Wren Close, Winch'

    def test_update_non_extant(self):
        # Test that the update function gives us a 404 if we try to update a non-extant entry
        all_entries = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(all_entries) == 0
        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Petert',
            surname='Meckiffet',
            telephone='07872124085',
            address='3 Wren Close, Wincht',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Entry does not exist"
        assert update_result.status_code == 404

    def test_update_entry(self):
        # Test that we can update an entry, changing all of its fields.
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
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
        # Check there is only 1 item in the DB
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Petert'
        assert confirmation[0]['surname'] == 'Meckiffet'
        assert confirmation[0]['telephone'] == '07872124085'
        assert confirmation[0]['address'] == '3 Wren Close, Wincht'

    def test_update_subset(self):
        # Test that if we only update 1, 2 or 3 items they will still update correctly
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Peterz',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Success"
        assert update_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Peterz'
        assert confirmation[0]['surname'] == 'Meckiffe'
        assert confirmation[0]['telephone'] == '07872124086'
        assert confirmation[0]['address'] == '3 Wren Close, Winch'

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Petery',
            surname='Meckiffey',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Success"
        assert update_result.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1

        assert confirmation[0]['forename'] == 'Petery'
        assert confirmation[0]['surname'] == 'Meckiffey'
        assert confirmation[0]['telephone'] == '07872124086'
        assert confirmation[0]['address'] == '3 Wren Close, Winch'

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
        assert confirmation[0]['address'] == '3 Wren Close, Winch'

    def test_update_no_ID(self):
        # Check that we get a 400 bad request if we try to update without ID
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201

        update_result = self.app.put('/update', data=dict(
            forename='Peterl',
            surname='Meckiffel',
            telephone='07872124089',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Please provide a valid ID"
        assert update_result.status_code == 400

    def test_update_invalid_telephone(self):
        # Test that we get a bad request if we try to update with non-compliant phone number
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201

        update_result = self.app.put('/update', data=dict(
            id=1,
            forename='Peterl',
            surname='Meckiffel',
            telephone='0787',
        ), follow_redirects=True)
        assert update_result.data.decode('utf-8') == "Please enter valid phone number"
        assert update_result.status_code == 400

    def test_db_increment(self):
        # Test that we grow by 1 as we add 1 item
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
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
        assert post_result.status_code == 201
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 2
        assert (confirmation[0]['id'] == 2 and confirmation[1]['id'] == 1) or (
        confirmation[1]['id'] == 2 and confirmation[0]['id'] == 1)

    def test_uniqueness(self):
        # Test that if we add exactly the same entry twice, the server gives us a 409 duplicate error.
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.status_code == 409
        assert post_result.data.decode('utf-8') == "Entry already exists on the system"
        assert len(json.loads(self.app.get('/list').data.decode('utf-8'))) == 1

    def test_optional_address(self):
        # Test that if we add without an address, the system doesn't crash out, and instead adds with blank address field
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'
        assert confirmation['surname'] == 'Meckiffe'
        assert confirmation['telephone'] == '07872124086'
        assert confirmation['address'] == ''

    def test_non_optional_telephone(self):
        # Test that if we add without an telephone, the system does crash out, and gives us a 400 Bad Request
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.status_code == 400

    def test_non_optional_forename(self):
        # Test that if we add without an forename, the system does crash out, and gives us a 400 Bad Request
        post_result = self.app.post('/add', data=dict(
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.status_code == 400

    def test_non_optional_surname(self):
        # Test that if we add without an surname, the system does crash out, and gives us a 400 Bad Request
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.status_code == 400


    def test_delete_id(self):
        # Test that we can delete an item from the phonebook
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='07872124086',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        post_result = self.app.post('/add', data=dict(
            forename='Rob',
            surname='Mack',
            telephone='12345678987',
            address='3 Oldham St',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        delete_assert = self.app.delete('/delete/1')
        assert delete_assert.data.decode('utf-8') == "Success"
        assert delete_assert.status_code == 200
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))
        assert len(confirmation) == 1
        assert confirmation[0]['forename'] == 'Rob'
        assert confirmation[0]['surname'] == 'Mack'
        assert confirmation[0]['telephone'] == '12345678987'
        assert confirmation[0]['address'] == '3 Oldham St'

    def test_delete_id(self):
        # Test that we get a 400 if we don't delete with a valid ID
        delete_assert = self.app.delete('/delete/1')
        assert delete_assert.data.decode('utf-8') == "Entry does not exist"
        assert delete_assert.status_code == 404


    def test_bobby_tables(self):
        # Check that if we add an entry and then list all entries, we get the same details passed back to us.
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname="'Meckiffe'); DROP TABLE phonebook;",
            telephone="07872124086",
            address='"3 Wren Close, Winch"; DROP TABLE phonebook;',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Success"
        assert post_result.status_code == 201
        confirmation = json.loads(self.app.get('/list').data.decode('utf-8'))[0]
        assert confirmation['forename'] == 'Peter'

        assert confirmation['surname'] == "'Meckiffe'); DROP TABLE phonebook;"
        assert confirmation['telephone'] == '07872124086'
        print(confirmation['address'])
        assert confirmation['address'] == '"3 Wren Close, Winch"; DROP TABLE phonebook;'


    def test_add_with_invalid_number(self):
        # Test that an invalid phonenumber in an add causes a 400 bad request
        post_result = self.app.post('/add', data=dict(
            forename='Peter',
            surname='Meckiffe',
            telephone='j123',
            address='3 Wren Close, Winch',
        ), follow_redirects=True)
        assert post_result.data.decode('utf-8') == "Please enter valid phone number"
        assert post_result.status_code == 400

# These will only pass if you have an active server
# A subset of the main unit tests to be run, to make sure our flask app works over a localhost at least.
class PhonebookSystemTestCase(unittest.TestCase):
    # Location of our server
    PORT = 5000
    HOST = "127.0.0.1"

    def test_web_service_up(self):
        url = 'http://{}:{}/list'.format(self.HOST,self.PORT)
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            assert response.code == 200
            assert [] == data

if __name__ == '__main__':
    unittest.main()
