from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def index(request):
    brand = "Volkswagen"
    name = "Passat"
    # model = "B6"
    getParams= {'query': str(brand + '+' + name ), 'page':'1'}
    r = requests.get('https://999.md/ro/search', params=getParams)
    strFormat = str(r.text)

    soup = BeautifulSoup(strFormat, 'html.parser')

    sum = 0.0
    unitsCount = 0
    minPrice = 5000000
    maxPrice = 0
    outputresponse = ""
    for item in soup.find_all('li'):
        if str(item.get('class'))=='[\'ads-list-photo-item\']':
            for priceTag in item.find_all('div'):
                if str(priceTag.get('class')) == '[\'ads-list-photo-item-title\']':
                    # if brand.lower() in str(priceTag.string).lower():
                    add = True
                    outputresponse += str(priceTag.a.string)
            # add = False
            # for nameTag in item.find_all('div'):
            #     outputresponse += str(nameTag.string) + ":"
            #     if str(nameTag.get('class')) == '[\'ads-list-photo-item-title\']':
            #         print("3\n")
            #
            #         # if brand.lower() in str(nameTag.string).lower():
            #         add = True
            # if add:
            for priceTag in item.find_all('div'):

                if str(priceTag.get('class')) == '[\'ads-list-photo-item-price\']':
                    priceMultiplier = 1;
                    rawPrice = str(priceTag.string)

                    outputresponse += rawPrice + "<br>"

                    if "€" in rawPrice:
                        rawPrice = rawPrice.replace("€","")
                        priceMultiplier = 20.14
                    if "MDL" in rawPrice:
                        rawPrice = rawPrice.replace("MDL","")
                    rawPrice = rawPrice.replace(" ", "")
                    Price = rawPrice[:len(rawPrice)-1]


                    unitsCount += 1

                    priceInMDL = float(Price) * priceMultiplier

                    sum += priceInMDL
                    if minPrice > priceInMDL:
                        minPrice = priceInMDL
                    if maxPrice < priceInMDL:
                        maxPrice = priceInMDL

    avgUnitPrice = sum/unitsCount
    response = "Results = " + str(unitsCount) + "<br>"
    response += "Average price = " + str(avgUnitPrice) + "<br>"
    response += "Lower price = " + str(minPrice) + "<br>"
    response += "Higher price = " + str(maxPrice) + "<br>"
    return HttpResponse(outputresponse)