import unittest
import network
import main
from main import sync_time
class TestMicropythonCode(unittest.TestCase):
        
    def test_read_settings(self):
        print('Test read settings function\n')
        settings = main.read_settings()
        self.assertIsInstance(settings, tuple)
        self.assertEqual(len(settings), 4)
        
    def test_read_key(self):
        print('Test read key function \n')
        keys = main.read_key('928weekly')
        self.assertIsInstance(keys, tuple)
        self.assertEqual(len(keys), 5)
        
    def test_find_secondary(self):
        print('Test find secondary function\n')
        secondary = main.find_secondary('928weekly')
        self.assertIsInstance(secondary, str)
        
    def test_connect_to_secondary(self):
        #print('Test connect to secondary function\n')
        secondary = main.find_secondary('928weekly')
        self.assertTrue(main.connect_to_secondary(secondary))
        
    def test_send_verbs(self):
        print('Test send verbs function\n')
        secondary = main.find_secondary('928weekly')
        ss = main.connect_to_secondary(secondary)
        response, command = main.send_verbs(ss, '928weekly')
        self.assertIsInstance(response, str)
        self.assertIsInstance(command, str)
        
if __name__ == '__main__':
    unittest.main()