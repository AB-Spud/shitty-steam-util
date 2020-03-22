from util_functions import UtilFunctions
from shlex import split
import logging

class CommandParse(UtilFunctions):
    def __init__(self, key_name):
        super().__init__(key_name)
        self.cmds = {
        'help': self.help, 'exit': self.exit,'clear': self.clear, 'login': self.steam_login, 'logout': self.kill_steam, 'gprofs': self.get_prof_names, 'rmd': self.remove_details,
        'get': self.display_var, 'set': self.set_var , 'rmv': self.remove_var,'profs': self.display_profiles, 'add': self.add_prof_details, 'backup': self.backup_profiles,
        'copy': self.copy, 'uprof': self.prof_url, 'pwrd': self.get_prof_pwrd, 'user': self.get_prof_uname, 'init': self.data_init
        }
    

    def call_cmd(self,cmd , *args):
        try:
            self.cmds[cmd](args[0])
        except Exception as error:
            if type(error) == KeyError:       
                print(f"Unkown command or missing data {error} type 'help' for a list of commands.")
            else:
                raise error


if __name__ == "__main__":
    keyn = str(input("Input the name of your key file (if you don't have one just enter a name): "))
    cmdp = CommandParse(keyn)
    cmdp.clear([])
    while True:
        ar = str(input(">>> "))
        args = split(ar)
        if len(args) < 1: args = ['clear', '']
        cmdp.call_cmd(args[0],args[1:])