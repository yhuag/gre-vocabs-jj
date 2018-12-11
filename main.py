from lxml import html
import requests
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import operator
import csv
import enchant

STOPWORDS = set(stopwords.words('english'))
ENGLISH = enchant.Dict("en_US")
vocabDict = dict()
customizedStopWords = [".", "ii"]


def encode(text):
    return text.replace(" ", "%20")


def getAllLinksFromASectionURLNumber(pageNum=16233):
    page = requests.get(
        'http://grev3.kmf.com/jijing/workbookdetail?sheet_id=' + str(pageNum))
    links = html.fromstring(page.text).xpath('//tr/td/a/@href')
    pageLinks = ["http://grev3.kmf.com/" + encode(link) for link in links]
    pageLinks = list(set(pageLinks))
    return pageLinks


def getQuestionFromALink(url):
    page = requests.get(url)
    question = html.fromstring(page.text).xpath(
        '//div[@class="mb20"]/text()')[0].strip("\n\r")
    return question


def getChoicesFromALink(url):
    page = requests.get(url)
    answers = html.fromstring(page.text).xpath(
        '//span[strong]/text()')
    answers = [ans.strip("\n\r") for ans in answers]
    return answers


def tokenizeSentence(sentence):
    wordTokens = word_tokenize(sentence.lower())
    filteredSentence = [w for w in wordTokens if not w in STOPWORDS]
    return filteredSentence


def addToVocabDict(li):
    for item in li:
        if item not in vocabDict:
            vocabDict[item] = 1
        else:
            vocabDict[item] += 1


def writePairListToFile(li):
    w = csv.writer(open("output.csv", "w"))
    for line in li:
        w.writerow([line[0], line[1]])


def filterPairList(li):
    response = []
    for line in li:
        vocab = line[0]
        if ENGLISH.check(vocab) and vocab not in customizedStopWords:
            response.append(line)
    return response


# Main
for num in range(16183, 16234):
    print("Crawling...", num)
    links = getAllLinksFromASectionURLNumber(num)
    for link in links:
        addToVocabDict(list(tokenizeSentence(getQuestionFromALink(link))))
        addToVocabDict(list(getChoicesFromALink(link)))

sortedVocabDict = sorted(vocabDict.items(), key=operator.itemgetter(1))
sortedVocabDict = filterPairList(sortedVocabDict)
writePairListToFile(sortedVocabDict)
print("DONE!")
