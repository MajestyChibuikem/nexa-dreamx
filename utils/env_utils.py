import os

def get_env_variable(key, default=None):
    """
    Retrieve an environment variable, returning a default value if not found.
    
    :param key: The name of the environment variable
    :param default: The default value to return if the variable is not set
    :return: The value of the environment variable or the default value
    """
    return os.getenv(key, default)
