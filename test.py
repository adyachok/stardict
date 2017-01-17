from stardict import load_dict
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
    for k, v in dict_reader.get_dict_by_index(test_index).items():
        print(v.decode('utf-8', errors='ignore'))

    # Test dict word
    test_word = "'cause"
    ifo_reader = file_stream['ifo']
    definitions = dict_reader.get_dict_by_word(test_word)
    for definition in definitions:
        for k, v in definition.items():
            print(v.decode('utf-8', errors='ignore'))
    # Print synonym
    syn_reader = file_stream['syn']
    if syn_reader:
        print(syn_reader.get_syn(test_word))

    # read_ifo_file(dict_files['ifo'])
    # read_idx_file(dict_files['idx'])


# dict_dir = 'stardict-dictd_anh-viet-2.4.2'
dict_dir = 'stardict-Collins_Cobuild_5-2.4.2'
test(dict_dir)
