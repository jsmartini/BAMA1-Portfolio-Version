import json


data = json.load(open("test.json", "r"))

print(data)

print(type(data))
data["flag"] = 1

json.dump(data, open("test.json", "w"))

data = json.load(open("test.json", "r"))

print(data)

