import unittest
import network
import main
from main import sync_time

class TestMicropythonCode(unittest.TestCase):
    
    # Test case for the read_settings function
    def test_read_settings(self):
        print('Test read settings function\n')
        settings = main.read_settings()
        self.assertIsInstance(settings, tuple) # Asserts that settings is an instance of tuple
        self.assertEqual(len(settings), 4) # Asserts that settings has a length of 4
        
    # Test case for the read_key function
    def test_read_key(self):
        print('Test read key function \n')
        keys = main.read_key('Your @at_sign')
        self.assertIsInstance(keys, tuple) # Asserts that keys is an instance of tuple
        self.assertEqual(len(keys), 5) # Asserts that keys has a length of 5
        
    # Test case for the find_secondary function
    def test_find_secondary(self):
        print('Test find secondary function\n')
        secondary = main.find_secondary('Your @at_sign')
        self.assertIsInstance(secondary, str) # Asserts that secondary is an instance of string
        
    # Test case for the connect_to_secondary function
    def test_connect_to_secondary(self):
        #print('Test connect to secondary function\n')
        secondary = main.find_secondary('your @at_sign')
        self.assertTrue(main.connect_to_secondary(secondary)) # Asserts that connecting to secondary is successful
        
    # Test case for the send_verbs function
    def test_send_verbs(self):
        print('Test send verbs function\n')
        secondary = main.find_secondary('your @at_sign')
        ss = main.connect_to_secondary(secondary)
        response, command = main.send_verbs(ss, 'your @at_sign')
        self.assertIsInstance(response, str) # Asserts that response is an instance of string
        self.assertIsInstance(command, str) # Asserts that command is an instance of string
        
if __name__ == '__main__':
    unittest.main()
