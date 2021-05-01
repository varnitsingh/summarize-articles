from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
import csv
from pytrends.request import TrendReq
import sys

# Summary libraries
import heapq
import nltk

def update_progress(progress,status):
    barLength = 40 # Modify this to change the length of the progress bar
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
    sys.stdout.write(text)
    sys.stdout.flush()

def getTrends():
    '''
    Gets the latest trends from google trends page and returns them in a list.
    :rtype: list()
    '''
    pytrends = TrendReq(hl='en-US', tz=360)
    df = pytrends.trending_searches(pn='united_states')
    return list(df.iloc[:, 0])

def getArticles(keyword,pages=1):
    '''
    Searches on google for the keyword and returns the results for the first page.
    :param keyword: str() keyword to search on google.
    :param pages: int() number of pages of result to be returned.
    :rtype: list()
    '''
    results = search(keyword, tld='com', lang='en', num=pages, start=0, stop=None, pause=2.0)
    links = []
    count = 1
    for result in results:
        links.append(result)
        if count == 7:
            break
        count += 1
    return links

def extractText(browser,links):
    '''
    Returns summarized text from the links given.
    :param browser: selenium webdriver variable. Loaded before to save time.
    :param links: list() List of links to be scraped.
    :rtype: str()
    '''
    article_text = ''
    for link in links:
        browser.get(link)
        soup = BeautifulSoup(browser.page_source,'html.parser')
        
        # page = requests.get(link)
        # soup = BeautifulSoup(page.content,'html.parser')
        text = soup.text

        # Removing cookies,javascript and other sentances.
        sentances_ignore = []
        with open('ignore.txt','r',encoding='utf-8-sig') as readfile:
            sentances_ignore = readfile.readlines()
        for sentance in sentances_ignore:
            text.replace(sentance,'')
        article_text += text
        # article_text += text

    return article_text

def textSummarize(article_text):
    '''
    Summarizes the text and returns a 10 word summary for it.
    Check here for more info https://stackabuse.com/text-summarization-with-nltk-in-python/
    :param article_text: str() String of text to be summarized.
    :rtype: str()
    '''
    # Removing Square Brackets and Extra Spaces
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
    article_text = re.sub(r'\s+', ' ', article_text)

    # Removing special characters and digits
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

    sentence_list = nltk.sent_tokenize(article_text)

    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    try:
        maximum_frequncy = max(word_frequencies.values())
    except:
        return ' '

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(10, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)
    
    return summary

if __name__ == '__main__':
    # Initializing chromedriver
    opts = Options()
    opts.add_argument('--ignore-certificate-errors')
    opts.add_argument('--ignore-ssl-errors')
    opts.headless = False
    browser = webdriver.Chrome("./chromedriver",options=opts)

    # Getting trends
    trends = getTrends()
    with open('trends.txt','w',encoding='utf-8-sig') as writefile:
        for trend in trends:
            writefile.write(trend)
            writefile.write('\n')
    input("Look the trends and enter new ones in trends.txt.\nPress Enter to continue.")
    with open('trends.txt','r',encoding='utf-8-sig') as readfile:
        trends = readfile.readlines()
    for i in range(len(trends)):
        trends[i] = trends[i].replace('\n', '').strip()
    count = 1
    for trend in trends:
        update_progress(count/len(trends),f"{count}/{len(trends)} {trend}")
        links = getArticles(trend)
        article_text = extractText(browser,links)
        summary = textSummarize(article_text).split(' ')
        writefile_data = ''
        for i in range(len(summary)):
            writefile_data += summary[i] + ' '
            if i%15 == 0 and i != 0:
                writefile_data += '\n'
        with open(f'output\\{trend}.txt','w',encoding='utf-8-sig') as writefile:
            writefile.write(writefile_data)
        count += 1

    # Closing browser
    browser.close()