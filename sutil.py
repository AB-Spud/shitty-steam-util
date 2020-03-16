from steam import SteamID
import requests, sys, os, json, shutil, shlex

class SteamUtil(object):
    def __init__(self):
        self.cfg_location = self.__parse_location__('sutil.json')
        self.backup_dir = self.__parse_location__('sutil_backup')
        self.is_dir()
        self.cfg = self.__get_cfg__()
        self.steam_path = os.path.join(self.cfg['steam_path'], '')
        self.cmds = {'help': self.help, 'exit': self.exit,'clear': self.clear, 'init': self.stuffs ,'set': self.set_var, 'copy': self.copy, 'profs': self.list_profiles, 'get': self.get_var, 'gprofs': self.update_profile_list, 'backup': self.backup_profiles}
    

    def __get_cfg__(self):
        if self.__check_file__(self.cfg_location):
            return self.load_cfg(self.cfg_location)
        else:
            return self.__create_cfg__()

    def __parse_location__(self, arg):
        return os.path.join(os.environ['APPDATA'], arg)
    
    def __check_file__(self, arg):
        if os.path.isfile(arg):
            return True
        else:
            return False
    
    def __create_cfg__(self):
        self.cfg = {
            "steam_path": '',
            "master": '',
            "profiles": {}
        }

        json.dump(self.cfg, open(self.cfg_location, 'w+'), indent=4)

        return self.load_cfg(self.cfg_location)
    
    def stuffs(self, args):
        """ Gets profiles and backs them up """
        self.update_profile_list([])
        self.backup_profiles([])
    
    def call_cmd(self, cmd, *args):
        try:
            self.cmds[cmd](args[0])
        except Exception as error:
            if type(error) == KeyError:
                print(f"Unkown command {error} type 'help' for a list of commands.")
            else:
                pass
    
    def clear(self, args):
        """ Clears console """
        os.system('cls')
    
    def update_profile_list(self, args):
        """ Updates profile list to include all profiles that have been used on the PC """
        try:
            for self.i, self.user in enumerate(os.listdir(self.steam_path + "userdata")):
                self.url = SteamID(self.user).community_url
                req = requests.get(self.url+'/ajaxaliases')
                if req.status_code:
                    self.cfg['profiles'][json.loads(req.content)[0]['newname']] = self.user
                    print(f"{self.i}  Added: '{json.loads(req.content)[0]['newname']}'")
                else:
                    print(f'bad status request for {self.user}')
            
            print(f'Added {self.i+1} users to the profile list')
            self.save_cfg()

        except FileNotFoundError as error:
            print(f"var 'steam_path' is not a valid path\nsteam_path = '{self.cfg['steam_path']}'")
                  print(error)

    def load_cfg(self, arg):
        return json.load(open(arg, 'r'))
    
    def is_dir(self):
        if os.path.exists(self.backup_dir):
            pass
        else:
            os.mkdir(self.backup_dir)
    
    def save_cfg(self):
        json.dump(self.cfg, open(self.cfg_location, 'w+'), indent=4)
    
    def set_var(self, args):
        """ Takes list len of two, index 0 = var, index 1 = val, cmd = 'set <var> <val>' """
        self.cfg[args[0]] = args[1]
        self.save_cfg()
    
    def get_var(self, args):
        """ Takes a single arg, returns cfg variable, cmd = 'get <var>' """

        try:
            if args[0] == "*":
                for self.v in self.cfg.keys():
                    if self.v == 'profiles': pass
                    else: print(f'var : {self.v} = {self.cfg[self.v]}')
                return None
            else:
                print(f'var : {args[0]} = {self.cfg[args[0]]}')
                return self.cfg[args[0]]
        except KeyError as error:
            print(f"variable {error} doesn't exit")

    def copy(self, args):
        """ child inherits files from parent, cmd = 'copy <child_user> <parent_user>' """
        try:
            self.p = self.cfg[args[1]]
        except:
            try:
                self.p = args[1]
            except IndexError as error:
                print('Bad args: copy <child> <parent>')
                return None

        try:
            self.parent_path = os.path.join(self.steam_path, ("userdata\\" + self.cfg['profiles'][self.p] + "\\730"))
            if args[0] == "*":
                self.copy_all(self.p ,self.parent_path)
            else:
                self.child_path = os.path.join(self.steam_path, ("userdata\\" + self.cfg['profiles'][args[0]] + "\\730" ))

            try:
                shutil.rmtree(self.child_path)
                shutil.copytree(self.parent_path , self.child_path)
            except Exception as error:
                raise error

        except KeyError as error:
            print(f"Unknown profile: {error}")
    
    def copy_all(self, parent,parent_path):
        for self.i, self.prof in enumerate(self.cfg['profiles'].keys()):
            if self.prof == parent:
                pass
            else:
                self.child_path = os.path.join(self.steam_path, ("userdata\\" + self.cfg['profiles'][self.prof] + "\\730" ))
                try:
                    shutil.rmtree(self.child_path)
                    shutil.copytree(self.parent_path , self.child_path)
                except Exception as error:
                    raise error

        print(f"{self.i} profiles inherited settings from {parent}") 

    def list_profiles(self, args):
        """ Prints a list of all profiles that have been used on the PC, cmd = 'profs' """ 
        for self.index, self.profile in enumerate(self.get_profiles(args)):
            self.id = self.cfg['profiles'][self.profile]
            print(f'{self.id} \t{self.index} :', self.profile)
        
    def get_profiles(self, args):
        """ Return a list of all profiles that have been used on the PC """        
        return self.cfg['profiles'].keys()
    
    def backup_profiles(self, args):
        """ Backs up userdata, stored in APPDATA/sutil_backup """
        try:
            for self.i, self.n in enumerate(self.get_profiles(args)):
                self.path = os.path.join(self.cfg['steam_path'] + "\\userdata", self.cfg['profiles'][self.n])
                try:
                    shutil.rmtree(self.backup_dir+f"\\{self.cfg['profiles'][self.n]}")
                except:
                    pass
                shutil.copytree(src=self.path, dst=self.backup_dir+f"\\{self.cfg['profiles'][self.n]}")
                print(f"{self.i}  Backing up: {self.path}")
            print(f"Backed up {self.i+1} profiles.")
        except Exception as error:
            pass
    
    def exit(self, args):
        """ Exits the program """
        sys.exit(0)

    def help(self, args):
        """ If 'help' is called returns list of commands, 'help <cmd>' returns details on the command """
        if len(args) < 1:
            print("List of commands: ")
            for self.i, self.cmd in enumerate(self.cmds):
                print(f"---",self.cmd)
            print(f"\nTotal commands: {self.i+1}")
        else:
            try:
                print( self.cmds[args[0]].__doc__)
            except KeyError as error:
                print(f"Command {error} doesn't exist.\n")
                self.help([])



if __name__ == '__main__':
    a = SteamUtil()
    while True:
        ar = str(input(">>> "))
        args = shlex.split(ar)
        if len(args) < 1: args = ['clear', '']
        a.call_cmd(args[0],args[1:])
