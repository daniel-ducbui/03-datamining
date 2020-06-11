import re
import requests
from requests.exceptions import Timeout
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
import string
from html.parser import HTMLParser
import pickle

import unicodedata as ud

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stopwords.words('english')

urls_list = []

root_url = 'https://en.wikipedia.org/wiki/Web_mining'
res = requests.get(root_url, timeout=1)

urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(res.content))

urls_set = set(urls)
urls_list = list(urls_set)

def findLink(numOfLinks):
    print(len(urls_list))
    for u in urls_list:
        try:
            res1 = requests.get(u, timeout=1)
            print(urls_list.index(u), " - Found: ", u, end='')
            urls1 = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(res1.content))
            for url in urls1:
                if len(urls_set) > numOfLinks:
                    for _ in range(0, len(urls_set) - numOfLinks):
                        urls_set.pop()
                    return
                else:
                    urls_set.add(url)
                if url not in urls_list:
                    urls_list.append(url)
            print("...Done!")
        except Exception as e:
            print(">> Error: ", e, end='\n')
            pass

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Start tag:", tag)

    def handle_endtag(self, tag):
        print("End tag :", tag)

    def handle_data(self, data):
        print("Data  :", data)


parser = MyHTMLParser()
parser.feed('<html><head><title>Test</title></head>')

def text_filter(element):
    if element.parent.name in ['style', 'title', 'script', 'head', '[document]', 'class', 'a', 'li']:
        return False
    elif isinstance(element, Comment):
        '''Opinion mining?'''
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        '''space, return, endline'''
        return False
    return True

def wordList(url):
    r = requests.get(url, timeout=1)
    soup = BeautifulSoup(r.content, "html.parser")
    text = soup.findAll(text=True)
    filtered_text = list(filter(text_filter, text))
    word_list = []

    print("Fetching word list...")

    for line in filtered_text:
        words = line.split(' ')
        for word in words:
            word = word.lower()
            tmp_word = ''
            for w in word:
                try:
                    if w not in string.punctuation:
                        tmp_word += w
                except Exception as e:
                    print(">> Error: ", e)
            if tmp_word not in stopwords.words('english'):
                word_list.append(tmp_word)
    return word_list

def read_url(urls_list, data):
    print("Reading URL...")
    for url in urls_list:
        try:
            url_idx = urls_list.index(url)
            print("URL: ", url_idx, " - ", url)
            word_list = wordList(url)

            for word in word_list:
                if word.isalpha():
                    if data.get(word) is None:
                        data[word] = [[url_idx], 1]
                    else:
                        if url_idx not in data[word][0]:
                            data[word][0].append(url_idx)
                        data[word][1] += 1
        except Exception as e:
            print(">> Error: ", e)
            pass
        finally:
            time.sleep(1)
    return 1

data={}
print("Finding URLs...", end='')

findLink(10)
urls_list = list(urls_set)
print("Done!")
print(f"Total: {len(urls_set)} links.")

read_url(urls_list, data)
sorted_keys = sorted(data.keys())

with open("output.txt", "w",encoding="utf-8") as f:
    output_line = "Word".ljust(50) + "Frequency".ljust(30) + "URL_idx".ljust(20) + "\n"
    f.writelines(output_line)
    f.writelines('---------------------------------------------------------------------\n\n')
    for key in sorted_keys:
        output_string = str(key).ljust(20) + str(data[key][1]).ljust(15) + str(data[key][0]).ljust(15) + "\n"
        f.writelines(output_string)