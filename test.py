from stardict import load_dict


def test():
    dict_dir = 'stardict-dictd_anh-viet-2.4.2'
    file_stream = load_dict(dict_dir)

    # Test dict index
    dict_reader = file_stream['dict']
    for i in range(10):
        print(dict_reader.get_dict_by_index(i)[
              'm'].decode('utf-8', errors='ignore'))

    # Test dict word
    ifo_reader = file_stream['ifo']
    definitions = dict_reader.get_dict_by_word(r"'cellist")
    for definition in definitions:
        sametypesequence = ifo_reader.get_ifo('sametypesequence')
        if sametypesequence:
            print(definition[sametypesequence].decode(
                'utf-8', errors='ignore'))

    # read_ifo_file(dict_files['ifo'])
    # read_idx_file(dict_files['idx'])


test()
