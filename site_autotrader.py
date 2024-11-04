# WE START HERE
import hyperSel
import hyperSel.data_utiliites
import hyperSel.log_utilities
import hyperSel.nodriver_utilities
import hyperSel.selenium_utilities
import math
import time
import re
import helpers
import hyperSel.soup_utilities
import threading

def get_num_listings(driver):
    soup = hyperSel.selenium_utilities.get_driver_soup(driver)
    count_text = soup.find("span", class_="at-results-count pull-left").text.replace(",", "")
    count = re.search(r'\d+', count_text).group()
    print("count:", count)
    return count

def get_num_listings_us(soup):
    count_text = soup.find("h2", class_="text-bold text-size-400 text-size-sm-500 padding-bottom-4").text.replace(",", "")
    count = re.search(r'\d+', count_text).group()
    print("count:", count)
    return count

def calculate_loops(total_items, items_per_page):
    print("total_items:", total_items)
    print("items_per_page:", items_per_page)
    try:
        # Calculate the number of pages needed to cover all items
        return math.ceil(int(total_items) / int(items_per_page))
    except Exception as e:
        print(e)
        print("UNABLE TO CALC LOOPS NEEDED")
        return 0 

def all_canadian_teslas():
    all_canada_url_template = 'https://www.autotrader.ca/cars/tesla/on/toronto/?rcp=100&rcs=@offset&srt=35&prx=100&prv=Ontario&kwd=autopilot&loc=M54A9&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch'
    all_canada_url = 'https://www.autotrader.ca/cars/tesla/on/toronto/?rcp=15&rcs=0&srt=35&prx=100&prv=Ontario&kwd=autopilot&loc=M54A9&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch'
    driver = hyperSel.selenium_utilities.open_site_selenium(all_canada_url, True)
    hyperSel.selenium_utilities.maximize_the_window(driver)
   
    # LOOPING
    items_per_page = 100
    num_listings = get_num_listings(driver)
    
    individual_car_urls = []

    for i in range(0, calculate_loops(total_items=num_listings, items_per_page =items_per_page)):
        print("big loop iter", i)

        offset = i * items_per_page
        url = all_canada_url_template.replace("@offset", str(offset))
        hyperSel.selenium_utilities.go_to_site(driver, url)
        time.sleep(3)

        soup = hyperSel.selenium_utilities.get_driver_soup(driver)
        # hyperSel.log_utilities.log_function(soup)

        pattern = r'href="/a/[^/]+/[^/]+/[^/]+/[^/]+/\d+_\d+_\d+/"'
        urls = re.findall(pattern, str(soup))
        cleaned_urls = [url.split('"')[1] for url in urls]
        for i in cleaned_urls:
            individual_car_urls.append(f"https://www.autotrader.ca{i}")

        go_through_individual_cars(driver, individual_car_urls)
        individual_car_urls = []

        print("SINGLE PAGE ITER")
        break

def extract_numbers(text):
    # Extract all parts of the number and join them
    match = ''.join(re.findall(r'\d+\.?\d*', text))
    return match

def extract_year(title):
    # Regular expression to find the first four-digit year in the title
    match = re.search(r'\b\d{4}\b', title)
    return match.group(0) if match else None  # Return the year or None if no match

def go_through_individual_cars(driver, individual_car_urls):
    for url in individual_car_urls:
        # print(url)
        hyperSel.selenium_utilities.go_to_site(driver, url)
        time.sleep(0.5)
        soup = hyperSel.selenium_utilities.get_driver_soup(driver)
        
        data_dict = {}
        try:
            title = soup.find("h1", class_="hero-title").text

            year =  extract_year(title)

            data_dict['title'] = title
            data_dict['year'] = year
        except Exception as e:
            continue
            input("TITLE ISSUE?") # for debugging

        try:
            price = soup.find("p", class_="hero-price").text
            data_dict['price'] = extract_numbers(price)
        except Exception as e:
            continue
            input("PRICE SSUE?") # for debugging

        for li in soup.select("#sl-card-body li"):
            # Find the 'key' and 'value' spans within each li
            key = li.find("span", {"id": lambda x: x and x.startswith("spec-key")}).text.strip()
            value = li.find("span", {"id": lambda x: x and x.startswith("spec-value")}).find("strong").text.strip()
            
            # Add to dictionary
            data_dict[key] = value

        data_dict['url'] = url 

        # print(data_dict)
        if helpers.should_log(data_dict['title']):
            print("LOGGING ONE")
            hyperSel.log_utilities.log_data(data_dict)
        else:
            print("DIDNT HIT CRITERION")
            # input("INDIVIUDAL CAR")

def main():
    print("AUTOTRADER MAIN")

    # Define the threads using lambda functions as targets
    canadian_thread = threading.Thread(target=lambda: all_canadian_teslas())
    american_thread = threading.Thread(target=lambda: all_american_teslas())

    # Start the threads
    canadian_thread.start()
    american_thread.start()

    # Optionally, wait for both threads to complete
    canadian_thread.join()
    american_thread.join()

    print("All tasks completed.")

def all_american_teslas():
    print("all_american_teslas")
    all_us_url = '''https://www.autotrader.com/cars-for-sale/all-cars/tesla/model-x/los-angeles-ca?keywordPhrases=self%20driving&newSearch=true&searchRadius=0&zip=90012'''
    iter_template_url ='https://www.autotrader.com/cars-for-sale/all-cars/tesla/model-x/los-angeles-ca?firstRecord=@PAGINATION&keywordPhrases=self%20driving&newSearch=false&searchRadius=0'
    # driver = hyperSel.selenium_utilities.open_site_selenium(all_us_url, True)
    browser = hyperSel.nodriver_utilities.open_browser()
    # hyperSel.nodriver_utilities.go_to_site(browser, all_us_url)
    soup = hyperSel.nodriver_utilities.get_site_soup(browser, all_us_url)

    items_per_page = 25
    num_listings = get_num_listings_us(soup)
    print("num_listings:", num_listings)
    for i in range(0, calculate_loops(total_items=num_listings, items_per_page =items_per_page)+1):
        full_url = iter_template_url.replace("@PAGINATION", str(i*items_per_page))
        new_soup = hyperSel.nodriver_utilities.get_site_soup(browser, full_url, 8)
        # hyperSel.log_utilities.log_function(soup)
        # "https://www.autotrader.com/cars-for-sale/all-cars/tesla/model-x/los-angeles-ca"
        # 
        list_urls = []
        active_ids = extract_active_results_ids(raw_string=str(new_soup))
        for j in active_ids:
            list_urls.append(f"https://www.autotrader.com/cars-for-sale/vehicle/{j}")

        go_through_us_single_page_urls(browser, list_urls)

def go_through_us_single_page_urls(browser, list_of_urls):  
    for url in list_of_urls:
        do_single_us_page(browser, url)
    
def do_single_us_page(browser, url):
    print("url:", url)
    soup = hyperSel.nodriver_utilities.get_site_soup(browser, url)
    # hyperSel.log_utilities.log_function(soup)
    data_dict = do_single_us_soup(soup)
    data_dict['url'] = url
    print("data_dict:", data_dict)

    if helpers.should_log(data_dict['title']):
        print("LOGGING ONE")
        hyperSel.log_utilities.log_data(data_dict)
    else:
        print("DIDNT HIT CRITERION")

def do_single_us_soup(soup_big):
    data_dict = {}

    title = soup_big.find("h1", class_="text-ultra-bold text-size-400 col-xs-12 col-sm-7 col-md-8 text-size-sm-700").text
    # print("title:", title)
    data_dict['title'] = title

    year = extract_year(title)
    data_dict['year'] = year

    price = extract_numbers(soup_big.find("span", class_="text-size-600 text-ultra-bold").text)
    data_dict['price'] = price

    tags = soup_big.find_all("div", class_="text-left")
    wanted_tag = tags[0]
    
    for i in wanted_tag.find_all('li'):
        inner_div = i.find("div", class_="col-xs-2")
        try:
            aria_label = inner_div.find("div")["aria-label"]
        except Exception as e:
            pass

        try:
            value = i.find("div", class_="display-flex col-xs-10 margin-bottom-0").text
        except Exception as e:
            pass

        data_dict[aria_label] = value

    return data_dict

def extract_active_results_ids(raw_string):
    # Regex to find all 'activeResults' arrays and extract their contents
    pattern = r'"activeResults"\s*:\s*\[(.*?)\]'
    matches = re.findall(pattern, raw_string)
    id_list = []

    for match in matches:
        # Split the match by commas and strip whitespace, converting to integers
        ids = [int(id_str.strip()) for id_str in match.split(',') if id_str.strip().isdigit()]
        id_list.extend(ids)

    # print("ID List:", id_list)
    return list(set(id_list))

def extract_all_hrefs(soup):
    hrefs = [a['href'] for a in soup.find_all('a', href=True)]
    return hrefs

if __name__ == '__main__':
    #all_american_teslas()
    # all_canadian_teslas()

    main()