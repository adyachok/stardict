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
    dict_reader = file_stream['dict']
    for i in range(10):
        for k, v in dict_reader.get_dict_by_index(i).items():
            print(v.decode('utf-8', errors='ignore'))

    # Test dict word
    ifo_reader = file_stream['ifo']
    definitions = dict_reader.get_dict_by_word(r"hello")
    for definition in definitions:
        sametypesequence = ifo_reader.get_ifo('sametypesequence')
        if sametypesequence:
            print(definition[sametypesequence].decode(
                'utf-8', errors='ignore'))

    # read_ifo_file(dict_files['ifo'])
    # read_idx_file(dict_files['idx'])


# dict_dir = 'stardict-dictd_anh-viet-2.4.2'
dict_dir = 'stardict-Collins_Cobuild_5-2.4.2'
test(dict_dir)
