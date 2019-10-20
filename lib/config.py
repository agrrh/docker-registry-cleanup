import yaml


class Config(object):
    """Load configuration."""

    def __init__(self, path='./config.yml'):
        with open(path) as fp:
            for k, v in yaml.load(fp, Loader=yaml.BaseLoader).items():
                setattr(self, k, v)
