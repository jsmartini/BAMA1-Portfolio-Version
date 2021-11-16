import toml

global API
global CONFIG

with open("configuration.toml", "r") as config:
    CONFIG = toml.load(config)

with open("api.toml", 'r') as api:
    API = toml.load(api)

global RUNTIME_STATES
RUNTIME_STATES = {
    "ARMED": False,
    "CTRL_OFF": False,
    "ADCS": False
}

