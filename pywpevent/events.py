import sys
import os
import inspect
import configparser
import importlib
import hashlib
from pywpevent.singleton import singleton

CONFIG_FILE = 'pywpevent.cfg'
DEFAULT_PLUGIN_DIR = 'pywpevent_plugins'


def hash_object(*args):
    return hashlib.md5(str(args).encode()).hexdigest()


@singleton
class EventCtrl:

    def __init__(self):
        self.__is_import = False
        self.__action_events = {}
        self.__filter_events = {}
        self.__caller_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.__config = configparser.RawConfigParser(allow_no_value=True)
        self.__plugin_dir = DEFAULT_PLUGIN_DIR

        config_path = self.__caller_path + '/' + CONFIG_FILE
        if os.path.exists(config_path):
            self.__config.read(config_path)

        for section in self.__config.sections():
            if section == 'plugin_dir_path':
                for option in self.__config.options(section):
                    if option == 'path':
                        self.__plugin_dir = self.__config.get(section, option)

            # if section != 'plugins':
            #     continue
            #
            # for option in self.__config.options(section):
            #     try:
            #         plugin = self.__config.getboolean(section, option)
            #         self.__enable_plugin[option] = plugin
            #     except ValueError:
            #         print('Config of {} is not support (should be in boolean)'.format(option))

    def initialize_plugin(self):
        if not self.__is_import:
            try:
                importlib.import_module(self.__plugin_dir)
            except ModuleNotFoundError as me:
                print(me)

            self.__is_import = True

    def add_action(self, name, func, priority):
        if not self.__action_events.get(name, None):
            func_hash = hash_object(func, priority)
            hash_name = name + '_' + func_hash
            self.__action_events[hash_name] = {'func': func, 'priority': priority}

    def add_filter(self, name, func, priority):
        if not self.__filter_events.get(name, None):
            func_hash = hash_object(func, priority)
            hash_name = name + '_' + func_hash
            self.__filter_events[hash_name] = {'func': func, 'priority': priority}

    def do_action(self, name, *args):
        sorted_actions = sorted(self.__action_events.items(), key=lambda kv: kv[1]['priority'])
        for k, v in sorted_actions:
            if k.split('_')[0] == name:
                func = v.get('func', None)
                if callable(func):
                    try:
                        func(*args)
                    except Exception as ex:
                        print(ex)

    def apply_filter(self, name, *args):
        sorted_filters = sorted(self.__filter_events.items(), key=lambda kv: kv[1]['priority'])
        result = None
        is_first = True
        for k, v in sorted_filters:
            if k.split('_')[0] == name:
                func = v.get('func', None)
                if callable(func):
                    try:
                        if not is_first:
                            args = list(args)
                            args[0] = result

                        result = func(*args)
                        is_first = False
                    except Exception as ex:
                        print(ex)

        return result

    # print(__file__)
    # print(sys.argv[0])
    # print(inspect.stack()[0][1])
    # print(sys.path[0])
    #
    # print(os.path.realpath(__file__))
    # print(os.path.abspath(__file__))
    # print(os.path.basename(__file__))
    # print(os.path.basename(os.path.realpath(sys.argv[0])))
    #
    # print(sys.path[0])
    # print(os.path.abspath(os.path.split(sys.argv[0])[0]))
    # print(os.path.dirname(os.path.abspath(__file__)))
    # print(os.path.dirname(os.path.realpath(sys.argv[0])))
    # print(os.path.dirname(__file__))
    #
    # print(inspect.getfile(inspect.currentframe()))
    #
    # print(os.path.abspath(inspect.getfile(inspect.currentframe())))
    # print(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
    #
    # print(os.path.abspath(inspect.stack()[0][1]))
    # print(os.path.dirname(os.path.abspath(inspect.stack()[0][1])))