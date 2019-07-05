from dictutils import find_installed_dictionaries_paths
from app import StarDict, DictionarySettings
import time

from html_output.html_convertor import build_report

DICTS_DIRPATH = './dicts'
SETTINGS_DIRPATH = './settings'


def test():
    settings = DictionarySettings(DICTS_DIRPATH, SETTINGS_DIRPATH)
    stardict = StarDict(settings)
    text = []

    word_str_list = ['hallo', 'happy', 'Tier', 'Elefant']
    for word_str in word_str_list:
        enabled_dictionaries_definitions = stardict.get_definitions_from_enabled_dictionaries(
            word_str)
        for dictionary, definitions in enabled_dictionaries_definitions:
            print(dictionary.name)
            for definition in definitions:
                for k, v in definition.items():
                    d = v.decode('utf-8', errors='ignore')
                    d = tuple(d.split('\n', 1))
                    text.append(d)
    build_report(text)


def install_dictionaries():
    settings = DictionarySettings(DICTS_DIRPATH, SETTINGS_DIRPATH)

    installed_dictionaries_paths = find_installed_dictionaries_paths(
        DICTS_DIRPATH)
    for dictionary_path in installed_dictionaries_paths:
        settings.install_dictionary(dictionary_path)


install_dictionaries()
test()
