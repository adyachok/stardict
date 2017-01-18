from stardict import load_dict, get_definitions
DEBUG = True


def test(dict_dir):
    if DEBUG:
        file_stream = load_dict(dict_dir)
    else:
        try:
            file_stream = load_dict(dict_dir)
        except Exception as e:
            print(e.args)
            file_stream = None

    if file_stream is None:
        print('Load dictionary {} failed'.format(dict_dir))
        return

    # Test dict index
    test_index = 0
    dict_reader = file_stream['dict']
    definition = dict_reader.get_dict_by_index(test_index)
    for k, v in definition.items():
        print(v.decode('utf-8', errors='ignore'))

    # Test dict word
    test_word = "hi"
    definitions = dict_reader.get_dict_by_word(test_word)
    for definition in definitions:
        for k, v in definition.items():
            print(v.decode('utf-8', errors='ignore'))

    # Print synonym
    syn_reader = file_stream['syn']
    if syn_reader:
        indexes = syn_reader.get_syn(test_word)
        idx_reader = file_stream['idx']
        for index in indexes:
            word_str, word_data_offset, word_data_size = idx_reader.get_index_by_num(
                index)
            print(word_str + ', ', end='')
        print('')

    # read_ifo_file(dict_files['ifo'])
    # read_idx_file(dict_files['idx'])


def test2(dict_dir):
    file_stream = load_dict(dict_dir)
    word_str = 'hello'
    definitions = get_definitions(word_str, file_stream)
    for definition in definitions:
        for k, v in definition.items():
            print(v.decode('utf-8', errors='ignore'))


# dict_dir = 'stardict-dictd_anh-viet-2.4.2'
dict_dir = 'stardict-Collins_Cobuild_5-2.4.2'
test2(dict_dir)
