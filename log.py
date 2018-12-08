import os
import json
import logging.config


def setup_logging(
        default_path='logging.json',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        # replace $HOME in the logfile
        home = os.environ['HOME']
        if home is not None:
            add_suffix(config, 'filename', home, '$HOME')
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def add_suffix(adict, k, suffix, replace_string):
    for key in adict.keys():
        if key == k:
            adict[key] = adict[key].replace(replace_string, suffix)
        elif type(adict[key]) is dict:
            add_suffix(adict[key], k, suffix, replace_string)
