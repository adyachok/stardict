from stardict import Stardict


def test():
    dictionaries_dirpath = './'
    stardict = Stardict(dictionaries_dirpath)
    word_str = 'hello'
    all_dictionaries_definitions = stardict.get_definitions_from_all_dictionaries(
        word_str)
    for dictnary_name, definitions in all_dictionaries_definitions.items():
        for definition in definitions:
            for k, v in definition.items():
                print(v.decode('utf-8', errors='ignore'))


test()
