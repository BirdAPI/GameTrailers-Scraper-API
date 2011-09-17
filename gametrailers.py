from BeautifulSoup import BeautifulSoup
from pprint import pprint
import urllib2
import sqlite3
import sys
import re

class GTInfo:
    def __init__(self):
        self.id = None
        self.link = None
        self.title = None
        self.system = None
        self.boxart = None
        self.release_date = None
        self.summary = None
        self.systems = None
        self.genres = None
        self.developer = None
        self.developer_link = None
        self.publisher = None
        self.publisher_link = None
        self.gt_score = None
        self.review_link = None
        self.user_score = None
        self.user_count = None
        self.esrb = None
        self.esrb_reason = None
        self.official_site = None
        self.banner_image = None  
        
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
    def get_info(id, system, user_count=None):
        info = GTInfo()
        info.id = id
        info.link = "http://www.gametrailers.com/game/%s.html" % id   
        info.system = system
        info.user_count = user_count
        
        html = get_html(info.link)
        if not html:
            return None
        soup = BeautifulSoup(html)
        
        title = soup.find("h1", "GameTitle")
        if title:
            info.title = title.text.strip()
        
        description = soup.find("div", "Description")
        if description:
            info.summary = description.text.strip()
            
        gametop_container = soup.find("div", "gametop_container")
        if gametop_container:
            img = gametop_container.find("img")
            if img:
                info.banner_image = img["src"]
        
        gamepage_boxart = soup.find("img", "gamepage_boxart")
        if gamepage_boxart:
            info.boxart = gamepage_boxart["src"]
        
        general_info = soup.find("div", "gamepage_gameinfo")
        if general_info:
            process_general_info(info, general_info)
        
        ratings = soup.findAll("div", "RatingWrapper")
        if ratings and len(ratings) == 2:
            info.gt_score = ratings[0].text.strip()
            info.user_score = ratings[1].text.strip()
        
        review = soup.find("a", "WatchReview")
        if review:
            info.review_link = "http://www.gametrailers.com" + review["href"]
        
        return info

def process_general_info(info, general_info):
    systems = []
    platforms = general_info.findAll("a", "gamepage_platform")
    for platform in platforms:
        match = re.search("gamepage_platform_(?P<plat>[^ ]+)", platform["class"])
        if match:
            systems.append(match.group("plat").strip())
    info.systems = systems
    
    bolds = general_info.findAll("span", "gamepage_gameinfo_bold_text")
    normals = general_info.findAll("span", "gamepage_gameinfo_normal_text")
    
    for i in range(len(bolds)):
        type = bolds[i].text.replace(":", "").strip()
        value = normals[i].text.strip()
        process_game_detail(info, normals[i], type, value)
    
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
    elif type == "Gamesite":
        if a and a["href"] and a["href"] != "":
            res.official_site = a["href"].strip()
    elif type == "ESRB":
        match = re.search("(?P<esrb>[^&]+)&nbsp;\((?P<reason>[^\)]+)\)", value)
        if match:
            res.esrb = match.group("esrb").strip()
            res.esrb_reason = match.group("reason").strip()
        else:
            res.esrb = value
            
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
            pprint(vars(result))
            print ""
            pprint(vars(GT.get_info(result.id, result.systems[0], result.votes)))
            print ""
    
if __name__ == "__main__":
    main()
