# Summarize Articles
Scrapes top trends from google trends and creates a summary for each trend by parsing the articles.

Summarized articles are saved in output folder. The sentances to be ignored are saved in ignore.txt, these usually contains sentances about cookies or javascript.

## Tech stack
* Python 3.8.6
* pytrends==4.7.3 for scraping google trends.
* Selenium for scraping text from articles.
* nltk==3.6.2 for summarization of articles.

## Todo
* Collecting article text with scrapy + selenium for faster crawling.
* Multiple language support.