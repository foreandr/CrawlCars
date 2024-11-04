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

def extract_year(title):
    # Regular expression to find the first four-digit year in the title
    match = re.search(r'\b\d{4}\b', title)
    return match.group(0) if match else None  # Return the year or None if no match

def should_log(title):
    """
    Determines whether a given title meets the criteria for logging.

    Criteria:
    - Must contain any of the specified keywords (case-insensitive).

    Args:
        title (str): The title to evaluate.

    Returns:
        bool: True if the title contains any of the keywords, False otherwise.
    """
    # Ensure the title is a string
    if not isinstance(title, str):
        return False

    # Convert the title to lowercase for case-insensitive comparison
    title_lower = title.lower()
    year = extract_year(title)

    try:
        if int(year) < 2021:
            return False
    except:
        pass
    
    # Combined list of all keywords related to "long range" and "self-driving"
    keywords = [
        # Long Range Keywords
        "long range",
        "extended range",
        "high mileage",
        "ultra range",
        "super range",  # Add more as needed
        "plaid", # plaid trim
        # Self-Driving Keywords
        "fsd",                        # Full Self-Driving
        "full self-driving",
        "self driving",
        "autopilot",
        "driver assist",
        "semi-autonomous",
        "autonomous driving",
        "advanced driver assistance", # ADAS
        "adas",
        "level 2 autonomy",
        "level 3 autonomy",
        "level 4 autonomy",
        "robotaxi",
        "hands-free driving",
        "smart summon",
        "autonomous",
        "self-driving capability",
        "automated driving",
        "driverless",
        "l2",                         # Level 2
        "l3",                         # Level 3
        "l4",                         # Level 4
        "auto pilot",                 # Alternative spelling
        "drive assist",
        "smart driving",
        "auto-assisted driving",
        "automated assistance",
        "self-driving system",
        "autonomous system",
        "hands free driving",         # Alternative spacing
        "handsfree driving",          # Alternative spelling
        "smart driving",              # Added for comprehensiveness
        "drive assist",
        "automated assistance",
        "self-driving system",
        "autonomous system",
        # Add more keywords as needed
    ]

    # Check if any keyword is present in the title
    return any(keyword in title_lower for keyword in keywords)