import requests
import concurrent.futures as cf
import re
from bs4 import BeautifulSoup
from TagGenerator import TagGenerator
import time as timer
import creds

proxies = creds.proxies

class DenniknSk:
    def GetIndexPage(self):
        url = "https://dennikn.sk/"
        payload = ""
        response = requests.request("GET", url, data=payload, headers=self.headers, proxies=proxies)

        self.GetUrls(response)

    def GetUrls(self, response : requests.Response):
        doc = BeautifulSoup(response.text, "html.parser")
        articles = doc.find(class_="tiles").find_all("article")
        for article in articles:
            try:
                aherf = article.find("h3").a.get("href")
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
        r = requests.get(url, headers=self.headers, proxies=proxies)
        self.responses.append(r)

    def CleanBody(self, body : BeautifulSoup):
            """
            removes certain unwanted tags from dom
            """
            for i in body.find_all("form"):
                i.decompose()
            for i in body.find_all(class_="e_lock"):
                i.decompose()
            for i in body.find_all("footer"):
                i.decompose()
            for i in body.find_all("script"):
                i.decompose()
            for i in body.find_all("style"):
                i.decompose()
            for i in body.find_all("iframe"):
                i.decompose()
            for i in body.find_all("figure"):
                i.decompose()
            for i in body.find_all(class_="e_langs__switcher"):
                i.decompose()
            return body

    def Parse(self, response : requests.Response):
        url = response.url
        doc = BeautifulSoup(response.text, "html.parser")
        try:
            title = doc.find("h1").get_text().strip()
        except:
            title = ""
        try:
            time = doc.find("time").get_text().strip()
        except:
            time = ""
        try:
            article_body = doc.find(class_="a_single__post")
            body_tags = []
            for i in self.CleanBody(article_body).children:
                try:
                    body_tags.append(i.get_text().strip())
                except:
                    pass
            body = " ".join(body_tags)
            body = re.sub("\n", " ", body)
        except:
            pass
        try:
            lead = doc.find(class_="b_single_e").get_text().strip()
        except:
            try:
                lead = "..." + re.search(r"\b.{120,250}\b", body).group().strip() + "..." #re.search(r"(\b[A-Z].*?\.)", body).group().strip()
            except:
                lead = ""
        try:
            tags_div = doc.find(class_="e_terms_scroll")
            tags_raw = tags_div.find_all(class_="e_terms_tag")
            tags = [tag.get_text().strip().replace(",", "") for tag in tags_raw]
        except:
            tags = []
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
        self.headers =  {
            "authority": "dennikn.sk",
            "accept-encoding": "gzip, deflate",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6",
            "cache-control": "no-cache",
            "cookie": 'cabrio=A; browser_id=789f09e0-5b2b-4e82-8099-e29a27671c4e; remp_session_id=320d8238-4678-46a0-909e-695c37c15009; dn_os_minute_prompt=12; lastarticleseen=1670059731202; campaigns={"2EeKvc":{"sn":0,"ct":12,"ut":1670059731},"oXOX71":{"sn":0,"ct":12,"ut":1670059731},"wMAnxq":{"sn":0,"ct":12,"ut":1670059731},"WiXJF9":{"sn":0,"ct":12,"ut":1670059731},"133mEo":{"sn":0,"ct":12,"ut":1670059731},"g4hTDy":{"sn":0,"ct":12,"ut":1670059731},"eatcUx":{"sn":0,"ct":12,"ut":1670059731},"LHmFVp":{"sn":0,"ct":12,"ut":1670059731},"hWNNGu":{"sn":0,"ct":12,"ut":1670059731},"wPgpgb":{"sn":0,"ct":12,"ut":1670059731},"MhMie9":{"sn":0,"ct":12,"ut":1670059731},"mC6tiv":{"sn":0,"ct":12,"ut":1670059731},"Du2GiE":{"sn":3,"ct":2,"vi":"RQdHdf","bi":"Yqd4IQ","ut":1669725775},"jMi8EY":{"sn":0,"ct":10,"ut":1670059731},"t7HqiW":{"sn":18,"ct":0,"vi":"RQdHdf","bi":"Yqd4IQ","ut":1670059732}}; campaigns_session={"t7HqiW":{"sn":18,"ut":1670059732}}',
            "pragma": "no-cache",
            "referer": "https://napunk.dennikn.sk/",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
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
    DenniknSk()
    end = timer.perf_counter()
    print(end-start)