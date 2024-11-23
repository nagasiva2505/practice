from bs4 import BeautifulSoup
import cloudscraper
from re import findall
from time import sleep
import pycurl
from sys import stderr as STREAM
import time
import urllib.parse  # For URL encoding

# Accepting Sendcm URL from User
url = input("Enter Sendcm URL (default is https://send.cm/aecdgu9xisny): ") or "https://send.cm/aecdgu9xisny"

# Check if the URL is a valid Send.cm URL
if "send.cm" not in url:
    print("\nURL Entered is not Supported!\n")
    exit()

base_url = "https://send.cm/"
client = cloudscraper.create_scraper(allow_brotli=False)
hs = {
    "Content-Type": "application/x-www-form-urlencoded", 
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
}

def is_sendcm_folder_link(url):
    return (
        f"{base_url}s/" in url
        or f"{base_url}?sort" in url
        or f"{base_url}?sort_field" in url
        or f"{base_url}?sort_order" in url
    )

# Determine if it's a Send.cm folder link
is_sendcm_folder = is_sendcm_folder_link(url)

# For downloading single files or folders
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
            parse = {"op": "download2", "id": file_id, "referer": url}
            sleep(2)
            resp3 = client.post(base_url, data=parse, headers=hs, allow_redirects=False)

            # Check for the redirect location
            if 'Location' in resp3.headers:
                dl_url = resp3.headers["Location"]
                dl_url = urllib.parse.quote(dl_url, safe="%/:=&?~#+!$,;'@()*[]")  # URL encode to handle special characters
                print("Fιℓє Nαмє: ", file_name)
                print("Fɪʟᴇ Lɪɴᴋ: ", file_url)
                print("Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋ: ", dl_url)
                print("\n")
            else:
                print("Download link not found.\n")
                continue
            
            # Pagination logic
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
    parse = {"op": "download2", "id": file_id, "referer": url}
    sleep(2)
    resp2 = client.post(base_url, data=parse, headers=hs, allow_redirects=False)
    
    # Check for the redirect location
    if 'Location' in resp2.headers:
        dl_url = resp2.headers["Location"]
        dl_url = urllib.parse.quote(dl_url, safe="%/:=&?~#+!$,;'@()*[]")  # URL encode to handle special characters
        print("\n")
        print("Fιℓє Nαмє: ", file_name)
        print("Fɪʟᴇ Lɪɴᴋ: ", url)
        print("Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋ: ", dl_url)
        print("\n")
    else:
        print("Download link not found.\n")

# Define callback function for download progress
kb = 1024  # Convert bytes to kilobytes for easier reading
def status(download_t, download_d, upload_t, upload_d):
    STREAM.write('Downloading: {}/{} kiB ({}%)\r'.format(
        str(int(download_d/kb)),
        str(int(download_t/kb)),
        str(int(download_d/download_t*100) if download_t > 0 else 0)
    ))
    STREAM.flush()

# Download file using pycurl with retry logic
with open(file_name, 'wb') as f:
    c = pycurl.Curl()
    c.setopt(c.URL, dl_url)
    c.setopt(c.WRITEDATA, f)
    c.setopt(c.SSL_VERIFYPEER, False)  # Disable SSL verification
    c.setopt(c.SSL_VERIFYHOST, False)  # Disable SSL verification
    c.setopt(c.SSLVERSION, pycurl.ssl.SSLVERSION_TLSv1_2)  # Enforce TLS v1.2

    c.setopt(c.NOPROGRESS, False)
    c.setopt(c.XFERINFOFUNCTION, status)

    try:
        c.perform()
    except pycurl.error as e:
        print(f"Error during download: {e}")
    finally:
        c.close()

print("Download complete.")
