from bs4 import BeautifulSoup as bs
import os
import requests
import json
import time

def download(info):
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
    

def main():
    datafile, cont, opening, recent = json.loads(open("data.json", "r").read()), False, False, 0
    start = time.time()
    try:
        data = int(datafile["last"])

    except:
        data = 0
        opening = True

    if data > 0 and not opening:
        x = input("Would you like to continue downloading from where you left off (Y/n)? ")
        if x.lower() in ['y','yes']:
            cont=True

        else:
            data=0
    
    pages = int(input("How many pages of images would you like to download? "))
    
    if pages <=0:
        print("Error, bad page amount")
        return
    
    for i in range(pages):
        try:
            page_no=i+1
            page=requests.get("http://e-shuushuu.net/?page="+str(page_no+data))
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
                    # blah is now something like 2018-08-14-999999.jpg
                    download(blah)
                    
            else:
                print("Error getting page")
                continue

        except:
            print("Error, something went wrong when finding images")

        print("Downloaded page {}".format(page_no))

        recent=int(i+1)

        stop = time.time()

        print("time taken: {}".format(int(stop)-int(start)))

    f = open("data.json", "w")
    datafile["last"] = int(recent)
    f.write(json.dumps(datafile))
    f.close()


if __name__ == "__main__":
    main()
