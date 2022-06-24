import json
import selenium
from selenium import webdriver

class Model:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            indent=4)


opt = webdriver.ChromeOptions()
#opt.add_argument("--")

driver = webdriver.Chrome("/Users/jayantbabu/Downloads/chromedriver")

jsons = Model()


def ParseObject(url, driver):

    driver.get(url)
    jsons.URL = url

    jsondat = json.loads(driver.find_element_by_xpath("//script[@type='application/json']").get_attribute("text"))

    jsons.Name = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["title"]

    jsons.Image = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["image"]["url"]

    jsons.Description = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][1]["subheader"]

    jsons.Lat = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][1]["layouts"][2]["blocks"][0]["map"]["pins"][0]["lat"]
    jsons.Lon = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][1]["layouts"][2]["blocks"][0]["map"]["pins"][0]["lon"]

    banner1 = ""
    banner2 = ""
    try:
        banner1 = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["banners"][0]["lines"][0]["spans"][0]["text"]
        banner2 = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["banners"][0]["lines"][0]["spans"][4]["text"]
    except:
        pass
    jsons.Spotlight = banner1 + " - " + banner2


    cuisineTypes = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["headerTags"]["lines"]
    i = 0
    cuisines = []
    for t in cuisineTypes:
        spans = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["headerTags"]["lines"][i]["spans"]

        j = 0
        for span in spans:
            try:
                text = jsondat["props"]["initialState"]["menuPage"]["menu"]["header"]["headerTags"]["lines"][i]["spans"][j]["text"]
            except:
                pass
            if (text!=None):
                if (i==0):
                    if (text!=None):
                        if (text!='.'):
                            cuisines.append(text)
                    jsons.CuisineTypes = cuisines
                if (i == 1 and j == 2):
                    if("." in text):
                        jsons.Rating = text
                if ("(" in text):
                    jsons.CountRating = text
                if ("Opens" in text or "Closes" in text):
                    jsons.OpenCloseTime = text
                if ("delivery" in text):
                    jsons.DeliveryType = text
                if ("minimum" in text):
                    jsons.MinimumOrderValue = text
            j+=1
        i+=1
    
    menuGroups = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][0]["layouts"]
    groups=[]
    y=0
    for category in menuGroups:
        menuGroup = Model()
        menuGroup.Id = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][0]["layouts"][y]["key"]
        menuGroup.Name = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][0]["layouts"][y]["header"]
        menuGroup.Description = jsondat["props"]["initialState"]["menuPage"]["menu"]["layoutGroups"][0]["layouts"][y]["subheader"]
        menuGroup.MenuItems = []
        groups.append(menuGroup)
        y+=1

    menuItems = jsondat["props"]["initialState"]["menuPage"]["menu"]["meta"]["items"]
    items = []
    x = 0
    for item in menuItems:
        menuItem = Model()
        menuItem.Name = jsondat["props"]["initialState"]["menuPage"]["menu"]["meta"]["items"][x]["name"]
        menuItem.Description = jsondat["props"]["initialState"]["menuPage"]["menu"]["meta"]["items"][x]["description"]
        try:
            menuItem.Image = jsondat["props"]["initialState"]["menuPage"]["menu"]["meta"]["items"][x]["image"]["url"]
        except:
            pass
        menuItem.Price = jsondat["props"]["initialState"]["menuPage"]["menu"]["meta"]["items"][x]["price"]["formatted"]
        categoryId = jsondat["props"]["initialState"]["menuPage"]["menu"]["meta"]["items"][x]["categoryId"]

        group = next((x for x in groups if x.Id == categoryId), None)

        if (group == None):
            dealGroup = Model()
            dealGroup.Name = "Top Deal Group"
            dealGroup.Description = "Deals"
            dealGroup.Id = categoryId

            groups.append(dealGroup)

            if (dealGroup.MenuItems == None):
                currentMenu1 = []
                currentMenu1.append(menuItem)

                dealGroup.MenuItems = currentMenu1
                items.append(menuItem)

            else:
                currentMenu2 = []
                currentMenu2.append(menuItem)
                dealGroup.MenuItems = currentMenu2
                items.append(menuItem)
        else:
            if (group.MenuItems == None):
                currentMenu1 = []
                currentMenu1.append(menuItem)

                group.MenuItems = currentMenu1
                items.append(menuItem)
            else:
                currentMenu2 = group.MenuItems
                currentMenu2.append(menuItem)
                group.MenuItems = currentMenu2
                items.append(menuItem)
        x+=1
    jsons.MenuGroup = groups
    return jsons

data = ParseObject("https://deliveroo.co.uk/menu/london/park-royal/24-7-booze-express-wembley/?day=today&geohash=gcpvn1m3qs1r&time=ASAP", driver)

with open('/Users/jayantbabu/Downloads/data.json', 'w') as f:
    f.write(data.toJSON())