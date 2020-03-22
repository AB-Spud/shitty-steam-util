from steam import SteamID
from local_util import LocalUtil
import requests, sys, os, json, shlex, pyperclip

class UtilFunctions(LocalUtil):
    def __init__(self, key_name):
        super().__init__(key_name)

    def help(self, args):
        """ If 'help' is called returns list of commands, 'help <cmd>' returns details on the command """
        if len(args) < 1:
            print("List of commands:\ncmd :: help <cmd>")
            for self.i, self.cmd in enumerate(self.cmds):
                print(f"---",self.cmd)
            print(f"\nTotal commands: {self.i+1}")
        else:
            try:
                print( self.cmds[args[0]].__doc__)
            except KeyError as error:
                print(f"Command {error} doesn't exist.\n")
                self.help([])

    def data_init(self, *args):
        """ Inits Data - be sure to set steam_path first """
        print('Getting profile data...')
        self.get_prof_names([])
        print('Backing up profiles...')
        self.backup_profiles([])

    def clear(self, args):
        """ Clears console """
        os.system('cls')

    def exit(self, args):
        """ Exits the program """
        sys.exit(0)

    def kill_steam(self, args):
        """ Kills the Steam.exe process - this can be used with the login function, cmd :: kill """
        try:
            os.system(f"TASKKILL /F /IM Steam.exe /T")
        except Exception as error:
            print(error)

    def display_var(self, args):
        """ Takes a single arg, returns cfg variable, cmd :: 'get <var>' """
        try:
            for self.d, self.v in enumerate(self.get_local_var(args[0])):
                print(f"{self.d} var : {self.v} = {self.cfg[self.v]}")
        except Exception as error:
            if type(error) == KeyError:
                print(f"cmd :: get <var>\nvariable '{args[0]}' doesn't exit")
            else:
                print(f"cmd :: get <var>\nError: {error}")


    def display_profiles(self, args):
        """ Prints a list of all profiles saved in the CONFIG """
        print("- STEAM_32 - DETAILS - USERNAME -\n")
        for self.am, self.p in enumerate(self.cfg['profiles'].keys()):
            if len(self.cfg['profiles'][self.p]['details']) > 1:
                self.dts = True
            else:
                self.dts = False
            print(f"{self.p}  :  {self.dts}  \t:  {self.cfg['profiles'][self.p]['user_name']}")
        
        print(f'\nTotal: {self.am+1}')
    
    def get_prof_names(self, args):
        try:
            for self.nm, self.u_32 in enumerate(self.get_local_32()):
                self.url = SteamID(self.u_32).community_url
                req = requests.get(self.url+'/ajaxaliases')
                if req.status_code:
                    self.user_name = json.loads(req.content)[0]['newname']
                    if not self.u_32 in self.cfg['profiles'].keys():
                        self.cfg['profiles'][self.u_32] = {'user_name': self.user_name, 'details': {}}
                    else:
                        self.cfg['profiles'][self.u_32]['user_name'] = self.user_name
                    
                    self.cfg['users'][self.user_name] = self.u_32

                    print(f'Found : {self.user_name} : {self.u_32}')

                else:
                    print(f'bad status request for {self.u_32} : {self.user_name}')
                
            print(f'Found {self.nm+1} accounts...')
            self.save_cfg()
        except Exception as error:
            pass

    def get_prof_uname(self, args):
        try:
            """ Prints profile's account name & copies it to clipboard, cmd :: user <user_name> """
            self.u_32 = self.cfg['users'][args[0]]
            self.en_user = self.cfg['profiles'][self.u_32]['details']['account_name']
            self.u_init = self.cfg['profiles'][self.u_32]['details']['u_init']
            self.user_name = self.decrypt(self.en_user, self.u_init)
            pyperclip.copy(self.user_name)
            print(f"{args[0]} : {self.user_name}\nCopied to clipboard!")
        except Exception as error:
            if type(error) == KeyError:
                print(f"{args[0]} does not have detail: {error} - otherwise {error} is not a user")
            else:
                print(f'cmd :: user <user_name>\nError: {error}')

    def get_prof_pwrd(self, args):
        try:
            """ Prints profile's password & copies it to clipboard, cmd :: user <user_name> """
            self.u_32 = self.cfg['users'][args[0]]
            self.en_pwrd = self.cfg['profiles'][self.u_32]['details']['password']
            self.p_init = self.cfg['profiles'][self.u_32]['details']['p_init']
            self.password = self.decrypt(self.en_pwrd, self.p_init)
            pyperclip.copy(self.password)
            print(f"{args[0]} : {self.password}\nCopied to clipboard!")
        except Exception as error:
            if type(error) == KeyError:
                print(f"{args[0]} does not have detail: {error} - otherwise {error} is not a user")
            else:
                print(f'cmd :: user <user_name>\nError: {error}')

    def prof_url(self, args):
        """ Return a profile's url, cmd :: uprof <user_name> """
        try:
            try:
                self.u_32 = self.cfg['users'][self.get_local_var(args[0])[args[0]]]
            except:
                self.u_32 = self.cfg['users'][args[0]]
            self.curl = SteamID(self.u_32).community_url
            print(self.curl, '\nCopied to clipboard!')
            pyperclip.copy(self.curl)
        except Exception as error:
            print(f"cmd :: uprof <user_name>\nError: {error}")

    def steam_login(self, args):
        """ Uses stored profile details to login to an account based off of username, cmd :: login <user_name> """
        try:
            try:
                self.un = self.cfg['users'][self.get_local_var(args[0])[args[0]]]
            except:
                self.un = self.cfg['users'][args[0]]
                
            self.en_user = self.cfg['profiles'][self.un]['details']['account_name']
            self.u_init = self.cfg['profiles'][self.un]['details']['u_init']
            self.en_pwrd = self.cfg['profiles'][self.un]['details']['password']
            self.p_init = self.cfg['profiles'][self.un]['details']['p_init']
            self.ukey = self.cfg['profiles'][self.un]['details']['ukey']

            if self.key_location != self.ukey:
                print(f'Encryption keys do not match!\nUSING: {self.key_location}\nUSED: {self.ukey}')
            
            else:
                self.user_name = self.decrypt(self.en_user, self.u_init)
                self.password = self.decrypt(self.en_pwrd, self.p_init)

                self.exe_path = os.path.join(self.cfg['steam_path'], "Steam.exe")


                if len(args) > 1:
                    try:
                        self.id = self.get_local_var(args[1])[args[1]]
                    except Exception as error:
                        self.id = args[1]

                    os.system(f'start "" "{self.exe_path}" /parameters -login {self.user_name} {self.password} -applaunch {self.id}')
                else:
                    os.system(f'start "" "{self.exe_path}" /parameters -login {self.user_name} {self.password}')

        except Exception as error:
            if type(error) == KeyError:
                print(f"username '{args[0]}' missing detail {error}")
            else:
                raise error
        

if __name__ == "__main__":
    pass
