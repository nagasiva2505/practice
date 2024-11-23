import requests
from bs4 import BeautifulSoup
from re import findall
from time import sleep

# Accepting Sendcm URL from User
url = input("Enter your Sendcm URL : ")

if "send.cm" not in url:
    print("\nURL Entered is not Supported!\n")
    exit()

base_url = "https://send.cm/"
client = requests.Session()

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
        soup = BeautifulSoup(resp.content, "lxml")
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

            # Check if there are enough inputs before accessing them
            if len(inputs) > 1:
                file_id = inputs[1]["value"]
                file_name = findall("URL=(.*?) - ", resp2.text)[0].split("]")[1]
                parse = {"op": "download2", "id": file_id, "referer": url}
                sleep(2)
                resp3 = client.post(base_url, data=parse, allow_redirects=False)
                dl_url = resp3.headers["Location"]
                dl_url = dl_url.replace(" ", "%20")
                print("Fιℓє Nαмє: ", file_name)
                print("Fɪʟᴇ Lɪɴᴋ: ", file_url)
                print("Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋ: ", dl_url)
                print("\n")
            else:
                print("Error: No file ID found for file: ", file_url)
                continue  # Skip this file if no file ID is found

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

    # Check if there are enough inputs before accessing them
    if len(inputs) > 1:
        file_id = inputs[1]["value"]
        file_name = findall("URL=(.*?) - ", resp.text)[0].split("]")[1]
        parse = {"op": "download2", "id": file_id, "referer": url}
        sleep(2)
        resp2 = client.post(base_url, data=parse, allow_redirects=False)
        dl_url = resp2.headers["Location"]
        dl_url = dl_url.replace(" ", "%20")
        print("\n")
        print("Fιℓє Nαмє: ", file_name)
        print("Fɪʟᴇ Lɪɴᴋ: ", url)
        print("Dᴏᴡɴʟᴏᴀᴅ Lɪɴᴋ: ", dl_url)
        print("\n")
    else:
        print("Error: No file ID found for the given URL:", url)

# Download the file using requests
response = requests.get(dl_url, stream=True)
file_size = int(response.headers.get('Content-Length', 0))

# Open file in write-binary mode
with open(file_name, 'wb') as f:
    for data in response.iter_content(chunk_size=1024):
        f.write(data)

print("\nDownload Complete!")
