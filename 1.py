from bs4 import BeautifulSoup
import cloudscraper
from re import findall
from time import sleep
import pycurl
from sys import stderr as STREAM

# Accepting Sendcm URL from User
url = input("Enter Sendcm URL (default is https://send.cm/aecdgu9xisny): ") or "https://send.cm/aecdgu9xisny"

if "send.cm" not in url:
    print("\nURL Entered is not Supported!\n")
    exit()

base_url = "https://send.cm/"
client = cloudscraper.create_scraper(allow_brotli=False)
hs = {"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"}

def is_sendcm_folder_link(url):
    return (
        f"{base_url}s/" in url
        or f"{base_url}?sort" in url
        or f"{base_url}?sort_field" in url
        or f"{base_url}?sort_order" in url
    )

is_sendcm_folder = is_sendcm_folder_link(url)
if is_sendcm_folder:
    done = False
    page_no = 0
    while not done:
        page_no += 1
        resp = client.get(url)
        soup  = BeautifulSoup(resp.content, "lxml")
        table = soup.find("table", id="xfiles")
        sleep(1)
        files = table.find_all("a", class_="tx-dark")
        num = len(files)
        print(f"\nNumber of Files in Page No {page_no}: ", num, "\n")
        for file in files:
            file_url = file["href"]
            resp2 = client.get(file_url)
            scrape = BeautifulSoup(resp2.text, "html.parser")
            inputs = scrape.find_all("input")
            file_id = inputs[1]["value"]
            file_name = findall("URL=(.*?) - ", resp2.text)[0].split("]")[1]
            parse = {"op":"download2", "id": file_id, "referer": url}
            sleep(2)
            resp3 = client.post(base_url, data=parse, headers=hs, allow_redirects=False)
            dl_url = resp3.headers["Location"]
            dl_url = dl_url.replace(" ", "%20")
            print("File Name:", file_name)
            print("File Link:", file_url)
            print("Download Link:", dl_url)
            print("\n")
            pages = soup.find("ul", class_="pagination")
            if pages is None:
                done = True
            else:
                current_page = pages.find("li", "page-item actived", recursive=False)
                next_page = current_page.next_sibling
                if next_page is None:
                    done = True
                else:
                    url = base_url + next_page["href"]
else:
    resp = client.get(url)
    scrape = BeautifulSoup(resp.text, "html.parser")
    inputs = scrape.find_all("input")
    file_id = inputs[1]["value"]
    file_name = findall("URL=(.*?) - ", resp.text)[0].split("]")[1]
    parse = {"op":"download2", "id": file_id, "referer": url}
    sleep(2)
    resp2 = client.post(base_url, data=parse, headers=hs, allow_redirects=False)    
    dl_url = resp2.headers["Location"]
    dl_url = dl_url.replace(" ", "%20")
    print("\nFile Name:", file_name)
    print("File Link:", url)
    print("Download Link:", dl_url)
    print("\n")

kb = 1024
def status(download_t, download_d, upload_t, upload_d):
    if download_t > 0:
        percentage = int(download_d / download_t * 100)
        STREAM.write('Downloading: {}/{} kiB ({}%)\r'.format(
            str(int(download_d / kb)),
            str(int(download_t / kb)),
            percentage
        ))
    else:
        STREAM.write('Starting download... {}\r'.format(download_d))
    STREAM.flush()

# Download file using pycurl
with open(file_name, 'wb') as f:
    c = pycurl.Curl()
    c.setopt(c.URL, dl_url)
    c.setopt(c.WRITEDATA, f)
    # Display progress
    c.setopt(c.NOPROGRESS, False)
    c.setopt(c.XFERINFOFUNCTION, status)
    c.perform()
    c.close()

# Keeps progress onscreen after download completes
print()
