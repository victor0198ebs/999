from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup

def getTitle(titleString):
    brand = "Volkswagen"
    model = "Passat"
    if (brand in titleString) and (model in titleString):
        print("--"+titleString+"--")
        return True
    else:
        return False

def getPrice(price):
    priceMultiplier = 1;
    rawPrice = price
    if "€" in rawPrice:
        rawPrice = rawPrice.replace("€", "")
        priceMultiplier = 20.14
    if "MDL" in rawPrice:
        rawPrice = rawPrice.replace("MDL", "")
    rawPrice = rawPrice.replace(" ", "")
    Price = rawPrice[:len(rawPrice) - 1]
    if Price == '':
        return
    print("--" + str(int(Price)) + "--")
    priceInMDL = float(Price) * priceMultiplier
    return priceInMDL

def processItems(items):
    title = ""
    year = 0
    priceInMDL = 0

    for itemDIV in items.find_all('div'):
        if str(itemDIV.get('class')) == '[\'ads-list-table-title-wrapper\']':
            title = getTitle(str(itemDIV.a.string))
            if not title:
                return


    for yearTDpriceTD in items.find_all('td'):
        if str(yearTDpriceTD.get('class')) == '[\'ads-list-table-col-3\', \'feature-19\']':
            rawYear = str(yearTDpriceTD.string).replace(" ", "")
            year=int(rawYear)
            print("--"+str(int(year))+"--")
        if str(yearTDpriceTD.get('class')) == '[\'ads-list-table-price\', \'feature-2\']':
            price=str(yearTDpriceTD.string)
            price = getPrice(price)
            if not price:
                return


    return (year, price)




def index(request):
    outputresponse = ""
    itemsList = []
    startYear = 2006
    endYear = 2010
    for page in range(1,6):
        getParams = {'page': str(page)}
        r = requests.get('https://999.md/ro/list/transport/cars?applied=1&eo=20&view_type=short&r_6_2_unit=eur&ef=260&ef=6&ef=1&ef=7&o_1_21_20=117&r_6_2_to=&r_7_19_from=2006&o_260_1=776&r_7_19_to=2010&r_6_2_from=', data=getParams)
        strFormat = str(r.text)

        soup = BeautifulSoup(strFormat, 'html.parser')

        for container in soup.find_all('div'):

            if str(container.get('data-view-type'))=="short": # got container

                for items in container.find_all('tr'):

                    titleYearPrice = processItems(items) #get title, year, price of one item



                    if titleYearPrice:
                        outputresponse += str(titleYearPrice) + "<br>"
                        itemsList.append(list(titleYearPrice))
                        print(titleYearPrice)

    groupedByYears=[]
    for year in range(startYear, endYear+1):
        groupedByYears.append([0,0])
    print("---making groups---")
    for year in range(startYear, endYear+1):
        for itemList in itemsList:
            print(itemList)
            if itemList[0] == year:
                print("yes")
                groupedByYears[year-startYear][0]+=1
                groupedByYears[year - startYear][1]+=itemList[1]
    print("---groups by one----")
    for oneGroup in groupedByYears:
        print(oneGroup)

    for year in range(startYear, endYear + 1):
        print(str(year) + " -> "+ str(round(groupedByYears[year-startYear][1]/groupedByYears[year-startYear][0],2)))

    return HttpResponse(outputresponse)


