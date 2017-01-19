import os
from stardict import Dictionary
from dictutils import find_dictionary_filepaths


class StarDict():

    def __init__(self, dictionary_settings):
        self.settings = dictionary_settings
        self._dictionaries = {}
        self._load_dictionaries()
        self._build_search_index()

    def _load_dictionaries(self):
        names = self.settings.find_enabled_dictionaries()
        for name in names:
            dictionary_path = os.path.join(
                self.settings.dicts_dirpath, name)
            self._load_dictionary(dictionary_path)

    def _load_dictionary(self, dictionary_path):
        try:
            dictionary = Dictionary(dictionary_path)
        except:
            dictionary = None
        if dictionary:
            self._dictionaries[dictionary.name] = dictionary

    def get_definitions_from_enabled_dictionaries(self, word_str, text_capture_mode=False):
        if text_capture_mode:
            names = self.settings.enabled_dictionaries_in_text_capture_mode
        else:
            names = self.settings.enabled_dictionaries_in_normal_mode

        enabled_dictionaries_definitions = []
        for name in names:
            dictionary = self._dictionaries[name]
            definitions = self.get_definitions(
                word_str, dictionary)
            enabled_dictionaries_definitions.append((dictionary, definitions))
        return enabled_dictionaries_definitions

    def get_definitions_from_one_dictionary(self, word_str, dictionary_name):
        dictionary = self._dictionaries[dictionary_name]
        return self.get_definitions(word_str, dictionary)

    def get_definitions(self, word_str, dictionary):
        definitions = dictionary.dict_reader.get_dict_by_word(word_str)
        if dictionary.syn_reader:
            indexes = dictionary.syn_reader.get_syn(word_str)
            for index in indexes:
                definition = dictionary.dict_reader.get_dict_by_index(index)
                definitions.append(definition)

        return definitions

    def install_dictionary(self, dictionary_path):
        self.settings.install_dictionary(dictionary_path)
        self._load_dictionary(dictionary_path)
        self._build_search_index()

    def _build_search_index(self):
        search_index = set()
        names = self.settings.enabled_dictionaries_in_index_group
        for name in names:
            dictionary = self._dictionaries[name]
            words = dictionary.idx_reader.get_all_words()
            search_index = search_index.union(words)
        self.search_index = sorted(search_index)


class DictionarySettings():

    def __init__(self, dicts_dirpath, settings_dirpath):
        self.dicts_dirpath = os.path.abspath(dicts_dirpath)
        self.settings_dirpath = os.path.abspath(settings_dirpath)
        self._load_settings()

    def _get_installed_dictionaries_settings(self):
        filename = 'installed_dictionaries_settings.txt'
        filepath = os.path.join(self.settings_dirpath, filename)
        if not os.path.exists(filepath):
            return []

        installed_dictionaries_settings = []
        with open(filepath, mode='r', encoding='utf-8') as f:
            for line in f:
                setting = tuple(line.split(sep=' '))
                installed_dictionaries_settings.append(setting)
        return sorted(installed_dictionaries_settings, key=lambda setting: setting[2])

    def _get_index_group_settings(self):
        filename = 'index_group_settings.txt'
        filepath = os.path.join(self.settings_dirpath, filename)
        if not os.path.exists(filepath):
            return []
        index_group_settings = []
        with open(filepath, mode='r', encoding='utf-8') as f:
            for line in f:
                setting = tuple(line.split(sep=' '))
                index_group_settings.append(setting)
        return sorted(index_group_settings, key=lambda setting: setting[2])

    def _get_text_capture_group_settings(self):
        filename = 'text_capture_group_settings.txt'
        filepath = os.path.join(self.settings_dirpath, filename)
        if not os.path.exists(filepath):
            return []
        text_capture_group_settings = []
        with open(filepath, mode='r', encoding='utf-8') as f:
            for line in f:
                setting = tuple(line.split(sep=' '))
                text_capture_group_settings.append(setting)
        return sorted(text_capture_group_settings, key=lambda setting: setting[2])

    def _load_settings(self):
        self.installed_dictionaries_settings = self._get_installed_dictionaries_settings()
        self.index_group_settings = self._get_index_group_settings()
        self.text_capture_group_settings = self._get_text_capture_group_settings()

        self.enabled_dictionaries_in_normal_mode = [setting[
            0] for setting in self.installed_dictionaries_settings if setting[1] != '0']
        self.enabled_dictionaries_in_index_group = [
            setting[0] for setting in self.index_group_settings if setting[1] != '0']
        self.enabled_dictionaries_in_text_capture_mode = [
            setting[0] for setting in self.text_capture_group_settings if setting[1] != '0']

    def find_enabled_dictionaries(self):
        enabled_dictionaries = set()
        enabled_dictionaries = enabled_dictionaries.union(
            self.enabled_dictionaries_in_normal_mode)
        enabled_dictionaries = enabled_dictionaries.union(
            self.enabled_dictionaries_in_index_group)
        enabled_dictionaries = enabled_dictionaries.union(
            self.enabled_dictionaries_in_text_capture_mode)
        return list(enabled_dictionaries)

    def install_dictionary(self, dictionary_path):
        filepaths = find_dictionary_filepaths(dictionary_path)
        if not filepaths:
            print('Install dictionary failed. Invalid dictionary')
            return False

        dictionary_name = os.path.basename(dictionary_path)
        for setting in self.installed_dictionaries_settings:
            if dictionary_name == setting[0]:
                print('This dictionary has been already installed')
                return False

        # TODO:Move file to dicts location

        order = len(self.installed_dictionaries_settings)
        with open('./settings/installed_dictionaries_settings.txt', mode='a', encoding='utf-8') as f:
            setting = '{} {} {}\n'.format(dictionary_name, 1, order)
            f.write(setting)

        with open('./settings/index_group_settings.txt', mode='a', encoding='utf-8') as f:
            setting = '{} {} {}\n'.format(dictionary_name, 1, order)
            f.write(setting)

        with open('./settings/text_capture_group_settings.txt', mode='a', encoding='utf-8') as f:
            setting = '{} {} {}\n'.format(dictionary_name, 1, order)
            f.write(setting)

        self._load_settings()
        print('Install dictionary successfully')
