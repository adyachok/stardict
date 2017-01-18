from stardict import Stardict, DictionarySettings
from dictutils import find_installed_dictionaries_paths

DICTS_DIRPATH = './dicts'
SETTINGS_DIRPATH = './settings'


def test(word_str):
    settings = DictionarySettings(DICTS_DIRPATH, SETTINGS_DIRPATH)
    stardict = Stardict(settings)

    all_dictionaries_definitions = stardict.get_definitions_from_all_dictionaries(
        word_str)
    for dictionary_name, definitions in all_dictionaries_definitions.items():
        print(dictionary_name)
        for definition in definitions:
            for k, v in definition.items():
                print(v.decode('utf-8', errors='ignore'))


def install_dictionaries():
    settings = DictionarySettings(DICTS_DIRPATH, SETTINGS_DIRPATH)

    installed_dictionaries_paths = find_installed_dictionaries_paths(DICTS_DIRPATH)
    for dictionary_path in installed_dictionaries_paths:
        settings.install_dictionary(dictionary_path)


# install_dictionaries()
test('hello')
