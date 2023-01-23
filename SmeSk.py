import requests
import concurrent.futures as cf
import re
from bs4 import BeautifulSoup
from TagGenerator import TagGenerator
import time as timer
import creds

proxies = creds.proxies

class SmeSk:
    def GetIndexPage(self):
        url = "https://www.sme.sk/"
        response = requests.request("GET", url, proxies=proxies)
        self.GetUrls(response)

    def GetUrls(self, response : requests.Response):
        doc = BeautifulSoup(response.text, "html.parser")
        articles = doc.find_all(class_="js-pvt-title")
        for article in articles:
            try:
                aherf = article.get("href")
                self.urls.append(aherf)
            except:
                continue
    
    def RunScrapers(self):
        """
        Calls self.Scrape method on self.urls
        """
        with cf.ThreadPoolExecutor() as exec:
            exec.map(self.Scrape, self.urls)

    def Scrape(self, url):
        """
        Scrape given urls and appends respons to self.responses
        """
        response = requests.get(url, proxies=proxies)
        self.responses.append(response)

    def CleanBody(self, body : BeautifulSoup):
            """
            removes certain unwanted tags from dom
            """
            for i in body.find_all(class_="share-box"):
                i.decompose()
            for i in body.find_all(class_="artemis-ad-position"):
                i.decompose()
            for i in body.find_all(class_="article-item-wrapper"):
                i.decompose()
            for i in body.find_all(class_="social-widget-twitter"):
                i.decompose()
            for i in body.find_all(class_="js-deep-container-promo-piano-article"):
                i.decompose()
            for i in body.find_all(class_="piano-promo"):
                i.decompose()
            for i in body.find_all(class_="js-ab-test-topic-after-forum"):
                i.decompose()
            for i in body.find_all(id="sme-promobox-teaser"):
                i.decompose()
            for i in body.find_all(class_="js-deep-container-article-topic-box"):
                i.decompose()
            for i in body.find_all(class_="article-published"):
                i.decompose()
            for i in body.find_all(class_="topic-box"):
                i.decompose()
            for i in body.find_all(class_="js-ab-test-topic-after-forum"):
                i.decompose()
            for i in body.find_all(class_="article-epilogue"):
                i.decompose()
            for i in body.find_all("iframe"):
                i.decompose()
            for i in body.find_all("figure"):
                i.decompose()
            for i in body.find_all("script"):
                i.decompose()
            for i in body.find_all("style"):
                i.decompose()
            return body

    def Parse(self, response : requests.Response):
        if "https://sportnet.sme.sk" in response.url:
            return

        url = response.url
        doc = BeautifulSoup(response.text, "html.parser")
        try:
            title = doc.find("h1").get_text().strip()
        except:
            title = ""
        try:
            time = doc.find(class_="article-heading").find("strong").get_text()
        except:
            time = ""
        try:
            tags_div = doc.find(class_="next-topics")
            tags_raw = tags_div.find_all("a")
            tags = [tag.get_text().strip() for tag in tags_raw]
        except:
            tags = []
        try:
            article = doc.find("article")
            body_cleanded = self.CleanBody(article)
            body_tags = []
            for i in body_cleanded.children:
                try:
                    body_tags.append(i.get_text().strip())
                except:
                    pass
            body = " ".join(body_tags)
            body = re.sub("\n", " ", body)
        except:
            return
        try:
            lead = body_cleanded.find("p").get_text().strip()
        except:
            lead = ""
        try:
            tags = TagGenerator(text=body, tags=tags).tags
        except Exception as ex:
            #print(ex)
            pass

        return {"url": url, "title": title, "datetime": time, "lead": lead, "tags": tags}

    def RunParsers(self):
        with cf.ThreadPoolExecutor() as exec:
            results = exec.map(self.Parse, self.responses)
        results = [r for r in results if r != None]
        self.results = results

    def __init__(self):
        self.headers = {
            "authority": "www.sme.sk",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6",
            "cache-control": "no-cache",
            "cookie": "_pbjs_userid_consent_data=6683316680106290; _pubcid=c0069282-d816-4c9f-bc02-bbb53017729e; _lr_env_src_ats=false; pbjs-unifiedid=%7B%22TDID_LOOKUP%22%3A%22FALSE%22%2C%22TDID_CREATED_AT%22%3A%222022-11-29T12%3A37%3A48%22%7D; _et_hb_4_ff=0; _lr_retry_request=true; cto_bundle=Ia_buF9KVDRneSUyQjBsQTJLVk5Uc1ZlRFpCMnJTeHdicnRHRFVvb0x1NmZleDhpVCUyQnRYUXp4d0ZRUFVxT2tpd0E0YzhuejU2cmRFZDM1alVra09VbUlLQUlweEhUYnMzVG9Va3JEYjdtd1klMkI0TkRtViUyRmNsZ2dpQmxKQk5FcDBoM21TM3ZWa096VDVBaDM1cVFqcTc5Tkx5RHNmZyUzRCUzRA; cto_bidid=N2N7Ol9NZkxxbFl6TXFMcll3OUxqMUdoUFpieEN3azE0eHFYMmRBd1l3Q2xqbm04ZVRBa2wlMkZVcXY1aWhqeWo5cUV5TWZtYWdKcGYxcHFnJTJGZmhGU2tpVVppV21xUHdJWlFtMUVZTFBEOWtuSExkZUklM0Q; notification_block_date=Sat Dec 03 2022 10:14:00 GMT+0100 (kÃ¶zÃ©p-eurÃ³pai tÃ©li idÅ‘)",
            "pragma": "no-cache",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        self.urls = []
        self.responses = []
        self.results = []
        self.GetIndexPage()
        self.RunScrapers()
        self.RunParsers()

if __name__ == "__main__":
    start = timer.perf_counter()
    SmeSk()
    end = timer.perf_counter()
    print(end-start)