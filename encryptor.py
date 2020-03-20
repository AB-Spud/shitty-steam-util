from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os

class EncryptorFunctions(object):
    def __init__(self):
        super().__init__()
        self.key_location =  self.__parse_location__('enk')
        self.key = self.__get_key__(self.key_location)
    
    def __get_key__(self, path):
        if self.__check_file__(path):
            return self.load_key(path)
        else:
            return self.gen_key(path)

    def __parse_location__(self, arg):
        return os.path.join(os.environ['APPDATA'], arg)
    
    def __check_file__(self, arg):
        if os.path.isfile(arg):
            return True
        else:
            return False
    
    def gen_key(self, path):
        self.rkey = get_random_bytes(16)
        with open(path, 'wb') as self.data:
            self.data.write(self.rkey)
            self.data.close()
        
        return self.rkey
    
    def load_key(self, path):
        with open(self.key_location, 'rb') as self.data:
            self.dkey = self.data.read(16)
            self.data.close()
        return self.dkey

    def encrypt(self, data):
        try:
            self.cipher = AES.new(self.key, AES.MODE_CBC)
            self.val = data.encode('utf-8')
            self.ct_bytes = self.cipher.encrypt(pad(self.val, AES.block_size))
            self.en_data = b64encode(self.ct_bytes).decode('utf-8')
            self.init_vector = b64encode(self.cipher.iv).decode('utf-8')

            return self.en_data, self.init_vector

        except Exception as error:
            raise error

    def decrypt(self, data, init_vector):
        try:
            self.init_vector = b64decode(init_vector)
            self.cipher = AES.new(self.key, AES.MODE_CBC, self.init_vector)
            self.val = b64decode(data)
            self.rdata = unpad(self.cipher.decrypt(self.val), AES.block_size).decode('utf-8')
            return self.rdata
        
        except Exception as error:
            raise error

if __name__ == "__main__":
    c = EncryptorFunctions()
    a,b = c.encrypt('two')
    print(a, b)
    a = c.decrypt(a, b)
    print(a)
