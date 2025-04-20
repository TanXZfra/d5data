import requests
import csv
from time import sleep
from urllib.parse import urljoin
import os

BASE_URL="https://pultegroup.wd1.myworkdayjobs.com/wday/cxs/pultegroup/PGI/jobs"
CSV_FILE="jobs.csv"
HEADERS={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/json"
}

def safe_get(data, keys, default="N/A"):
    for key in keys:
        try:
            data=data[key]
        except (KeyError,TypeError):
            return default
    return data

def scrape_jobs():
    with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f)
        writer.writerow(["Title","Location","Posted","Application Link"])
        page=0
        total=None
        
        while True:
            payload={"appliedFacets": {},"limit":20,"offset":page*20,"searchText":""}
            try:
                response=requests.post(BASE_URL,json=payload,headers=HEADERS,timeout=15)
                response.raise_for_status()
                data=response.json()
                if total is None:
                    total=data.get("total",0)
                    if total==0:
                        break

                for job in data.get("jobPostings", []):
                    writer.writerow([
                        job.get("title", "N/A"),
                        job.get("locationsText", "N/A"),
                        job.get("postedOn", "N/A"),
                        urljoin("https://pultegroup.wd1.myworkdayjobs.com/PGI", 
                               job.get("externalPath", ""))
                    ])
                if(page+1)*20 >= total:
                    break
                page+=1
                sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"Request Failed:{str(e)}")
                break
            except KeyError as e:
                print(f"JSON Structure Error{str(e)}")
                break
            except Exception as e:
                print(f"Unknown Error{str(e)}")
                break

if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    os.chdir(current_dir)
    scrape_jobs()