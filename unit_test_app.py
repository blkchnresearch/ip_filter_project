
# I am now going to enhance the unit test to check concurrency. 
import unittest
from concurrent.futures import ThreadPoolExecutor
from backend import app

# Define functions to be executed. Again, this is not optimal but I am running short on time. 
def get_tor_ip(_):
    with app.test_client() as client:
        response = client.get('/tor')
        return response.status_code

def post_non_tor_ip(_):
    with app.test_client() as client:
        response = client.post('/non-tor', json={'ip': '192.168.1.1'})
        return response.status_code

class backend_test(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_tor_endpoint(self):
        # First endpoint test
        response = self.app.get('/tor')
        self.assertEqual(response.status_code, 200)

    def test_non_tor_endpoint(self):
        # Second endpoint test
        response = self.app.post('/non-tor', json={'ip': '192.168.1.1'})
        self.assertEqual(response.status_code, 200)


    # Ok, so this was simple as we had done in our previous unit test. The main issue comes now.
    # How do we test parallel requests? 
    def test_parallel_requests(self):
        # Parallel Get and Post
        # Reference to this code in StackOverflow: https://stackoverflow.com/questions/20838162/how-does-threadpoolexecutor-map-differ-from-threadpoolexecutor-submit
        with ThreadPoolExecutor(max_workers=2) as executor:
            result = list(executor.map(get_tor_ip, [None] * 2)) + list(executor.map(post_non_tor_ip, [None] * 2))
        # Check if both of the requests were successful
        for status_code in result:
            self.assertEqual(status_code, 200)

    # Note sure this is working fine :-(. Unfortunately, my expertise end here. 

if __name__ == '__main__':
    unittest.main()
