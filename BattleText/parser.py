import requests
import json

sortedWords = {
    'q':[],
    'w':[],
    'e':[],
    'r':[],
    't':[],
    'y':[],
    'u':[],
    'i':[],
    'o':[],
    'p':[],
    'a':[],
    's':[],
    'd':[],
    'f':[],
    'g':[],
    'h':[],
    'j':[],
    'k':[],
    'l':[],
    'z':[],
    'x':[],
    'c':[],
    'v':[],
    'b':[],
    'n':[],
    'm':[]
}

len = 12
opaf5 = '-' * (len - 1)
#print(opaf5)

for char in sortedWords:
    r = requests.get(f"https://www.crosswordsolver.org/solve/{char}{opaf5}")
    str = r.text
    opa = str.find("Matching Words")
    l = str.find("<span>", opa) + 6
    r = str.find("</span>", opa) - 8
    count = int(str[l : r])
    print(char, count)
    for it in range(0, count, 10):
        r = requests.get(f"https://www.crosswordsolver.org/solve/{char}{opaf5}/{it}")
        str = r.text
        stop = 0
        for opa in range(10):
            stop = str.find("<div class='word'>", stop) + 19
            word = str[stop : str.find("</div>", stop)]
            if word.isalpha():
                sortedWords[char].append(word.lower())


f = open("testingWords.txt", 'r')
temp = json.loads(f.read())
f.close()

for char in sortedWords:
    for word in temp[char]:
        sortedWords[char].append(word)



#print(json.dumps(sortedWords, sort_keys=True, indent=4))
f = open("testingWords.txt", 'w')
f.write(json.dumps(sortedWords))
f.close()
