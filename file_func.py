import os
import subprocess
import sys
import pickle
import json


def dir_exists(dir_path):
    return os.path.isdir(dir_path)


def file_exists(file_path):
    return os.path.isfile(file_path)


# Rename Directory
def rename_dir(old_dir, new_dir):
    if os.path.exists(old_dir):
        os.rename(old_dir, new_dir)


# Make Directory
def make_dir(dir_path):
    if not dir_exists(dir_path):
        os.makedirs(dir_path)


def make_file(file_path, data=None, overwrite=False):
    if not file_exists(file_path) or overwrite:
        with open(file_path, 'w') as file:
            if data is not None and data != '':
                file.write(data + '\n')


def delete_file(file_path):
    if file_exists(file_path):
        os.remove(file_path)


def file_to_set(file_path):
    return_set = set()
    if file_exists(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                return_set.add(line.replace('\n', ''))
    return return_set


def set_to_file(item_set, file_path, append=False):
    mode = 'a' if append else 'w'
    with open(file_path, mode) as file:
        for item in sorted(item_set):
            file.write(item + '\n')


def pickle_dump_to_file(obj, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(obj, file)


# noinspection PyBroadException
def pickle_load_from_file(file_path):
    rv = None
    try:
        if file_exists(file_path):
            with open(file_path, 'rb') as file:
                rv = pickle.load(file)
    except:
        pass
    return rv


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError


def json_dump_to_file(obj, file_path):
    with open(file_path, 'w') as file:
        # print(obj, type(obj), isinstance(obj, datetime))
        json.dump(obj, file, indent=4, ensure_ascii=False, separators=(',', ': '), default=json_serial)


# noinspection PyBroadException
def json_load_from_file(file_path):
    rv = None
    try:
        if file_exists(file_path):
            with open(file_path, 'r') as file:
                rv = json.load(file)
    except:
        pass
    return rv


def open_path(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def file_size(file_path):
    if file_exists(file_path):
        return os.path.getsize(file_path)
    else:
        return 0


def get_file_path(path, *paths):
    return os.path.join(path, *paths)
