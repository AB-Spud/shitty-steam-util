from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os, logging, json, shutil

class LocalUtil(object):
    def __init__(self, key_name):
        self.log_location = self.__get_expected__('startup_log.out')
        self.key_location =  self.__get_expected__(key_name)
        self.cfg_location = self.__get_expected__('sutil.json')
        self.backup_dir = self.__get_expected__('sutil_backup')

        self.key = None
        self.cfg = None
        self.steam_path = None

        logging.basicConfig(filename=self.log_location, level=logging.ERROR)

        self.__start_up__()

    def __get_expected__(self, arg):
        return os.path.join(os.environ['APPDATA'], arg)

    def __create_cfg__(self):
        self.cfg = {
            "steam_path": '',
            "master": '',
            "profiles": {},
            "users" : {}
        }

        json.dump(self.cfg, open(self.cfg_location, 'w+'), indent=4)

        return self.cfg
  
    def __start_up__(self):
        try:
            if self.check_path(self.key_location):
                self.key = self.load_key(self.key_location)
            else:
                self.key = self.gen_key(self.key_location)

            if self.check_path(self.cfg_location):
                self.cfg = self.load_cfg(self.cfg_location)
            else:
                self.cfg = self.__create_cfg__()

            if self.check_path(self.backup_dir):
                pass
            else:
                os.mkdir(self.backup_dir)

        except Exception as error:
            logging.exception(error)
            print(f'Exception occured check, {self.log_location} for traceback.\nException: {error}')

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

    def save_cfg(self):
        json.dump(self.cfg, open(self.cfg_location, 'w+'), indent=4)

    def gen_key(self, path):
        self.rkey = get_random_bytes(16)
        with open(path, 'wb') as self.data:
            self.data.write(self.rkey)
            self.data.close()
        
        return self.rkey

    def load_cfg(self, arg):
        return json.load(open(arg, 'r'))

    def load_key(self, path):
        with open(self.key_location, 'rb') as self.data:
            self.dkey = self.data.read(16)
            self.data.close()
        return self.dkey

    def check_path(self, arg):
        if os.path.isfile(arg):
            return True
        elif os.path.isdir(arg):
            return True
        else:
            return False

    def remove_var(self, args):
        """ Removes a var, cmd :: 'rmv <var>' """
        del self.cfg[args[0]]
        self.save_cfg()
    
    def remove_32_pointer(self, args):
        """ Removes a username that points to a steam_32 id from the cfg, cmd :: 'rm32 <user>' """
        del self.cfg['users'][args[0]]
        self.save_cfg()
    
    def remove_details(self, args):
        """ Removes login details from a username, cmd :: 'rmd <user>' """
        try:
            self.u_32 = self.cfg['users'][args[0]]
            self.cfg['profiles'][self.u_32 ]['details'] = {}
            self.save_cfg()
        except Exception as error:
            print(f'cmd :: rmd <user>\nError: {error}')


    def set_var(self, args):
        """ Takes list len of two, index 0 = var, index 1 = val, cmd :: 'set <var> <val>' """
        self.cfg[args[0]] = args[1]
        self.save_cfg()

    def get_local_var(self, var):
        """ returns var or vars as a dict """
        try:
            self.vars = {}
            if var == "*":
                for self.n, self.v in enumerate(self.cfg.keys()):
                    if self.v == 'profiles':
                        pass
                    else:
                        self.vars[self.v] = self.cfg[self.v]

                return self.vars
            else:
                self.vars[var] = self.cfg[var]
                return self.vars

        except Exception as error:
            pass

    def get_local_32(self):
        try:
            return os.listdir(os.path.join(self.cfg['steam_path'], "userdata"))
        except Exception as error:
            print('steam_path is most likely not set, unable to parse local userdata...\ncmd :: set steam_path "<path>" - ex. "C:\Program Files (x86)\Steam"\n')

    def add_prof_details(self, args):
        """ Add login details to a username, cmd :: add <user_name> <account_name> <password> """
        try:
            try:
                self.u_32  = self.cfg['users'][self.get_local_var(args[0])[args[0]]]
            except:
                self.u_32  = self.cfg['users'][args[0]]

            self.en_user, self.u_init = self.encrypt(args[1])
            self.en_pwrd, self.p_init = self.encrypt(args[2])

            self.cfg['profiles'][self.u_32 ]['details']['account_name'] = self.en_user
            self.cfg['profiles'][self.u_32 ]['details']['u_init'] = self.u_init
            self.cfg['profiles'][self.u_32 ]['details']['password'] = self.en_pwrd
            self.cfg['profiles'][self.u_32 ]['details']['p_init'] = self.p_init
            self.cfg['profiles'][self.u_32]['details']['ukey'] = self.key_location

            print('Saved!')
            self.save_cfg()

        except Exception as error:
            raise error

    def copy(self, args):
        """ child inherits files from parent, cmd :: 'copy <child_user> <parent_user>' """
        try:
            self.p = self.cfg['users'][self.get_local_var(args[1])[args[1]]]
        except:
            self.p = self.cfg['users'][args[1]]

        self.parent_path = os.path.join(self.cfg['steam_path'], ("userdata\\" + self.p + "\\730"))


        if args[0] == "*":
                self.copy_all(self.p ,self.parent_path)
        else:
            try:
                self.c = self.cfg['users'][self.get_local_var(args[0])[args[0]]]
            except:
                self.c = self.cfg['users'][args[0]]
            
            try:
                self.child_path = os.path.join(self.cfg['steam_path'], ("userdata\\" + self.c + "\\730" ))
                try:
                    shutil.rmtree(self.child_path)
                    shutil.copytree(self.parent_path , self.child_path)
                except Exception as error:
                    raise error

                print(self.c, '<--' ,self.p)

            except Exception as error:
                print(f"Unknown profile: {error}")


    def copy_all(self, parent,parent_path):
        for self.i, self.prof in enumerate(self.get_local_32()):
            if self.prof == parent:
                pass
            else:
                self.child_path = os.path.join(self.cfg['steam_path'], ("userdata\\" + self.prof + "\\730" ))
                try:
                    shutil.rmtree(self.child_path)
                    shutil.copytree(self.parent_path , self.child_path)
                except Exception as error:
                    raise error
                
                print(self.prof, '<--' ,parent)
        print(f"{self.i} profiles inherited settings from {parent}")

    def backup_profiles(self, args):
        """ Backs up userdata, stored in APPDATA/sutil_backup """
        try:
            for self.i, self.n in enumerate(self.get_local_32()):
                self.path = os.path.join(self.cfg['steam_path'] + "\\userdata", self.n)
                try:
                    shutil.rmtree(self.backup_dir+f"\\{self.n}")
                except:
                    pass
                shutil.copytree(src=self.path, dst=self.backup_dir+f"\\{self.n}")

                print(f"{self.i}  Backing up: {self.path}\t : {self.cfg['profiles'][self.n]['user_name']}")
            print(f"Backed up {self.i+1} profiles.")
        except Exception as error:
            print(f'Error: {error}\n')

if __name__ == "__main__":
    pass
    
