from os import path, mkdir, listdir
import configparser

project_root = path.split(path.dirname(path.abspath(__file__)))[0]


def default_config(config):
    """Put here the content of the default configuration file"""
    config['vosk'] = {'project_name': 'vosk',
                      'model_name': '',
                      'models_url': 'https://alphacephei.com/vosk/models'}
    config['fastpunct'] = {'project_name': 'fastpunct',
                           'model_name': '',
                           'models_url': 'https://github.com/notAI-tech/fastPunct'}


class Settings:
    __config = configparser.ConfigParser()
    __config_path = path.join(project_root, "settings")

    def __init__(self):
        # Check if the settings folder already exist
        if not path.exists(self.__config_path):
            mkdir(self.__config_path)
        # Check if the config file already exist else fill it with default settings
        if "config" in listdir(self.__config_path):
            self.__config.read(path.join(self.__config_path, "config"))
            self.__add_default_params()
        else:
            default_config(self.__config)
            self.write_config()

    def __getitem__(self, sections):
        """Get the item according to the section(s) given\n
            Example :\n
                > settings ["vosk", "model_name"]\n
                   "model_name" \n
                > settings ["vosk"]\n
                   {"model_name" : "model_name, \n
                    "" : ""}"""
        if isinstance(sections, tuple):
            section, property = sections
            return self.__config[section][property]
        else:
            return self.__config[sections]

    def __setitem__(self, tuple, data):
        """Set the item according to the tuple given\n
            Example : settings ["vosk", "model_name"] = "model_name" """
        section, property = tuple
        self.__config[section][property] = data

    def write_config(self):
        """Write the config to the file"""
        with open(path.join(self.__config_path, "config"), 'w') as configfile:
            self.__config.write(configfile)

    def __add_default_params(self):
        """If the default settings are modified in term of slots,
        then apply it to the existing config\n
        NOTE: it only works with 1 or 2 dimensions dictionnary"""
        default_dict = {}
        default_config(default_dict)
        stored_dict = dict(self.__config._sections)
        for key1 in default_dict.keys():
            if isinstance(default_dict[key1], dict):
                for key2 in default_dict[key1].keys():
                    if key1 in stored_dict.keys() and key2 in stored_dict[key1]:
                        default_dict[key1][key2] = stored_dict[key1][key2]
            else:
                if key1 in stored_dict.keys():
                    default_dict[key1] = stored_dict[key1]
        self.__config.read_dict(default_dict)
        self.write_config()


def dl_model_path(project):
    """Return the DeepLearning model path corresponding to the poject.R

    Args:
        project (dict): Project informations

    Returns:
        str: path to the model directory
    """
    model_name = project["model_name"]
    project_name = project["project_name"]

    def error(e):
        print(f"  Could not access deeplearning model '{model_name}' of project '{project_name}'.")
        print("  " + e)
        return None
    if not model_name:
        error("Model name empty")
    path_models = path.join(project_root, "models")
    if not path.exists(path_models):
        mkdir(path_models)
        error("Model folder unexisting. Creating one at : " + path_models)
    path_model = path.join(path_models, project_name, model_name)
    if path.exists(path_model):
        if (listdir(path_model) != []):
            print(f"Model '{model_name}' of project '{project_name}' found")
            return path_model
        else:
            error("Model seems empty. Check the contents of : " + path_model)
    else:
        if not path.exists(path.join(path_models, project_name)):
            mkdir(path.join(path_models, project_name))
            print(f"Project is unexisting in {path_models}. Creating the folder.")
        error("Model unexisting. Please")
