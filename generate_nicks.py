from random import *
import requests

def generateNicks(n):
    f = open("tss_nicks.txt", "a")
    nick = ""
    w1parems = (("sp", "s????*"), ("max", "1000"), ("md", "p"))
    w1opts = requests.get('https://api.datamuse.com/words', params=w1parems).json()[400:]
    for w in w1opts:
        if not "tags" in w or not "n" in w["tags"]:
            w1opts.remove(w)
    count = 0
    while True:
        try:
            w1 = choice(w1opts)["word"].capitalize()
            w2parems = (("sp", "s??*"), ("max", "200"), ("rel_jjb", w1))
            w2opts = requests.get('https://api.datamuse.com/words', params=w2parems).json()
            w2 = choice(w2opts)["word"].capitalize()
            w3parems = (("sp", "t??*"), ("max", "200"), ("rel_jjb", w1))
            w3opts = requests.get('https://api.datamuse.com/words', params=w3parems).json()
            w3 = choice(w3opts)["word"].capitalize()
            nick = w3 + w2 + w1 + "\n"
            f.write(nick)
            count += 1
            if count >= n:
                break
        except:
            do_nothing_expression = 0
    f.close()

for i in range(100):
    print(i * 100)
    generateNicks(100)
