from uk_boundary import is_within_uk_boundary  # Ensure this function is available

# Example dictionary of cities with their coordinates
city_coordinates = {
    "Bath": ["51.38", "-2.36"],
    "Birmingham": ["52.48", "-1.9025"],
    "Bradford": ["53.8", "-1.75"],
    "Brighton": ["50.8208", "-0.1375"],
    "Bristol": ["51.4536", "-2.5975"],
    "Cambridge": ["52.2053", "0.1192"],
    "Canterbury": ["51.28", "1.08"],
    "Carlisle": ["54.8947", "-2.9364"],
    "Chelmsford": ["51.73", "0.48"],
    "Chester": ["53.19", "-2.89"],
    "Chichester": ["50.8365", "-0.7792"],
    "Colchester": ["51.8917", "0.903"],
    "Coventry": ["52.4081", "-1.5106"],
    "Derby": ["52.9247", "-1.478"],
    "Doncaster": ["53.5231", "-1.1339"],
    "Durham": ["54.7761", "-1.5733"],
    "Ely": ["52.3981", "0.2622"],
    "Exeter": ["50.7256", "-3.5269"],
    "Gloucester": ["51.8667", "-2.25"],
    "Hereford": ["52.056", "-2.716"],
    "Kingston upon Hull": ["53.7444", "-0.3325"],
    "Lancaster": ["54.0489", "-2.8014"],
    "Leeds": ["53.7975", "-1.5436"],
    "Leicester": ["52.6344", "-1.1319"],
    "Lichfield": ["52.682", "-1.829"],
    "Lincoln": ["53.2283", "-0.5389"],
    "Liverpool": ["53.4094", "-2.9785"],
    "London": ["51.5072", "-0.1275"],
    "Manchester": ["53.479", "-2.2452"],
    "Milton Keynes": ["52.04", "-0.76"],
    "Newcastle under Lyme": ["53.0109", "-2.2278"],
    "Norwich": ["52.6286", "1.2928"],
    "Nottingham": ["52.9561", "-1.1512"],
    "Oxford": ["51.75", "-1.25"],
    "Peterborough": ["52.5661", "-0.2364"],
    "Plymouth": ["50.3714", "-4.1422"],
    "Portsmouth": ["50.8058", "-1.0872"],
    "Preston": ["53.83", "-2.735"],
    "Ripon": ["54.138", "-1.524"],
    "Salford": ["53.483", "-2.2931"],
    "Salisbury": ["51.07", "-1.79"],
    "Sheffield": ["53.3808", "-1.4703"],
    "Southampton": ["50.9025", "-1.4042"],
    "Southend": ["51.55", "0.71"],
    "Stoke-on-Trent": ["53", "-2.1833"],
    "Sunderland": ["54.906", "-1.381"],
    "Truro": ["50.26", "-5.051"],
    "Wakefield": ["53.6825", "-1.4975"],
    "Wells": ["51.2094", "-2.645"],
    "Westminster": ["51.4947", "-0.1353"],
    "Winchester": ["51.0632", "-1.308"],
    "Wolverhampton": ["52.5833", "-2.1333"],
    "Worcester": ["52.1911", "-2.2206"],
    "York": ["53.96", "-1.08"],
    "test":["54.786337610503296", "-1.7873395523171414"]
}

def check_coordinates_within_uk(city_coords):
    invalid_coordinates = []
    for city, coords in city_coords.items():
        latitude, longitude = map(float, coords)
        if not is_within_uk_boundary(latitude, longitude):
            invalid_coordinates.append({city: coords})
    return invalid_coordinates

# Check all coordinates
invalid_coords = check_coordinates_within_uk(city_coordinates)
print("len of invalid coordinates",len(invalid_coords))

if invalid_coords:
    print("Invalid coordinates found:", invalid_coords)
else:
    print("All coordinates are within the UK.")
