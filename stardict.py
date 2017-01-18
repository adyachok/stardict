#!/usr/bin/python
# -*- coding: utf-8 -*-
import struct
import gzip
import os


class IfoFileException(Exception):
    """Exception while parsing the .ifo file.
    Now version error in .ifo file is the only case raising this exception.
    """

    def __init__(self, description="IfoFileException raised"):
        """Constructor from a description string.

        Arguments:
        - `description`: a string describing the exception condition.
        """
        self._description = description

    def __str__(self):
        """__str__ method, return the description of exception occured.

        """
        return self._description


class IfoFileReader(object):
    """Read infomation from .ifo file and parse the infomation a dictionary.
    The structure of the dictionary is shown below:
    {key, value}
    """

    def __init__(self, filename):
        """Constructor from filename.

        Arguments:
        - `filename`: the filename of .ifo file of stardict.
        May raise IfoFileException during initialization.
        """
        self._ifo = dict()
        with open(filename, "rU", encoding='utf-8') as ifo_file:
            self._ifo["dict_title"] = ifo_file.readline()  # dictionary title
            line = ifo_file.readline()  # version info
            key, equal, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # check version info, raise an IfoFileException if error encounted
            if key != "version":
                raise IfoFileException(
                    "Version info expected in the second line of {!r:s}!".format(filename))
            if value != "2.4.2" and value != "3.0.0":
                raise IfoFileException(
                    "Version expected to be either 2.4.2 or 3.0.0, but {!r:s} read!".format(value))
            self._ifo[key] = value
            # read in other infomation in the file
            for line in ifo_file:
                key, equal, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                self._ifo[key] = value
            # check if idxoffsetbits should be discarded due to version info
            if self._ifo["version"] == "3.0.0" and "idxoffsetbits" in self._ifo:
                del self._ifo["version"]

    def get_ifo(self, key):
        """Get configuration value.

        Arguments:
        - `key`: configuration option name
        Return:
        - configuration value corresponding to the specified key if exists, otherwise False.
        """
        if key not in self._ifo:
            return False
        return self._ifo[key]


class IdxFileReader(object):
    """Read dictionary indexes from the .idx file and store the indexes in a list and a dictionary.
    The list contains each entry in the .idx file, with subscript indicating the entry's origin index in .idx file.
    The dictionary is indexed by word name, and the value is an integer or a list of integers pointing to
    the entry in the list.
    """

    def __init__(self, filename, compressed=False, index_offset_bits=32):
        """
        Note: filename.dict and filename.dict.dz have different indices

        Arguments:
        - `filename`: the filename of .idx file of stardict.
        - `compressed`: indicate whether the .idx file is compressed.
        - `index_offset_bits`: the offset field length in bits.
        """
        # Open file
        if compressed:
            with gzip.open(filename, "rb") as index_file:
                self._content = index_file.read()
        else:
            with open(filename, "rb") as index_file:
                self._content = index_file.read()

        # Init
        self._offset = 0
        self._index = 0
        self._index_offset_bits = index_offset_bits
        self._word_idx = {}
        self._index_idx = []

        # Indexing
        for word_str, word_data_offset, word_data_size, index in self:  # Call __iter__ function
            self._index_idx.append(
                (word_str, word_data_offset, word_data_size))
            if word_str in self._word_idx:
                self._word_idx[word_str].append(len(self._index_idx) - 1)
            else:
                self._word_idx[word_str] = [len(self._index_idx) - 1]

        # Clean up
        del self._content
        del self._index_offset_bits
        del self._index

    def __iter__(self):
        """Define the iterator interface.

        """
        return self

    def __next__(self):
        """Define the iterator interface.

        """
        # EOF
        if self._offset == len(self._content):
            raise StopIteration
        # Read word_str => end with \0
        end = self._content.find(b'\x00', self._offset)
        word_str = self._content[self._offset: end].decode('utf-8')
        self._offset = end + 1

        # Read word_data_offset => 32 or 64 bits
        word_data_offset = 0
        if self._index_offset_bits == 32:
            word_data_offset, = struct.unpack(
                "!I", self._content[self._offset:self._offset + 4])
            self._offset += 4
        elif self._index_offset_bits == 64:
            word_data_offset, = struct.unpack(
                "!I", self._content[self._offset:self._offset + 8])
            self._offset += 8
        else:
            raise ValueError

        # Read word_data_size => always 32 bits
        word_data_size = 0
        word_data_size, = struct.unpack(
            "!I", self._content[self._offset:self._offset + 4])
        self._offset += 4

        # Increase index
        self._index += 1

        return (word_str, word_data_offset, word_data_size, self._index)

    def get_index_by_num(self, number):
        """Get index infomation of a specified entry in .idx file by origin index.
        May raise IndexError if number is out of range.

        Arguments:
        - `number`: the origin index of the entry in .idx file
        Return:
        A tuple in form of (word_str, word_data_offset, word_data_size)
        """
        if number >= len(self._index_idx):
            raise IndexError("Index out of range! Acessing the {:d} index but totally {:d}".format(
                number, len(self._index_idx)))
        return self._index_idx[number]

    def get_index_by_word(self, word_str):
        """Get index infomation of a specified word entry.

        Arguments:
        - `word_str`: name of word entry.
        Return:
        Index infomation corresponding to the specified word if exists, otherwise False.
        The index infomation returned is a list of tuples, in form of [(word_data_offset, word_data_size) ...]
        """
        if word_str not in self._word_idx:
            return []
        numbers = self._word_idx[word_str]
        indexes = []
        for number in numbers:
            indexes.append(self._index_idx[number][1:])
        return indexes


class SynFileReader(object):
    """Read infomation from .syn file and form a dictionary as below:
    {synonym_word: original_word_index}, in which 'original_word_index' could be a integer or
    a list of integers.

    """

    def __init__(self, filename):
        """Constructor.

        Arguments:
        - `filename`: The filename of .syn file of stardict.
        """
        self._syn = {}
        with open(filename, "rb") as syn_file:
            content = syn_file.read()
        offset = 0
        while offset < len(content):
            end = content.find(b'\x00', offset)
            if end == -1:
                break

            synonym_word = content[offset:end].decode('utf-8')
            offset = end + 1

            original_word_index, = struct.unpack(
                "!I", content[offset:offset + 4])
            offset += 4

            if synonym_word in self._syn:
                self._syn[synonym_word].append(original_word_index)
            else:
                self._syn[synonym_word] = [original_word_index]

    def get_syn(self, synonym_word):
        """

        Arguments:
        - `synonym_word`: synonym word.
        Return:
        If synonym_word exists in the .syn file, return the corresponding indexes, otherwise False.
        """
        if synonym_word not in self._syn:
            return []
        return self._syn[synonym_word]


class DictFileReader(object):
    """Read the .dict file, store the data in memory for querying.
    """

    def __init__(self, filename, dict_ifo, dict_index, compressed=False):
        """Constructor.

        Arguments:
        - `filename`: filename of .dict file.
        - `dict_ifo`: IfoFileReader object.
        - `dict_index`: IdxFileReader object.
        """
        self._dict_ifo = dict_ifo
        self._dict_index = dict_index
        self._compressed = compressed
        self._offset = 0
        if self._compressed:
            with gzip.open(filename, "rb") as dict_file:
                self._dict_file = dict_file.read()
        else:
            with open(filename, "rb") as dict_file:
                self._dict_file = dict_file.read()

    def get_dict_by_word(self, word):
        """Get the word's dictionary data by it's name.

        Arguments:
        - `word`: word name.
        Return:
        The specified word's dictionary data, in form of dict as below:
        {type_identifier: infomation, ...}
        in which type_identifier can be any character in "mlgtxykwhnrWP".
        """
        result = []
        indexes = self._dict_index.get_index_by_word(word)
        if not indexes:
            return result
        # sametypesequence = m => same type_identifier = m
        sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
        for index in indexes:
            self._offset = index[0]
            size = index[1]
            if sametypesequence:
                result.append(self._get_entry_sametypesequence(size))
            else:
                result.append(self._get_entry(size))
        return result

    def get_dict_by_index(self, index):
        """Get the word's dictionary data by it's index infomation.

        Arguments:
        - `index`: index of a word entrt in .idx file.'
        Return:
        The specified word's dictionary data, in form of dict as below:
        {type_identifier: infomation, ...}
        in which type_identifier can be any character in "mlgtxykwhnrWP".
        """
        word, offset, size = self._dict_index.get_index_by_num(index)
        self._offset = offset
        sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
        if sametypesequence:
            return self._get_entry_sametypesequence(size)
        else:
            return self._get_entry(size)

    def _get_entry(self, size):
        result = {}
        read_size = 0
        start_offset = self._offset
        while read_size < size:
            type_identifier = struct.unpack("!c")
            if type_identifier in "mlgtxykwhnr":
                result[type_identifier] = self._get_entry_field_null_trail()
            else:
                result[type_identifier] = self._get_entry_field_size()
            read_size = self._offset - start_offset
        return result

    def _get_entry_sametypesequence(self, size):
        start_offset = self._offset
        result = {}
        sametypesequence = self._dict_ifo.get_ifo("sametypesequence")
        for k in range(0, len(sametypesequence)):
            if sametypesequence[k] in "mlgtxykwhnr":
                if k == len(sametypesequence) - 1:
                    result[sametypesequence[k]] = self._get_entry_field_size(
                        size - (self._offset - start_offset))
                else:
                    result[sametypesequence[k]
                           ] = self._get_entry_field_null_trail()
            elif sametypesequence[k] in "WP":
                if k == len(sametypesequence) - 1:
                    result[sametypesequence[k]] = self._get_entry_field_size(
                        size - (self._offset - start_offset))
                else:
                    result[sametypesequence[k]] = self._get_entry_field_size()
        return result

    def _get_entry_field_null_trail(self):
        end = self._dict_file.find(b'\x00', self._offset)
        result = self._dict_file[self._offset:end]
        self._offset = end + 1
        return result

    def _get_entry_field_size(self, size=None):
        if size is None:
            size = struct.unpack("!I", self._dict_file[
                                 self._offset:self._offset + 4])
            self._offset += 4
        result = self._dict_file[
            self._offset:self._offset + size]
        self._offset += size
        return result


class Stardict():

    def __init__(self, dictionaries_dirpath):
        self._dictionary_readers = self._load_dictionaries(
            dictionaries_dirpath)

    def _load_dictionaries(self, dictionaries_dirpath):
        dictionaries_dirpath = os.path.abspath(dictionaries_dirpath)
        if not os.path.isdir(dictionaries_dirpath):
            return None
        dictionary_readers = {}
        for filename in os.listdir(dictionaries_dirpath):
            if os.path.isfile(filename):
                continue
            dictionary_path = os.path.join(dictionaries_dirpath, filename)
            dictionary_reader = self._load_dictionary(dictionary_path)
            if not dictionary_reader:
                continue
            dictionary_readers[dictionary_reader['name']] = dictionary_reader
        return dictionary_readers

    def _load_dictionary(self, dictionary_path):
        filepaths = self._get_dictionary_filepaths(dictionary_path)
        if not filepaths:
            return None
        if not('ifo' in filepaths and 'idx' in filepaths and 'dict' in filepaths):
            return None

        dictionary_name = os.path.basename(dictionary_path)
        ifo_reader = IfoFileReader(filepaths['ifo'])
        idx_reader = IdxFileReader(filepaths['idx'], compressed=filepaths[
            'idx.gz'], index_offset_bits=32)
        dict_reader = DictFileReader(
            filepaths['dict'], ifo_reader, idx_reader, compressed=filepaths['dict.dz'])
        syn_reader = SynFileReader(
            filepaths['syn']) if 'syn' in filepaths else None

        return dict(name=dictionary_name, ifo=ifo_reader, idx=idx_reader, dict=dict_reader, syn=syn_reader)

    def _get_dictionary_filepaths(self, dictionary_path):
        dictionary_path = os.path.abspath(dictionary_path)
        if not os.path.isdir(dictionary_path):
            return None

        filepaths = {}
        for filename in os.listdir(dictionary_path):
            # Get real file extension
            name = filename
            is_compressed = False
            while True:
                name, ext = os.path.splitext(name)
                if ext != '.dz' and ext != '.gz':
                    break
                is_compressed = True

            filepath = os.path.join(dictionary_path, filename)

            if ext == '.ifo':
                filepaths['ifo'] = filepath
            elif ext == '.idx':
                filepaths['idx'] = filepath
                filepaths['idx.gz'] = is_compressed
            elif ext == '.dict':
                filepaths['dict'] = filepath
                filepaths['dict.dz'] = is_compressed
            elif ext == '.syn':
                filepaths['syn'] = filepath

        return filepaths

    def get_definitions_from_all_dictionaries(self, word_str):
        definitions = {}
        for dictionary_reader in self._dictionary_readers.values():
            dictionary_definitions = self._get_definitions(
                word_str, dictionary_reader)
            definitions[dictionary_reader['name']] = dictionary_definitions
        return definitions

    def get_definitions_from_one_dictionary(self, word_str, dictionary_name):
        if not (dictionary_name in self._dictionary_readers):
            return None
        dictionary_reader = self._dictionary_readers[dictionary_name]
        definitons = self._get_definitions(word_str, dictionary_reader)
        return definitons

    def _get_definitions(self, word_str, dictionary_reader):
        dict_reader = dictionary_reader['dict']
        definitions = dict_reader.get_dict_by_word(word_str)

        syn_reader = dictionary_reader['syn']
        if syn_reader:
            indexes = syn_reader.get_syn(word_str)
            for index in indexes:
                definition = dict_reader.get_dict_by_index(index)
                definitions.append(definition)

        return definitions
