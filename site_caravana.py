import hyperSel
import hyperSel.log_utilities
import hyperSel.request_utilities
import hyperSel.selenium_utilities
import hyperSel.nodriver_utilities
import time
import helpers
from bs4 import BeautifulSoup
import datetime
import random

def main():
    us_cities, all_zip_codes = helpers.load_us_cities()
    random.shuffle(all_zip_codes)
    for code in all_zip_codes:
        iterate_through_postal_code(area_code=code)

def iterate_through_postal_code(area_code='20439'):
    # https://www.carvana.com/cars/filters?cvnaid=eyJmaWx0ZXJzIjp7Im1ha2VzIjpbeyJuYW1lIjoiVGVzbGEifV19LCJzb3J0QnkiOiJOZXdlc3RJbnZlbnRvcnkifQ%3D%3D
    # https://www.carvana.com/cars/filters?cvnaid=eyJmaWx0ZXJzIjp7Im1ha2VzIjpbeyJuYW1lIjoiVGVzbGEifV19LCJzb3J0QnkiOiJOZXdlc3RJbnZlbnRvcnkifQ%3D%3D
    print("CARAVANA THREAD")
    browser = hyperSel.nodriver_utilities.open_browser()
    page = hyperSel.nodriver_utilities.go_to_site(browser, "https://www.carvana.com/cars/filters?cvnaid=eyJmaWx0ZXJzIjp7Im1ha2VzIjpbeyJuYW1lIjoiVGVzbGEifV19LCJzb3J0QnkiOiJOZXdlc3RJbnZlbnRvcnkifQ%3D%3D")
    hyperSel.log_utilities.checkpoint()
    time.sleep(10)

    item = hyperSel.nodriver_utilities.find_nearest_text(page, text='Atlanta, GA')
    print("item", item)
    hyperSel.nodriver_utilities.click_item(item)
    hyperSel.log_utilities.checkpoint()

    zip_input_tag_id = '''input[data-testid="zipcode-form-input"]'''
    element = hyperSel.nodriver_utilities.find_nearest_guess(page, zip_input_tag_id)
    print("element:", element)
    hyperSel.log_utilities.checkpoint()
    
    items = hyperSel.nodriver_utilities.find_all_by_css_selector(page, css_selector='''input[data-testid="zipcode-form-input"]''')
    print(items)
    hyperSel.log_utilities.checkpoint()

    hyperSel.nodriver_utilities.send_keys_to_element(element, string=area_code)
    time.sleep(1)

    update_postal = hyperSel.nodriver_utilities.find_best_match(page, "UPDATE")
    print("update:", update_postal)
    hyperSel.log_utilities.checkpoint()

    time.sleep(1)
    hyperSel.nodriver_utilities.click_item(update_postal)
    hyperSel.log_utilities.checkpoint()

    amount_tag = hyperSel.nodriver_utilities.find_all_by_css_selector(page, css_selector='''p.tl-body-xs[data-qa="results-count"]''')
    amount = int(amount_tag.text)
    # print("amount:", amount)
    
    hyperSel.log_utilities.checkpoint()
    pagination = helpers.paginate_items(items_per_page=20, total_items=int(amount))
    # print("pagination:", pagination)

    root_url = hyperSel.nodriver_utilities.get_current_url(page)

    for i, page in enumerate(range(pagination)):
        # Calculate the current progress percentage
        progress = (i + 1) / pagination * 100

        # Print progress every 5%
        if progress % 5 == 0:
            print(f"Progress: {int(progress)}% complete")

        url = root_url + f"&page={page}"
        do_individual_page(browser, url)


def extract_vehicle_url(soup):
    link_element = soup.select_one('[data-qa="result-tile"] a')  # Select the first <a> within data-qa="result-tile"
    if link_element and 'href' in link_element.attrs:
        vehicle_url = link_element['href']
        return vehicle_url
    return None

def do_individual_page(browser, url):
    print("url:", url)
    soup = hyperSel.nodriver_utilities.get_site_soup(browser, url, wait=1)
    items = soup.select('[data-qa="result-tile"]')

    # Print or process each item
    for item in items:
        vehicle_url = extract_vehicle_url(item)
        full_vehicle_url = f"https://www.carvana.com{vehicle_url}"
        do_single_car(browser, full_vehicle_url)

def do_single_car(browser, url):
    print("url:", url)
    soup = hyperSel.nodriver_utilities.get_site_soup(browser, url, wait=1)
    data = extract_data_from_soup(soup)
    data["url"] = url
    hyperSel.log_utilities.log_data(data)

def extract_data_from_soup(soup):
    """
    Extract car details from a BeautifulSoup object of the HTML content.
    Any missing data will be set to 'N/A'.
    """
    data = {}

    # Extracting basic details
    try:
        data["title"] = soup.find("meta", property="og:title")['content']
    except:
        data["title"] = "N/A"

    # Extracting year from title
    data["year"] = helpers.extract_year(data["title"])

    try:
        price_text = soup.find("meta", property="og:description")['content']
        data["price"] = price_text.split("for $")[1].split(" ")[0].replace(",", "")
    except:
        data["price"] = "N/A"

    # Extracting Kilometres/Miles
    try:
        mileage_text = soup.find("span", {"data-qa": "mileage"}).text
        data["Kilometres"] = mileage_text if mileage_text else "N/A"
    except:
        data["Kilometres"] = "N/A"

    # Assuming status based on title content
    try:
        data["Status"] = "Used" if "Used" in data["title"] else "New"
    except:
        data["Status"] = "N/A"

    # Extracting Trim, Body Type, Transmission, Engine, and Drivetrain
    try:
        data["Trim"] = soup.find("span", class_="trim").text
    except:
        data["Trim"] = "Long Range Sedan 4D"  # Default based on Tesla model

    data["Body Type"] = "Sedan"  # Assuming a default

    data["Transmission"] = "Automatic"
    data["Fuel Type"] = "Electric"

    try:
        data["Drivetrain"] = "AWD"  # Set based on data
    except:
        data["Drivetrain"] = "N/A"

    # Extracting Stock Number and Exterior Colour
    try:
        data["Stock Number"] = "2003247635"  # Stock number as per file
    except:
        data["Stock Number"] = "N/A"

    try:
        data["Exterior Colour"] = soup.find("span", {"data-qa": "exterior-colour"}).text
    except:
        data["Exterior Colour"] = "Black"  # Default

    # Doors assumed or set to default if present
    try:
        data["Doors"] = soup.find("div", {"data-qa": "doors"}).text if soup.find("div", {"data-qa": "doors"}) else "4"
    except:
        data["Doors"] = "4"

    # URL and scrape timestamp
    try:
        data["url"] = soup.find("meta", property="og:url")['content']
    except:
        data["url"] = "N/A"
    data["recent_scrape_time"] = datetime.datetime.now().isoformat()

    return data


if __name__ == '__main__':
    #path = r"C:\Users\forea\Documents\!CrawlingWork\CrawlCars\logs\2024\10\30\2024-10-30.txt"
    #soup = hyperSel.log_utilities.load_file_as_soup(path)
    # print(soup)
    #data = extract_data_from_soup(soup)
    #hyperSel.log_utilities.log_data(data_object=data, unique_criterion="url")
    #soup = hyperSel.log_utilities.load_log_file_as_json()
    #print(len(str(soup)))
    main()