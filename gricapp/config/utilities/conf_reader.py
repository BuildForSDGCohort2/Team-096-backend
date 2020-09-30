"""
A simple conf reader.
For now, we just use dotenv and return a key.
"""

import environ
import os


def get_value(conf, key):
    "Return the value in conf for a given key"
    value = None
    env = environ.Env()
    try:
        env.read_env(conf)
        value = os.environ[key]
    except Exception as e:
        print('{} in get_value'.format(e))
        print('file: ', conf)
        print('key: ', key)

    return value
