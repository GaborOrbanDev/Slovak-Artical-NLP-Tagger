import time as timer

start = timer.perf_counter()

from AktualitySk import AktualitySk
from DenniknSk import DenniknSk
from SmeSk import SmeSk
import concurrent.futures
import pandas as pd


class Main:
    def ExecuteScrapers(self):
        with concurrent.futures.ThreadPoolExecutor() as exec:
            for i_scraper in exec.map(lambda scraper: scraper(), self.scrapers):
                self.executed_scrapers.append(i_scraper)

    def CreateOutput(self):
        dataframes : list[pd.DataFrame] = []
        for e_scraper in self.executed_scrapers:
            dataframes.append(pd.DataFrame(e_scraper.results))

        output_csv = pd.concat(dataframes)
        output_csv.to_csv("crawling_results.csv", sep=";", index=False)

    def __init__(self):
        self.scrapers = [AktualitySk, DenniknSk, SmeSk]
        self.executed_scrapers = []

        self.ExecuteScrapers()
        self.CreateOutput()

if __name__ == "__main__":
    Main()
    end = timer.perf_counter()
    print(f"Crawler has run successfully and generated crawling_results.csv - running time: {end-start:.2f}s")