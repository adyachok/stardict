from stardict import load_dict, get_definitions
DEBUG = True


def test(dict_path):
    if DEBUG:
        file_stream = load_dict(dict_path)
    else:
        try:
            file_stream = load_dict(dict_path)
        except Exception as e:
            print(e.args)
            file_stream = None

    if file_stream is None:
        print('Load dictionary {} failed'.format(dict_path))
        return

    # Test dict index
    test_index = 0
    dict_reader = file_stream['dict']
    definition = dict_reader.get_dict_by_index(test_index)
    for k, v in definition.items():
        print(v.decode('utf-8', errors='ignore'))


def test2(dict_path):
    file_stream = load_dict(dict_path)
    word_str = 'hello'
    definitions = get_definitions(word_str, file_stream)
    for definition in definitions:
        for k, v in definition.items():
            print(v.decode('utf-8', errors='ignore'))


# dict_path = 'stardict-dictd_anh-viet-2.4.2'
dict_path = 'stardict-Collins_Cobuild_5-2.4.2'
test2(dict_path)
