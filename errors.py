class ConfigurationError(Exception):
    def __init__(self, reason):
        super('%s! Please ensure the configuration in config.py is correct' % reason)