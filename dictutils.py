import os


def find_dictionary_filepaths(dictionary_path):
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

    # Not a valid dictionary
    if not('ifo' in filepaths and 'idx' in filepaths and 'dict' in filepaths):
        return None

    return filepaths


def find_installed_dictionaries_paths(dicts_dirpath):
    dicts_dirpath = os.path.abspath(dicts_dirpath)
    if not os.path.isdir(dicts_dirpath):
        return []
    installed_dictionaries = []
    for filename in os.listdir(dicts_dirpath):
        if os.path.isfile(filename):
            continue
        dictionary_path = os.path.join(dicts_dirpath, filename)
        filepaths = find_dictionary_filepaths(dictionary_path)
        if filepaths:
            installed_dictionaries.append(dictionary_path)
    return installed_dictionaries
