from selenium import webdriver
import time, json
import pandas as pd
from bs4 import BeautifulSoup


chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--headless")  # IMP
web = webdriver.Chrome(
    executable_path='F:\Devesh\chromedriver.exe',
    options = chrome_options
)


def get_product_details(source):
    soup = BeautifulSoup(source, 'html.parser')
    rtrn = {}
    for i in soup:
        if str(i).startswith("<tr"):
            rtrn[ i.find("span", "a-size-base a-text-bold").get_text() ] = i.find("td", "a-span9").find("span").get_text()
    return rtrn



def get_kindle_details(source):
    soup = BeautifulSoup(source, "html.parser")
    rtrn = {}
    for index, i in enumerate(soup.find('ul')):
        if str(i).startswith("<li"):
            temp = []
            for j in i.find("span","a-list-item"):
                if str(j).startswith("<span"):
                    temp.append( str(j.get_text()).replace('\n','').replace(':','').replace(' ','') )
            rtrn[temp[0]] = temp[1]
    return rtrn


def get_product_price(source):
    span = BeautifulSoup(source, "html.parser")
    price = ''
    for i in span:
        if str(i).startswith("<span"):
            price = price + i.get_text()
    return price


def get_kindle_price(source):
    span = BeautifulSoup(source, "html.parser")
    return span.get_text().replace('\n','').replace(' ','').replace("from",'')


def get_data(url, country):
    web.get(url)
    time.sleep(2)

    try:
        web.find_element_by_xpath("/html/body/div/div/a/img")
        return {"error" : "no such product exists", "url" : url.replace("com", country),}

    except:
        try: 

            try:
                # for product
                data = {
                    "title" : web.find_element_by_xpath("/html/body/div[1]/div[2]/div[9]/div[4]/div[4]/div[1]/div/h1/span").text,
                    "image_url" : web.find_element_by_xpath("/html/body/div[1]/div[2]/div[9]/div[4]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/div[1]/ul/li[1]/span/span/div/img").get_attribute('src'),
                    "product_details" : get_product_details(web.find_element_by_xpath("/html/body/div[1]/div[2]/div[9]/div[4]/div[4]/div[37]/div/table/tbody").get_attribute("innerHTML")),
                    "url" : url.replace("com", country),
                    "price" : get_product_price(web.find_element_by_xpath("/html/body/div[1]/div[2]/div[9]/div[4]/div[4]/div[10]/div[1]/div[1]/span[1]/span[2]").get_attribute("innerHTML"))
                }
            
            except:
                # for kindle
                data = {
                    "title" : web.find_element_by_xpath("/html/body/div[1]/div[2]/div[4]/div[1]/div[7]/div[2]/div/h1/span[1]").text,
                    "image_url" : web.find_element_by_xpath("/html/body/div[1]/div[2]/div[4]/div[1]/div[6]/div[1]/div[1]/div[1]/div[1]/div/div/div/img").get_attribute('src'),
                    "product_details" : get_kindle_details(web.find_element_by_xpath("/html/body/div[1]/div[2]/div[4]/div[25]/div/div[1]").get_attribute('innerHTML')),
                    "url" : url.replace("com", country),
                    "price" : get_kindle_price(web.find_element_by_xpath("/html/body/div[1]/div[2]/div[4]/div[1]/div[7]/div[15]/div[2]/div[2]/ul/li/span/span[1]/span/a/span[2]").get_attribute("innerHTML")),
                }

            return data

        except: 

            try :
                data = {
                    "title" : web.find_element_by_xpath("/html/body/div[1]/div[2]/div[3]/div[1]/div[7]/div[2]/div/h1/span[1]").text,
                }
                data["image_url"] = web.find_element_by_xpath("/html/body/div[1]/div[2]/div[3]/div[1]/div[6]/div[1]/div[1]/div[1]/div[1]/div/div/div/img").get_attribute('src')
                data["product_details"] = get_kindle_details(web.find_element_by_xpath("/html/body/div[1]/div[2]/div[3]/div[25]/div/div[1]").get_attribute("innerHTML"))
                data["price"] = web.find_element_by_xpath("/html/body/div[1]/div[2]/div[3]/div[1]/div[7]/div[15]/div[2]/div[2]/ul/li/span/span[1]/span/a/span[2]/span").text
                data["url"] : url.replace("com", country)
                return data
            
            except : return {"error" :"some error occured while scraping.", "url" : url.replace("com", country),}



df = pd.read_csv("Amazon Scraping.csv")
url_scraped = set()


for i in range( 0, len(df['id']) ):

    with open('data.json', 'r') as f:
        old = json.load(f)

    country = list(df['country'])[i]
    asin = list(df['Asin'])[i]

    url = f"https://www.amazon.com/dp/{asin}"
    if url not in url_scraped and old[asin].get("error") == "some error occured while scraping.":
        print(f"index {i} --> ", end='')
        temp = get_data(url, country)
        print( temp )
        url_scraped.add(url)

        old[asin] = temp

        with open("data.json", 'w') as f:
            json.dump(old, f, indent=4)
