
import sys; sys.path.append('..')  #Needed to do this hack, as there is a problem with the unittest module to import from other directories
from RoboCraig import app
import unittest


class FlaskTestCase(unittest.TestCase):

    # Test to see if it can get to the landing page correctly
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)


    # Test to see if the login page properly loads with the text "login" on the page
    def test_login_load(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertTrue(b'Login' in response.data)

    # Testing the home page redirect to see if the text "Enter some search details" displays
    def test_page_redirect(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        print (tester)
        print (response.data)
        self.assertTrue(b'Enter some search details' in response.data)



if __name__ == '__main__':
    unittest.main()