from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup


# item means car ;)

def index(request):
    itemsList = []
    startYear = 2005
    endYear = 2017
    page_nr = 1
    pages = 1
    cars = 0
    # loop through pages
    while page_nr <= pages:

        # set variable parameters
        # getParams = {'r_7_19_from': str(startYear), 'r_7_19_to': str(endYear), 'page': str(page_nr)}
        r = requests.get(
            'https://999.md/ro/list/transport/cars?applied=1&ef=260&ef=6&r_6_2_from=&r_6_2_to=&view_type=short&r_6_2_unit=eur&ef=1&eo=20&o_1_21_20=117&ef=7&r_7_19_from=2005&r_7_19_to=2017&page=' + str(
                page_nr))
        strFormat = str(r.text)

        soup = BeautifulSoup(strFormat, 'html.parser')

        # refresh last page's number, from current page's navigation buttons
        for navs in soup.find_all('nav'):
            for page in navs.find_all('li'):
                if is_number(str(page.a.string)):
                    pages = int(page.a.string)

        # search for container with results
        for container in soup.find_all('div'):
            # if got page's container with items

            if (str(container.get('data-view-type')) == "short") and (
                    str(container.get('class')) == '[\'items__list__container\']'):
                print(container)
                for item in container.find_all('tr'):
                    print(item)
                    titleYearPrice = processItem(item)  # get title, year and price of one item
                    # if got valid data, append in list

                    if titleYearPrice:
                        itemsList.append(list(titleYearPrice))
        page_nr += 1

    groupedByYears = []

    # for item in itemsList:

    for year in range(startYear, endYear + 1):
        groupedByYears.append([0, 0, 0, 500000, 0])
        groupedByYears[year - startYear][0] = year
        for itemList in itemsList:
            # print(str(itemList[1]))
            if itemList[0] == year:
                # set cars number
                groupedByYears[year - startYear][1] += 1
                # set sum of prices per year
                groupedByYears[year - startYear][2] += round(itemList[1])
                # update min price
                if groupedByYears[year - startYear][3] > itemList[1] and itemList[1] != 0:
                    groupedByYears[year - startYear][3] = round(itemList[1])
                # update max price
                if groupedByYears[year - startYear][4] < itemList[1]:
                    groupedByYears[year - startYear][4] = round(itemList[1])


    return HttpResponse(makeHTMLResponse(groupedByYears))


def confirmTitle(titleString):
    brandAndModel = "Passat"
    if (brandAndModel in titleString):
        return True
    else:
        return False


def getPrice(rawPrice):
    priceMultiplier = 1;

    if "€" in rawPrice:
        rawPrice = rawPrice.replace("€", "")
        priceMultiplier = 20.14

    if "$" in rawPrice:
        rawPrice = rawPrice.replace("$", "")
        priceMultiplier = 17.89

    if "MDL" in rawPrice:
        rawPrice = rawPrice.replace("MDL", "")

    rawPrice = rawPrice.replace(" ", "")
    Price = rawPrice.rstrip()

    # check for empty strings
    if not Price:
        return

    priceInMDL = float(Price) * priceMultiplier

    return priceInMDL


def processItem(item):
    year = 0
    itemPrice = 0
    for itemDIV in item.find_all('div'):
        if str(itemDIV.get('class')) == '[\'ads-list-table-title-wrapper\']':
            title = confirmTitle(str(itemDIV.a.string))
            if not title:
                return False

    for yearTDpriceTD in item.find_all('td'):
        if str(yearTDpriceTD.get('class')) == '[\'ads-list-table-col-3\', \'feature-19\']':
            rawYear = str(yearTDpriceTD.string).replace(" ", "")
            if is_number(rawYear):
                year = int(rawYear)
            else:
                return False

        if str(yearTDpriceTD.get('class')) == '[\'ads-list-table-price\', \'feature-2\']':
            itemPrice = getPrice(str(yearTDpriceTD.string))
            if not is_number(itemPrice):
                return False

    return (year, itemPrice)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def makeHTMLResponse(groupedByYears):

    response = """<html>
            <head>
                <style>
                    th{
                        width: 120px;
                    }
                </style>
            </head>
              <body>
                <center>
                    <table border=1>
                      <tr>
                        <th>Year</th>
                        <th>Cars number</th>
                        <th>Average price</th>
                        <th>Lowest price</th>
                        <th>Highest price</th>
                      </tr>"""
    for oneGroup in groupedByYears:
        print(str(oneGroup))
        response += "<tr><td>" + str(oneGroup[0]) + "</td><td>" + str(oneGroup[1]) + "</td><td>" + str(
            "{:,.2f}".format(round(oneGroup[2] / oneGroup[1]))) + "&nbspMDL</td><td>" + str(
            "{:,.2f}".format(oneGroup[3])) + "&nbspMDL</td><td>" + str(
            "{:,.2f}".format(oneGroup[4])) + "&nbspMDL</tr>"
    response += """</tr>
                        </table>
                    <center>
                  </body>
                </html>"""

    return response
