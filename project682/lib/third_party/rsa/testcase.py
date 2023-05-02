import unittest
from third_party.rsa import key
import hashlib
from third_party.rsa import base64

from third_party.rsa.pkcs1 import encrypt, decrypt, sign, verify, sign_hash, VerificationError, DecryptionError

class PKCS1Test(unittest.TestCase):
    
   
    def test_encrypt_decrypt(self):
        (public_key, private_key) = key.newkeys(512)
        plaintext = b'This is a secret message.'

        # Encrypt the message
        ciphertext = encrypt(plaintext, public_key)

        # Decrypt the message
        decrypted_text = decrypt(ciphertext, private_key)

        # Verify the decrypted message matches the original plaintext
        self.assertEqual(decrypted_text, plaintext)
        
    def test_sign_verify(self):
        (public_key, private_key) = key.newkeys(512)
        message = b'This is a message to sign.'

        # Sign the message
        signature = sign(message, private_key, 'SHA-256')
        # Verify the signature
        verify(message, signature, public_key)
        
    def test_sign_hash(self):
        (public_key, private_key) = key.newkeys(512)
        message = b'This is a message to sign.'
        hash_value = hashlib.sha256(message).digest()

        # Sign the hash
        signature = sign_hash(hash_value, private_key, 'SHA-256')

        # Verify the signature
        verify(message, signature, public_key) 
        
        
    def test_decrypt_fail(self):
        (public_key, private_key) = key.newkeys(512)
        plaintext = b'This is a secret message.'
        ciphertext = encrypt(plaintext, public_key)

        # Modify ciphertext to cause decryption to fail
        modified_ciphertext = b'X' + ciphertext[1:]

        # Verify decryption fails
        with self.assertRaises(DecryptionError):
            decrypt(modified_ciphertext, private_key)

"""
def test_sign_verify_file(self):
        (public_key, private_key) = key.newkeys(512)
        message = b'This is a message to sign.'
        hash_value = hashlib.sha256(message).digest()

        # Sign the hash
        signature = sign_hash(hash_value, private_key, 'SHA-256')

        # Write message and signature to file
        with open('testfile', 'wb') as f:
            f.write(message)
            f.write(signature)

        # Verify the signature on file
        with open('testfile', 'rb') as f:
            verify(f, signature, public_key)
def test_verify_fail(self):
        (public_key, private_key) = key.newkeys(512)
        message = b'This is a message to sign.'
        signature = base64.b64decode('VxhZ4Pe+4GYaYn/PL5+yVhJNbUBrL9Mk0J0cMNFZ8WjHg+12loYBQI/Vtnv/d8W6fJd9kLRikzHz93q3mp8WQ==')

        # Verify signature fails
        with self.assertRaises(VerificationError):
            verify(message, signature, public_key)"""


if __name__ == '__main__':
    unittest.main()


