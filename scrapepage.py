from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import urllib.request
import json
import re
import csv

def latlon_from_postcode(postcodes):

    if len(postcodes) > 0:

        postcode = postcodes[0]

        # Build URL & request
        url="http://api.postcodes.io/postcodes/"+postcode.replace(' ', '')
        print(url)

        try:
            res = urllib.request.urlopen(url).read()
            # Get JSON
            data = json.loads(res)
            long = data["result"]["longitude"]
            lat = data["result"]["latitude"]

        except urllib.error.HTTPError:

            print('HTTP Error')
            long = ''
            lat = ''

    else:
        lat = ''
        long = ''
        postcode = 'No Valid Postcode Found'

    return long, lat, postcode


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# TODO - Update to handle multiple URL's
# Specify Members Free Entry Page url's
urls = (
        "https://www.museumsassociation.org/members-free-entry/channel-islands",
        "https://www.museumsassociation.org/members-free-entry/east-midlands",
        "https://www.museumsassociation.org/members-free-entry/east-of-england",
        "https://www.museumsassociation.org/members-free-entry/isle-of-man",
        "https://www.museumsassociation.org/members-free-entry/london",
        "https://www.museumsassociation.org/members-free-entry/north-east",
        "https://www.museumsassociation.org/members-free-entry/north-west",
        "https://www.museumsassociation.org/members-free-entry/scotland",
        "https://www.museumsassociation.org/members-free-entry/south-east",
        "https://www.museumsassociation.org/members-free-entry/south-west",
        "https://www.museumsassociation.org/members-free-entry/wales",
        "https://www.museumsassociation.org/members-free-entry/west-midlands",
        "https://www.museumsassociation.org/members-free-entry/northern-ireland",
        "https://www.museumsassociation.org/members-free-entry/yorkshire-and-humberside")



print(urls)
def getLocationInfo(url):

    html = urlopen(url, context=ctx).read()

    soup = BeautifulSoup(html, "html.parser")

    # Navigate to main body which contains tags of level with postcodes
    main_col = soup.body.contents[5].contents[2].contents[10].contents[3].contents[1].contents[7].contents[7]

    locations = []

    # Iterate over main col tags
    for child in main_col.children:

        try:
            if child['style'] == 'font-weight: bold; padding-top: 15px;' :

                name = child.string.strip()
                addresses = child.next_sibling.next_sibling.text.strip().split('\n\n')


                # regex to find postcodes - note "   *" to allow matching of an arbitrary number of spaces in middle
                postcodes = re.findall(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? *[0-9][ABD-HJLNP-UW-Z]{2}\b', addresses[0])

                # If no postcodes found and we have more address, try the other part of address
                if len(postcodes) == 0 & len(addresses) >1 :

                    postcodes = re.findall(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? *[0-9][ABD-HJLNP-UW-Z]{2}\b', addresses[1])



                [long, lat, postcode] = latlon_from_postcode(postcodes)



                try:
                    web = addresses[1]
                    locations.append({'name': name, 'address': addresses[0],
                                      'postcode':postcode,
                                      'lat':lat, 'long':long,
                                      'web': web})

                except IndexError:
                    locations.append({'name': name, 'address': addresses[0],
                                      'postcode':postcode,
                                      'lat':lat, 'long':long})


        except TypeError:
            continue

        except KeyError:
            continue

    return locations


loc_list = []

for url in urls:

    new_locations = getLocationInfo(url)

    loc_list.extend(new_locations)

# Addresses look to be contained within '<div id="main_column">'
for loc in loc_list:
    print(loc)

print('')

# TODO - Write list out to a csv for QGIS


with open('MAM.csv', 'w', newline='') as csvfile:

    spamwriter = csv.writer(csvfile, dialect='excel', quoting=csv.QUOTE_MINIMAL)

    spamwriter.writerow(['name','address','postcode','lat','long','web'])

    for item in loc_list:
        try:
            spamwriter.writerow([item['name'],item['address'],item['postcode'], item['lat'],item['long'], item['web']])

        except KeyError:
            spamwriter.writerow(
                [item['name'], item['address'], item['postcode'], item['lat'], item['long']])