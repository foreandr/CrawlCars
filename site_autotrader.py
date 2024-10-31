# WE START HERE
import hyperSel
import hyperSel.data_utiliites
import hyperSel.log_utilities
import hyperSel.selenium_utilities
import math
import time
import re

def get_num_listings(driver):
    soup = hyperSel.selenium_utilities.get_driver_soup(driver)
    count = soup.find("span", class_="at-results-count pull-left").text.replace(",","")
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
    all_canada_url_template = 'https://www.autotrader.ca/cars/tesla/on/toronto/?rcp=100&rcs=@offset&srt=35&prx=100&prv=Ontario&loc=M54A9&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch'
    all_canada_url = 'https://www.autotrader.ca/cars/tesla/on/toronto/?rcp=15&rcs=0&srt=35&prx=100&prv=Ontario&loc=M54A9&hprc=True&wcp=True&sts=New-Used&inMarket=basicSearch'
    driver = hyperSel.selenium_utilities.open_site_selenium(all_canada_url, False)
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
        hyperSel.log_utilities.log_function(soup)

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
        hyperSel.log_utilities.log_data(data_dict)
        # input("INDIVIUDAL CAR")

def main():
    print("AUTOTRADER MAIN")

    # CANADIAN
    all_canadian_teslas()

    # LOOP THROUGH AMERICA POSTAL CODES

if __name__ == '__main__':
   main()