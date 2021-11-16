import json

def load_statedict(fname = "state.json"):
    with open(fname, "r") as f:
        return json.load(f)

def update_statedict(state:dict, fname = "state.json"):
    with open(fname, "w") as f:
        json.dump(state, f, indent=4)
    return load_statedict()


    
