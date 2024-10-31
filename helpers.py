import csv
import re
def paginate_items(items_per_page, total_items):
    num_pages = (total_items + items_per_page - 1) // items_per_page  # Calculate total pages needed
    return num_pages

def extract_year(title):
    # Regular expression to find the first four-digit year in the title
    match = re.search(r'\b\d{4}\b', title)
    return match.group(0) if match else None  # Return the year or None if no match

def load_us_cities():
    file_path = "./data/cities_us.csv"
    
    us_cities = []
    all_zip_codes = []  # Set to collect unique ZIP codes
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Split ZIP codes and add to the all_zip_codes set
            zips = row['zips'].split()
            all_zip_codes.extend(zips)  # Add ZIP codes from this row
            
            us_cities.append({
                'city': row['city'],
                'city_ascii': row['city_ascii'],
                'state_id': row['state_id'],
                'state_name': row['state_name'],
                'county_fips': row['county_fips'],
                'county_name': row['county_name'],
                'lat': row['lat'],
                'lng': row['lng'],
                'population': row['population'],
                'density': row['density'],
                'source': row['source'],
                'military': row['military'],
                'incorporated': row['incorporated'],
                'timezone': row['timezone'],
                'ranking': row['ranking'],
                'zips': zips,
                'id': row['id']
            })
    
    return us_cities, all_zip_codes  # Return the list of cities and the set of ZIP codes

def load_canadian_cities():
    file_path = "./data/cities_can.csv"
    
    canadian_cities = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            canadian_cities.append({
                'city': row['city'],
                'city_ascii': row['city_ascii'],
                'province_id': row['province_id'],
                'province_name': row['province_name'],
                'lat': row['lat'],
                'lng': row['lng'],
                'population': row['population'],
                'density': row['density'],
                'timezone': row['timezone'],
                'ranking': row['ranking'],
                'postal': row['postal'].split(),
                'id': row['id']
            })
    
    return canadian_cities