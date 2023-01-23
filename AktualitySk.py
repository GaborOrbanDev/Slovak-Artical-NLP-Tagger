import requests
import concurrent.futures as cf
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
# import asyncio
# import httpx
from TagGenerator import TagGenerator
import time as timer
import creds

proxies = creds.proxies

@dataclass
class ApiParam:
    name : str
    url : str
    query : dict
    payload : str

class AktualitySk:
    """
    Pipeline of working:
    init -> GetHeadPart -> GetUrls -> CallApis -> Call -> RunScrapers -> Scrape -> RunParsers -> Parse -> CleanBody
    """
    def GetHeadPart(self):
        """
        This method requests the static first part of the webpage and calls self.GetUrls() method
        """
        url = "https://www.aktuality.sk/"
        headers = {
            "cookie": "_sp_sampled_user=false; ea_uuid=202105251749334816108171; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CPifGEAPifGEAAGABCENCqCsAP_AAAAAAA6gHFgRJApEQSVBIGhoIJEAAAACwQQIAWACCBAAAAABAAAAKAAQEAAgAAAABAACAAAAABBAAAAgAAEAAAAAIAAAAAAIAAAAgAAAAQAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAgAAAAAAAQAAAAAAAAAAAAAAAAIAAAERkAIAJgC8xgAEA6oiACAdUQABABIEgIgAZAA4ACAAGAAMgAaQBEAEUAJgATwAqgCEAFKALcAfoA_wF5gMkCAAgASAHVDQAQDqioAQATAF5igAIB1R0BQADIAHAAQAAwABkADSAIgAigBMACeAFUAMQApQBYgC3AH6AP8AiwC8wGSAOLHAAwALgAkAOqQgDgAZACYAFUAMQApQBYgD_IAAQDqkoBQAGQAOAAwACIAEwAKoAYgBSgC3AXmSABAAXAOqUgJAAZAA4ACAAGAAMgAaQBEAEUAJgATwAqgBiAFKALEAW4A_QCLALzAZIUACAAXABIAdUA_4A.YAAAAAAAAAAA; consentUUID=796cc38d-ce09-43a3-bf43-a80322e5d1de_13; consentDate=2022-11-15T08:59:00.252Z; __gads=ID=fa4ff87064ddec35-2244da26b0ce00da:T=1668502740:RT=1668502740:S=ALNI_MZIptzwwcBHJr3vZ-HFA70s8RnmFw; _ga=GA1.1.2009910658.1668502740; _hjSessionUser_1443765=eyJpZCI6Ijk1ZTE3NWZkLWZlZTctNWIxMy05NjQwLWEzM2IzNTEzOGJiMCIsImNyZWF0ZWQiOjE2Njg1MDI3NDI1MTAsImV4aXN0aW5nIjp0cnVlfQ==; _ga_JCWC9QRWV6=GS1.1.1668509457.2.1.1668510403.60.0.0; abusr=27.6258795; campaigns={}; browser_id=298e57d3-73dc-4752-8866-8c6769b490a1; __gfp_64b=-TURNEDOFF; _pbjs_userid_consent_data=237620875615572; _gcl_au=1.1.742599301.1669724871; _hjSessionUser_1219637=eyJpZCI6IjYwMDVlNmI0LTEyZDgtNTVhMi05NGVlLTY1MWVhN2NiMDg1NyIsImNyZWF0ZWQiOjE2Njk3MjQ4Njk5MTIsImV4aXN0aW5nIjp0cnVlfQ==; adblock-disabled=0; __gpi=UID=00000b819378e68c:T=1668502740:RT=1669894219:S=ALNI_Mbq3mCMY6Ir00_sVeHeupIBjGTfgQ; TS01dc1985=015c8fe40e7f04c8ce6e0bb2309eaea82e5ee84b4282f1f00049482d4e85726ef17c3d7d8c830ebba6466b1e614eae2d8f3c67b755; _sp_id.3aa3=2fb9f0d398f45e22.1669724867.5.1669911581.1669894225; _sp_ses.3aa3=*; ats_ri=fp_ms=1668502723566&ri=202105251749334816108171&model=202105251749334816108171&models=eyJhdHNfcmkiOiIyMDIxMDUyNTE3NDkzMzQ4MTYxMDgxNzEifQ%3D%3D&ttl_ms=3600000&expires_ms=1669915181258&version=1669911581.322; _hjIncludedInSessionSample=0; _hjSession_1219637=eyJpZCI6ImQzNTU1M2I0LWE2NjgtNGU5NC1hNDZhLWJkNDZmMTExNzdlNCIsImNyZWF0ZWQiOjE2Njk5MTE1ODMwMzEsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _ga_GNW0LC86SZ=GS1.1.1669911584.6.0.1669911584.60.0.0; _ga_4PRCPPJEJZ=GS1.1.1669911584.5.0.1669911584.60.0.0; cto_bundle=0RzJ5V9Db2M0UCUyQkNLUmc0bU1lVDlRS05KRCUyQkVpJTJGVGdXN0klMkJDeGkybU9YbCUyQnJpazJMdWE5JTJGZCUyRlZGUjBWTmRTdG51M2N5dTZiUWVlQWRZU011R1BHNDRYOExRRjklMkJWY3FCdCUyRnBJdFAlMkZOSXlHVU5MODklMkY4QkNnY3BQdUFGTm1lZDlGNDYlMkJrOGVKNTA5OWZUaFFiMkJ1SmxDM2clM0QlM0Q; TS858467e6029=08e5e65cc0ab280092c5c46080dfef26778415441b88b63e19774c5597eff39678bc840e41de66975b7aaa28c6d9e264; TScb90d893027=08e5e65cc0ab20000f05f40f515be2f0198fbc293347886368345e400911f47e7cc5ffefe894feeb08753e23e311300022908fef51f35dd9c04e8af9744f4ba100406f97d257f8b42dcabc5a5e09b36b0d67258a904b38f9a9f8164c6fb96801",
            "authority": "www.aktuality.sk",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6",
            "cache-control": "no-cache",
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

        response = requests.request("GET", url, headers=headers, proxies=proxies)

        self.GetUrls(response)

    def GetUrls(self, response : requests.Response):
        """
        Get urls from the static part of the website
        """
        doc = BeautifulSoup(response.text, "html.parser")

        div_main_content = doc.find(class_="main-content")
        urls = div_main_content.find_all(class_="item-link")
        for url in urls:
            self.urls.append(url.get("href"))

        div_most_read_articles = doc.find(class_="most-read-articles-list")
        for url in div_most_read_articles.find_all("a"):
            self.urls.append(url.get("href"))

    def CallApis(self):
            """
            Loops through self.ApiParams and with ThreadPoolExecutor() calls with threading the given apis
            """
            with cf.ThreadPoolExecutor() as exec:
                exec.map(self.Call, self.ApiParams)

    def Call(self, params : ApiParam):
        """
        Calls Api with given parameters and append parsed response to self.urls 
        """
        response = requests.request("GET", params.url, data=params.payload, headers=self.headers, params=params.query, proxies=proxies)
        responseList = response.json()
        for item in responseList:
            self.urls.append(item["url"])

    #region: Async version -- can work / fast proxy may needed
    # async def Scrape(self, client, url):
    #         await asyncio.sleep(2)
    #         r = await client.get(url)
    #         return r
            
    # async def RunScrapers(self):
    #     async with httpx.AsyncClient(proxies='http://gfxbmkor-rotate:7xq8rjut8w8o@149.6.162.2:80') as client:
    #         tasks = [self.Scrape(client, url) for url in self.urls]
    #         responses = await asyncio.gather(*tasks)
    #         return responses
    #endregion

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
        r = requests.get(url, proxies=proxies)
        self.responses.append(r)
            
    def CleanBody(self, body : BeautifulSoup):
        """
        removes certain unwanted tags from dom
        """
        for i in body.find_all(class_="object-image"):
            i.decompose()
        for i in body.find_all(class_="info-wrapper"):
            i.decompose()
        for i in body.find_all(class_="premium-blocker-container"):
            i.decompose()
        for i in body.find_all(class_="thanks-blocker-container"):
            i.decompose()
        for i in body.find_all(class_="embed-wrapper"):
            i.decompose()
        for i in body.find_all(class_="article-object"):
            i.decompose()
        for i in body.find_all(class_="ring-embed-wrapper"):
            i.decompose()
        for i in body.find_all("script"):
            i.decompose()
        for i in body.find_all("style"):
            i.decompose()
        for i in body.find_all(class_="rs-advertisement"):
            i.decompose()
        return body

    def Parse(self, response : requests.Response):
        if "https://www.aktuality.sk/" not in response.url or sum(1 for i in response.url if i=="/")==4:
            return
        url = response.url
        doc = BeautifulSoup(response.text, "html.parser")
        try:
            title = doc.h1.get_text()
        except:
            title = ""
        try:
            publication_time = doc.find(class_="date").get_text().strip()
            time = re.search(r"[0-9].{1,}", publication_time).group()
        except:
            time = ""
        try:
            lead = doc.find(class_="introtext").get_text()
        except:
            lead = ""
        try:
            tags_div = doc.find(class_="more-themes")
            tags_raw = tags_div.find_all("a")
            tags = [tag.get_text().strip().replace(",", "") for tag in tags_raw]
        except:
            tags = []
        try:
            article_body = doc.select("#articleContent")[0] #doc.find(class_="fulltext")
            bodyTags = []
            for i in self.CleanBody(article_body).children:
                try:
                    bodyTags.append(i.get_text().strip())
                except:
                    pass
            body = " ".join(bodyTags)
            body = re.sub("\n", " ", body)
        except:
            return
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
        #region: request assign variables
        self.headers = {
            "cookie": "_sp_sampled_user=false; ea_uuid=202105251749334816108171; _sp_enable_dfp_personalized_ads=true; euconsent-v2=CPifGEAPifGEAAGABCENCqCsAP_AAAAAAA6gHFgRJApEQSVBIGhoIJEAAAACwQQIAWACCBAAAAABAAAAKAAQEAAgAAAABAACAAAAABBAAAAgAAEAAAAAIAAAAAAIAAAAgAAAAQAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAgAAAAAAAQAAAAAAAAAAAAAAAAIAAAERkAIAJgC8xgAEA6oiACAdUQABABIEgIgAZAA4ACAAGAAMgAaQBEAEUAJgATwAqgCEAFKALcAfoA_wF5gMkCAAgASAHVDQAQDqioAQATAF5igAIB1R0BQADIAHAAQAAwABkADSAIgAigBMACeAFUAMQApQBYgC3AH6AP8AiwC8wGSAOLHAAwALgAkAOqQgDgAZACYAFUAMQApQBYgD_IAAQDqkoBQAGQAOAAwACIAEwAKoAYgBSgC3AXmSABAAXAOqUgJAAZAA4ACAAGAAMgAaQBEAEUAJgATwAqgBiAFKALEAW4A_QCLALzAZIUACAAXABIAdUA_4A.YAAAAAAAAAAA; consentUUID=796cc38d-ce09-43a3-bf43-a80322e5d1de_13; consentDate=2022-11-15T08:59:00.252Z; __gads=ID=fa4ff87064ddec35-2244da26b0ce00da:T=1668502740:RT=1668502740:S=ALNI_MZIptzwwcBHJr3vZ-HFA70s8RnmFw; _ga=GA1.1.2009910658.1668502740; _hjSessionUser_1443765=eyJpZCI6Ijk1ZTE3NWZkLWZlZTctNWIxMy05NjQwLWEzM2IzNTEzOGJiMCIsImNyZWF0ZWQiOjE2Njg1MDI3NDI1MTAsImV4aXN0aW5nIjp0cnVlfQ==; _ga_JCWC9QRWV6=GS1.1.1668509457.2.1.1668510403.60.0.0; abusr=27.6258795; campaigns={}; browser_id=298e57d3-73dc-4752-8866-8c6769b490a1; __gfp_64b=-TURNEDOFF; _pbjs_userid_consent_data=237620875615572; _gcl_au=1.1.742599301.1669724871; _hjSessionUser_1219637=eyJpZCI6IjYwMDVlNmI0LTEyZDgtNTVhMi05NGVlLTY1MWVhN2NiMDg1NyIsImNyZWF0ZWQiOjE2Njk3MjQ4Njk5MTIsImV4aXN0aW5nIjp0cnVlfQ==; adblock-disabled=0; __gpi=UID=00000b819378e68c:T=1668502740:RT=1669894219:S=ALNI_Mbq3mCMY6Ir00_sVeHeupIBjGTfgQ; _sp_ses.3aa3=*; ats_ri=fp_ms=1668502723566&ri=202105251749334816108171&model=202105251749334816108171&models=eyJhdHNfcmkiOiIyMDIxMDUyNTE3NDkzMzQ4MTYxMDgxNzEifQ%3D%3D&ttl_ms=3600000&expires_ms=1669915181258&version=1669911581.322; _hjIncludedInSessionSample=0; _hjSession_1219637=eyJpZCI6ImQzNTU1M2I0LWE2NjgtNGU5NC1hNDZhLWJkNDZmMTExNzdlNCIsImNyZWF0ZWQiOjE2Njk5MTE1ODMwMzEsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; TS01dc1985=015c8fe40e6bda2d052afe3d6b5b04b5075cada8fe6aab02530794f309213793fcdcead5fdda648eabf5b04ae19e93d5d313fa7f34; azTrackerTestCookie=2; remp_session_id=78a09abd-b7c1-41f5-bb2c-911f18f75b0f; _sp_id.3aa3=2fb9f0d398f45e22.1669724867.5.1669912192.1669894225; cto_bundle=cJIj419Db2M0UCUyQkNLUmc0bU1lVDlRS05KRDJvWHFTTlJsOXppUm9lamNwcDZUOGJpdnVaJTJGaFhGQ2pkWmZDMWxIeXJYWCUyRkJhSG9HJTJCckJoMzl0cU81RGdsa1BHSTBPS0duWnU0QVFQeEdqJTJGTklXd3l0NVIwOHR6d1ZTcHYxbHVsbTAxREtucVExeUtzc1pCS1NOMXdScjJOOU1RJTNEJTNE; _ga_4PRCPPJEJZ=GS1.1.1669911584.5.1.1669912195.55.0.0; _ga_GNW0LC86SZ=GS1.1.1669911584.6.1.1669912195.55.0.0; TS858467e6029=08e5e65cc0ab280014799ee1176f61eff899548e37a691891a72fe975e1f5bcce49657f79552565a5090a5eec4ae576d; TScb90d893027=08e5e65cc0ab2000a7d408d6f83797e2ef39818a928c59a80088dc26286b3cc0e64e465d6e4f3fc0087dddba7511300099d2d54fc49fee1b519e3355ca1162b6d9a83ef52a218d66a19bb3ebf1358a788298df6e9796c21a04498b7be4d6ff18",
            "authority": "www.aktuality.sk",
            "accept": "application/json, text/plain, */*",
            "accept-language": "sk-SK,sk;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://www.aktuality.sk/",
            "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "x-security-request": "required"
        }
        self.ApiParams = [
            ApiParam(name = "comment",
                     url="https://www.aktuality.sk/_s/api/homepage/articles/commentary",
                     query={"limit":"3","allowedLabels\\[\\]":"plus","excludedArticles\\[\\]":""},
                     payload=""),
            ApiParam(name="crosspromo",
                     url="https://www.aktuality.sk/_s/api/homepage/articles/crosspromo",
                     query={"limit":"8","excludedArticles\\[\\]":""},
                     payload=""),
            ApiParam(name="pr",
                     url="https://www.aktuality.sk/_s/api/homepage/articles/pr",
                     query={"limit":"2"},
                     payload=""),
            ApiParam(name="most_read",
                     url="https://www.aktuality.sk/_s/api/homepage/articles-most-read",
                     query={"projects[]":["sport","zive","diva","najmama","recepty","receptysk"],"limit":"5"},
                     payload=""),
            ApiParam(name="video",
                     url="https://www.aktuality.sk/_s/api/homepage/articles/video",
                     query={"limit":"4","excludedArticles\\[\\]":""},
                     payload=""),
            ApiParam(name="podcast",
                     url="https://www.aktuality.sk/_s/api/homepage/articles/podcast",
                     query={"limit":"4","excludedArticles\\[\\]":""},
                     payload=""),
            ApiParam(name="newscast",
                     url="https://www.aktuality.sk/_s/api/homepage/articles-most-read",
                     query={"limit":"5","projects[]":"newscast"},
                     payload=""),
            ApiParam(name="ecology",
                     url= "https://www.aktuality.sk/_s/api/homepage/articles/aktuality-ecology",
                     query={"limit":"4"},
                     payload=""),
            ApiParam(name="travel",
                     url= "https://www.aktuality.sk/_s/api/homepage/articles/aktuality-travel",
                     query={"limit":"4"},
                     payload=""),
            ApiParam(name="culture",
                     url= "https://www.aktuality.sk/_s/api/homepage/articles/aktuality-culture",
                     query={"limit":"4"},
                     payload=""),           
        ]
        #endregion

        #region: get urls
        self.urls = []
        self.GetHeadPart()
        self.CallApis()
        self.urls = list(set(self.urls)) #filtering out duplicates
        #endregion

        #region: get articles
        # self.responses = asyncio.run(self.RunScrapers())
        self.responses = []
        self.RunScrapers()
        #endregion
        
        #region: run parser
        self.results = []
        self.RunParsers()
        #endregion

if __name__ == "__main__":
    start = timer.perf_counter()
    AktualitySk()
    end = timer.perf_counter()
    print(end-start)