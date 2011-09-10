from datetime import datetime
from BeautifulSoup import BeautifulSoup
import json
import urllib2
import sqlite3
import sys
import re
import os

class GTInfo:
    def __init__(self):
        self.id = None
        self.title = None
        self.system = None
        
class SearchResult:
    def __init__(self):
        self.id = None
        self.title = None
        self.link = None
        self.boxart = None
        self.score = None
        self.votes = None
        self.media_count = None
        self.download_count = None
        self.systems = None
        self.release_date = None
        self.genres = None
        self.developer = None
        self.developer_link = None
        self.publisher = None
        self.publisher_link = None
        self.index = None
        self.page = None
        
    def __repr__(self):
        return repr([self.id, \
                    self.title, \
                    self.link, \
                    self.boxart, \
                    self.score, \
                    self.votes, \
                    self.media_count, \
                    self.download_count, \
                    self.systems, \
                    self.release_date, \
                    self.genres, \
                    self.developer, \
                    self.developer_link, \
                    self.publisher, \
                    self.publisher_link, \
                    self.index, \
                    self.page])
        
class GT:
    @staticmethod
    def search(query):
        url = get_search_url(query)
        html = get_html(url)
        if not html:
            return None
        soup = BeautifulSoup(html)
        i = 0
        page = 0
        allresults = []

        rows = soup.findAll("div", "search_content_row")
        for row in rows:
            res = SearchResult()
            
            thumb = row.find("div", "search_game_row_thumb")
            if thumb:
                img = thumb.find("img")
                if img:
                    res.boxart = "http://www.gametrailers.com/" + img["src"]
                   
            title = row.find("div", "gamepage_content_row_title")
            if title:
                res.title = title.text.strip()
                a = row.find("a")
                if a:
                    res.link = "http://www.gametrailers.com/" + a["href"]
                    res.id = res.link[res.link.rfind("/")+1 : res.link.rfind(".html")]
        
            details = row.find("div", "gamepage_content_row_text")
            process_details(res, details)
            
            score = row.find("div", "gamepage_content_score_number")
            if score:
                res.score = float(score.text.strip())
                
            votes = row.find("div", "gamepage_content_score_votes")
            if votes:
                res.votes = votes.text.replace("VOTES", "").replace("VOTE", "").strip()
                
            bottom = row.find("div", "gamepage_content_row_info_bottom")
            if bottom:
                match = re.search("Media:(?P<media>[0-9\,]+)Downloads:(?P<downloads>[0-9\,]+)", bottom.text.strip())
                if match:
                    res.media_count = int(match.group("media").strip().replace(",", ""))
                    res.download_count = match.group("downloads").strip().replace(",", "")
            
            res.index = i
            res.page = page
            i = i + 1
            allresults.append(res)
        return allresults
        
    @staticmethod
    def get_info(id):
        return None

def process_details(res, details):
    imgs = details.findAll("img")
    systems = []
    for img in imgs:
        match = re.search("images/plat_(?P<system>.+)_default.gif", img["src"])
        if match:
            systems.append(match.group("system").strip())
    res.systems = systems
    
    txt = str(details).strip()
    txt = re.sub("<b>([^:]+):</b>", '<div class="\\1">', txt)
    txt = txt.replace("</div>", "</div></div>")
    txt = txt.replace("<br />", "</div>")
    
    soup2 = BeautifulSoup(txt)
    divs = soup2.findAll("div")
    for div in divs:
        type = div["class"].strip()
        value = div.text.strip()
        process_game_detail(res, div, type, value)

def process_game_detail(res, div, type, value):
    a = div.find("a")
    if type == "Release Date":
        res.release_date = value
    elif type == "Genres":
        res.genres = value
    elif type == "Developer":
        res.developer = value
        if a and a["href"] and a["href"] != "":
            res.developer_link = a["href"].strip()
    elif type == "Publisher":
        res.publisher = value
        if a and a["href"] and a["href"] != "":
            res.publisher_link = a["href"].strip()
        
def get_html(url):
    try:
        request = urllib2.Request(url)
        request.add_header("User-Agent", "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101")
        html = urllib2.urlopen(request).read()
        return html
    except:
        print "Error accessing:", url
        return None
        
def get_search_url(query):
    return "http://www.gametrailers.com/search.php?s=%s" % query.replace(":", "").replace("-", "").replace("_", "").replace(" ", "+")
       
def main():
    if len(sys.argv) == 2:
        results = GT.search(sys.argv[1])
        for result in results:
            print result, "\n"
            print GT.get_info(result.id), "\n"
    
if __name__ == "__main__":
    main()
