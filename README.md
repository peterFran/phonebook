# phonebook
## Setup
To set up, you'll need to make sure that you have all of the dependencies in requirements.txt installed in your virtualenv. 
You can do this using the command:
`pip install -r requirements.txt`
*Make sure this is your python 3 virtualenv pip instance*
## to start on port 5000 run:
`python3 phonebook.py`
## To run multiple instances on different ports, you can specify a port like so:
`python3 phonebook.py 5001`

## 5 methods are supported using the following urls:
1. `/list` - GET: returns all phonebook entries as a JSON object

2. `/add` - POST: adds a new entry to the phone book. Form parameters are:
    - forename
    - surname
    - telephone
    - address (optional)

3. `/delete/\<id\>` - DELETE: takes an entry id, and deletes that entry if it exists.

4. `/search/\<surname\>` - GET: takes surname and finds all SIMILAR surnames, and returns their entries in a JSON object

5. `/update` - PUT: takes between 2 and 5 parameters. The same as those in /add, but with a mandatory 'id' field, which 
serves to identify the entry for updating


## Testing
- unittests are int PhoneBookTestCase.py
- there is a rudimentary system test PhoneBookSystemTestCase  to test that the system is running when you start 
your own server on port 5000. Note, this will fail if you do not have a server running.

*NOTE: This is a python3 application, so you'll need a python3 interpreter to make it work. - Embrace, the future.*
