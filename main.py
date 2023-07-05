# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from tqdm import tqdm

url_pre = "https://www.netlib.org/fdlibm/"

index = requests.get(url_pre + "index").content.decode("utf8")

for line in tqdm(index.splitlines()):
    if len(line) > 0:
        path = line.split("\t")[1].split("/")[1]
        file = requests.get(url_pre + path).content
        with open("./out/fdlibm/" + path, "wb") as f:
            f.write(file)

'''
with open("py017.jpeg", "wb") as f:
    f.write(r.content)
'''
