import unittest
from backend import app

# A basic unittest app. Just set up, test for the Endpoint 1 and then Endpoint 2. 

class backend_test(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_tor_endpoint(self):
        # First endpoint test. 
        response = self.app.get('/tor')
        self.assertEqual(response.status_code, 200)

        
    def test_non_tor_endpoint(self):
        # Second endpoint test. 
        response = self.app.post('/non-tor', json={'ip': '192.168.1.1'})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
