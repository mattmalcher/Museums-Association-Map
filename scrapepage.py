from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import urllib.request
import json
import re


def latlon_from_postcode(postcode):

    # Remove Spaces
    postcode=postcode.replace(' ', '')

    # Build URL
    res = urllib.request.urlopen("http://api.postcodes.io/postcodes/"+postcode).read()

    # Get JSON
    data = json.loads(res)

    return data["result"]["longitude"], data["result"]["latitude"]

[lat, long] = latlon_from_postcode('GU22 8RL')


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Specify Members Free Entry Page url's
urls = ("https://www.museumsassociation.org/members-free-entry",
        "https://www.museumsassociation.org/members-free-entry/london",
        "https://www.museumsassociation.org/members-free-entry/northern-ireland",
        "https://www.museumsassociation.org/members-free-entry/yorkshire-and-humberside")

url = urls[1]
html = urlopen(url, context=ctx).read()

soup = BeautifulSoup(html, "html.parser")

# Navigate to main body which contains tags of level with postcodes
main_col = soup.body.contents[5].contents[2].contents[10].contents[3].contents[1].contents[7].contents[7]

locations=[]

# Iterate over main col tags
for child in main_col.children:

    try:
        if child['style'] == 'font-weight: bold; padding-top: 15px;' :

            name = child.string.strip()
            addresses = child.next_sibling.next_sibling.text.strip().split('\n\n')
            address = addresses[0]

            # regex to find postcodes
            postcodes = re.findall(r'\b[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b', address)
            print(postcodes[0])

            try:
                web = addresses[1]
                locations.append({'name': name, 'address': address, 'web': web})

            except IndexError:
                locations.append({'name': name, 'address': address})


    except TypeError:
        continue

    except KeyError:
        continue

# Addresses look to be contained within '<div id="main_column">'
for loc in locations:
    print(loc)

print('')