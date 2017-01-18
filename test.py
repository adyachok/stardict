from stardict import Stardict


def test(word_str):
    dictionaries_dirpath = './'
    stardict = Stardict(dictionaries_dirpath)
    all_dictionaries_definitions = stardict.get_definitions_from_all_dictionaries(
        word_str)
    for dictionary_name, definitions in all_dictionaries_definitions.items():
        print(dictionary_name)
        for definition in definitions:
            for k, v in definition.items():
                print(v.decode('utf-8', errors='ignore'))


test('hello')
