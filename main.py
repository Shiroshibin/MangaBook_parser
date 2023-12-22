import requests as req
from bs4 import BeautifulSoup as bs
import json
import os
from fake_useragent import UserAgent

from wp_post import post_image_to_server

try:
    os.mkdir("data")
except:
    pass

try:
    os.mkdir("page_json")
except:
    pass

try:
    os.mkdir("img")
except:
    pass



def pars_catalog():
    try:

        list_with_name = list()

        with open("data/title_list.json", "r") as file:
            list_with_dict = json.load(file) 

        for i in list_with_dict:
            list_with_name.append(i["title_name"])

    except:

        list_with_dict = list()

    sess = req.session()

    response = sess.get("https://mangabook.org/filterList?page=1&ftype[]=0&status[]=0&sortBy=rate&asc=true")
    soup = bs(response.text, "lxml")

    titles_list = soup.find_all("article")

    for title in titles_list:
        title_dict = dict()

        # Название
        title_name = title.find("div", class_ = "sh-title")
        title_dict["title_name"] = title_name.text

        # URL
        title_url = title.find("a", "short-poster img-box")
        title_url = title_url.get("href")
        title_dict["title_url"] = title_url

        title_dict["last_chapter"] = None 

        title_dict["chapters_url_list"] = None 

        if title_dict["title_name"] not in list_with_name:
            list_with_dict.append(title_dict)
            print(title_dict)
        
    with open("data/title_list.json", "w") as file:
        json.dump(list_with_dict, file, indent = 4) 



def pars_chapter():

    # ua = UserAgent()
    sess = req.session()
    # sess.headers.update({'User-Agent': ua.chrome})

    with open("data/title_list.json", "r") as file:
        url = json.load(file)[0]
        chapter = pars_title(url["title_url"])
       
    url = chapter[0]["url"]

    title_dir_name = "img/" + url.split("/")[4]
    chapter_dir_name = title_dir_name + "/" + url.split("/")[-1]

    # try:
    #     os.makedirs(title_dir_name)
    # except:
    #     pass

    try:
        os.makedirs(chapter_dir_name)
    except:
        pass

    
    
    response = sess.get(url)
    
    soup = bs(response.text, "lxml")

    max_page = soup.find("select", class_ = "btn-filt2").find_all("option")[-1]
    max_page = int(max_page.text)

    count = 1


    wp_id_list = list()
    while count <= max_page:
        new_url = f"{url}/{count}"
      
        
        response = sess.get(new_url)
        soup = bs(response.text, "lxml")

        url_of_img = soup.find("img", class_ = "img-responsive scan-page").get("src")
        
        

        img = sess.get(url_of_img[:-1])
        img = img.content
        
        
        print(url_of_img)
        # print(img)

       

        with open(f'{chapter_dir_name}/{url_of_img.split("/")[-1]}', "wb") as file:
            file.write(img)
        
        
            
        wp_id_list.append(post_image_to_server(f'{chapter_dir_name}/{url_of_img.split("/")[-1]}'[:-1]))
    
        count += 1
        
        break


    with open(f"page_json/{url.split('/')[4]}", "w+") as file:
        json.dump(
            {
                "page_id" : wp_id_list, 
                "name": f'{soup.find("div", class_ = "ts_in tb-wrp").find("a").text} {chapter[0]["name"]}'}, 
            file, 
            indent = 4
            )
        


def pars_title(url):
         
    sess = req.session()
    response = sess.get(url)
    soup = bs(response.text, "lxml")
    chapters_list = list()

    chapter = {
        "url": soup.find("ul", class_ = "chapters").find_all("h5")[0].find("a").get("href"),
        "name": soup.find("ul", class_ = "chapters").find_all("h5")[0].find("a").text
    }

    chapters_list.append(chapter)

    
    return chapters_list

    

def main():
    pars_catalog()
    pars_chapter()



if __name__ == "__main__":
    main()