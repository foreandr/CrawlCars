import csv

def load_us_cities():
    file_path = "./data/cities_us.csv"
    
    us_cities = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
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
                'zips': row['zips'].split(),
                'id': row['id']
            })
    
    return us_cities

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