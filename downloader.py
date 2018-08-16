from bs4 import BeautifulSoup as bs
from queue import Queue
import threading
import requests
import json
import time
import os

def download():
    while not q.empty():
        info = q.get()
        name=info[11:]
        url="http://e-shuushuu.net/images/"+str(info)
        path="./downloaded/"+info[:10]+"/"
        
        if not os.path.exists(path):
            os.makedirs(path)

        headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
        }

        r=requests.get(url, headers=headers, stream=True)

        if r:
            with open(str(path+name), "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

        q.task_done()

        print("Downloaded {}".format(name))
    

def main():
    datafile, cont, opening, recent = json.loads(open("data.json", "r").read()), False, False, 0
    try:
        data = int(datafile["last"])

    except:
        data = 0
        opening = True

    if data > 0 and not opening:
        x = input("Would you like to continue downloading from where you left off (Y/n)? ")
        if x.lower() not in ['y', 'yes', 'n', 'no']:
            print("Error, invalid option {}. Please try again.".format(x))
            return
        
        if x.lower() in ['y','yes']:
            cont=True

        else:
            data=0
    
    pages = input("How many pages of images would you like to download? ")

    threads = input("Amount of threads to download with (type \"default\" for default number)? ")    

    if not pages.isnumeric():
        print("Error: {} is not an integer")
        return

    else:
        pages = int(pages)

    if threads.lower() == "default":
        threads = "4"

    if not threads.isnumeric():
        print("Error: {} is not an integer".format(threads))
        return

    else:
        threads = int(threads)

    if pages <=0:
        print("Error, bad page amount")
        return
    
    global q, debug
    q = Queue()
    debug = []

    start = time.time()
    
    for i in range(pages):
        try:
            page_no=int(i)+1+int(data)
            page=requests.get("http://e-shuushuu.net/?page="+str(page_no))
            if page:
                soup=bs(page.content, "html.parser")

                main=soup.find("div", {"id":"page"})
                content=main.find("div", {"id":"content"})
                links = []
                for x in content.findAll("div", {"class":"image_thread display"}):
                    for y in x.findAll("div", {"class":"image_block"}):
                        z = y.find("div", {"class":"thumb"})
                        a = z.find("a", {"class":"thumb_image"})
                        links.append(a["href"].replace("/images/", "").strip())
                        
                for blah in links:
                    q.put(blah)
                    debug.append(blah)

                print("Retrieved images from page {}".format(page_no))
                    
            else:
                print("Error getting page")
                continue

        except:
            print("Error, something went wrong when finding images")

        recent=int(page_no)

    for i in range(threads):
        t = threading.Thread(target=download)
        t.daemon = True
        t.start()
        t.join()

    print("Downloaded all images")

    f = open("data.json", "w")
    datafile["last"] = int(recent)+1
    f.write(json.dumps(datafile))
    f.close()

    stop = time.time()

    print("Total elapsed time: {} seconds".format(int(stop)-int(start)))

if __name__ == "__main__":
    main()
