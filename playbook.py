from ruamel import yaml
from pathlib import Path
import json
from loggable import Loggable
import traceback


class Playbook (Loggable):
    PLAYBOOK_VMEMPEROR_CONF = 'vmemperor.conf'

    @staticmethod
    def get_playbooks():
        from vmemperor import opts
        playbooks = []
        directory = Path(opts.ansible_dir)
        for item in directory.iterdir():
            p = Playbook(item.name)
            playbooks.append(p)
        return playbooks


    def __init__(self, playbook_name):
        from vmemperor import opts
        self.init_log()
        directory = Path(opts.ansible_dir)
        playbook_dir = directory.joinpath(playbook_name)
        try:
            if not playbook_dir.is_dir():
                raise ValueError(f'"{playbook_dir.absolute()}" does not exist or not a directory!')

            config_file = playbook_dir.joinpath('vmemperor.conf')
            if not config_file.is_file():
                raise ValueError(f'"{config_file.absolute()}" does not exist or not a file!')

            with open(config_file) as file:
                config_dict = yaml.safe_load(file)

                self.config = config_dict

            # Find variables
            keys = self.config['variables'].keys()
            self.variables_locations = {}
            self.vars={}
            for var in ('host_vars', 'group_vars'):
                self.variables_locations[var] = []
                host_vars_file = playbook_dir.joinpath(var, 'all')
                if not host_vars_file.is_file():
                    continue
                with open(host_vars_file) as file:
                    host_vars = yaml.safe_load(file)

                self.vars[var] = host_vars
                for key in keys:
                    try:
                        self.config['variables'][key] = {**self.config['variables'][key],
                                               **{'value': host_vars[key]}}
                        self.variables_locations[var].append(key)
                    except KeyError:
                        continue

            # Check if playbook file exists
            playbook_file = playbook_dir.joinpath(self.config['playbook'])
            if not playbook_file.is_file():
                raise ValueError("Playbook file {0} does not exist".format(playbook_file.absolute()))


            self.config['playbook_dir'] = playbook_dir.absolute()
            self.config['id'] = playbook_dir.name
        except Exception as e:
            self.log.error(f"Exception: {e}")
            self.log.error(f"At {traceback.print_exc()}")

    def get_name(self):
        return self.config['name']

    def get_requires(self):
        return self.config['requires']

    def get_playbook_file(self):
        '''
        This is relative path to playbook file
        :return:
        '''
        return self.config['playbook']

    def get_description(self):
        return self.config.get('description', '')

    def get_playbook_dir(self):
        return self.config['playbook_dir']

    def get_config(self):
        return self.config

    def get_variables(self):
        return self.config['variables']

    def get_id(self):
        return self.config['id']

    def get_variables_locations(self):
        return self.variables_locations



class PlaybookEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Playbook):
            return o.get_config()

        return super().default(o)






