from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
}


url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
response = requests.get(url=url, headers=HEADERS)
soup = BeautifulSoup(response.text, "lxml")

SEARCH_PRODUCT_DIV_LIST = soup.find_all("div", attrs={"data-component-type":"s-search-result"})

PRODUCT_TITLE_LIST = []
PRODUCT_PRICE_LIST = []
PRODUCT_URL_LIST=[]
PRODUCT_RATING_LIST = []
PRODUCT_NUMBER_OF_REVIEWS_LIST = []
PRODUCT_DESCRIPTION_LIST = []
PRODUCT_ASIN_LIST = []
PRODUCT_MANUFACTURER_LIST = []



def fetch_required_info(url_list_current_page):

    global SEARCH_PRODUCT_DIV_LIST
    global PRODUCT_TITLE_LIST
    global PRODUCT_PRICE_LIST
    global PRODUCT_RATING_LIST
    global PRODUCT_NUMBER_OF_REVIEWS_LIST
    global PRODUCT_ASIN_LIST
    global PRODUCT_URL_LIST

    raw_url_list = []
    for product_div in SEARCH_PRODUCT_DIV_LIST:

        extracted_raw_url = product_div.find("a", attrs={"class":"a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"}).get("href")
        raw_url_list.append(extracted_raw_url)

        title = product_div.find("span", attrs={"class":"a-size-medium a-color-base a-text-normal"}).get_text()
        product_asin = product_div.get("data-asin")

        try:
            price = product_div.find_all("span", attrs={"class":"a-price-whole"})
        except:
            price = "Not found"
        else:
            final_price = ""
            for tag in price:
                if final_price != "":
                    final_price += f"- ₹{tag.get_text()}"
                else:
                    final_price += f"₹{tag.get_text()}"

        try:
            rating = product_div.find("span", attrs={"class": "a-icon-alt"}).get_text().split(" ")[0]
        except:
            rating = "Not found"
        
        try:
            number_of_review = product_div.find("span", {"class":"a-size-base s-underline-text"}).get_text()
        except:
            number_of_review = "Not found"
                

        PRODUCT_TITLE_LIST.append(title)
        PRODUCT_PRICE_LIST.append(final_price)
        PRODUCT_RATING_LIST.append(rating)
        PRODUCT_NUMBER_OF_REVIEWS_LIST.append(number_of_review)
        PRODUCT_ASIN_LIST.append(product_asin)


    for url in raw_url_list:
        if "https" not in url:
            complete_url = "https://www.amazon.in" + url
            PRODUCT_URL_LIST.append(complete_url)
            url_list_current_page.append(complete_url)
        else:
            PRODUCT_URL_LIST.append(url)
            url_list_current_page.append(complete_url)



#Part-2- Defining Required Functions:

def scrape_manufacturer(soup2):
    global PRODUCT_MANUFACTURER_LIST

    table_id = soup2.find("table", attrs={"id":"productDetails_techSpec_section_1"})
    ul_class = soup2.find("ul", attrs={"class":"a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"})


    if table_id != None:
        th_list = table_id.find_all("th")
        td_list = table_id.find_all("td")
        manufacturer_found = False
        for th in th_list:
            if "Manufacturer" in (th.get_text()):
                position = th_list.index(th)
                td = td_list[position].get_text().strip()
                PRODUCT_MANUFACTURER_LIST.append(td)
                manufacturer_found = True
                break
        if not manufacturer_found:
            PRODUCT_MANUFACTURER_LIST.append("Not Mentioned.")
    elif ul_class != None:
        span_list = ul_class.find_all("span", attrs={"class":"a-list-item"})
        span_title_span = ul_class.find_all("span", attrs={"class":"a-text-bold"})
        manufacturer_found = False
        for span in span_list:
            for _ in span_title_span:
                if ("Manufacturer" in (_.string)) and ("Discontinued" not in (_.string)):
                    position = span_title_span.index(_)
                    manufacturer_found = True
                    break
        if manufacturer_found:
            required_text = span_list[position].contents[3].string.strip()
        else:
            required_text = "Not Mentioned"
        PRODUCT_MANUFACTURER_LIST.append(required_text)
        

def scrape_description(soup2):
    global PRODUCT_DESCRIPTION_LIST

    try:
        description_div = soup2.find("div", attrs={"id":"productDescription"})
        alt_description_div = soup2.find("div", attrs={"class": "aplus-v2 desktop celwidget"})

        if description_div != None:
            description_text = description_div.get_text(strip=True)
        elif (alt_description_div != None) and (alt_description_div.get_text(strip=True) != ""):
            description_text = alt_description_div.get_text(strip=True)
        else:
            description_span= soup2.find("span", attrs={"class":"a-list-item a-size-base a-color-base"})
            if description_span == None:
                description_text = soup2.find("div", attrs={"id":"feature-bullets"}).find("span", attrs={"class":"a-list-item"}).string.strip()
            else:
                description_text = description_span.string.strip()

        if description_text == "":
            PRODUCT_DESCRIPTION_LIST.append("Not Mention")
        else:
            PRODUCT_DESCRIPTION_LIST.append(description_text)
    except:
        PRODUCT_DESCRIPTION_LIST.append("Not Mentioned")



def get_data(fetch_required_info, scrape_manufacturer, scrape_description):
    url_list_current_page = []
    # Part: - 1 :-
    fetch_required_info(url_list_current_page)

    # Part - 2 :-

    for url in url_list_current_page:
        new_response = requests.get(url, headers=HEADERS)
        soup2 = BeautifulSoup(new_response.text, "lxml")

        scrape_manufacturer(soup2)
        scrape_description(soup2)


end_page = False
def get_next_page(soup):
    global end_page
    print("Page Change.")
    next_page = soup.find('a', {'class': 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator'})
    if next_page != None:
        raw_url = next_page.get("href")
        url = "https://www.amazon.in/" + raw_url
        return url
    else:
        end_page=True
        return



get_data(fetch_required_info, scrape_manufacturer, scrape_description)

while not end_page:
    url = get_next_page(soup)
    if url != None:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "lxml")
        SEARCH_PRODUCT_DIV_LIST = soup.find_all("div", attrs={"data-component-type":"s-search-result"})

        get_data(fetch_required_info, scrape_manufacturer, scrape_description)
    else:
        last_page = True



data = {
    "Title": PRODUCT_TITLE_LIST,
    "Price": PRODUCT_PRICE_LIST,
    "Ratings": PRODUCT_RATING_LIST,
    "NumberOfReviews": PRODUCT_NUMBER_OF_REVIEWS_LIST,
    "ASIN": PRODUCT_ASIN_LIST,
    "URL": PRODUCT_URL_LIST,
    "Manufacturer": PRODUCT_MANUFACTURER_LIST,
    "Description": PRODUCT_DESCRIPTION_LIST,
}

df = pd.DataFrame(data= data)
df.index.name = "Index"
df.index += 1

df.to_csv("amazon_scrape.csv", index_label="Index")


