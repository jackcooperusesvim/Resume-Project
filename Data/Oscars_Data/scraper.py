import selenium 
from icecream import ic
import pickle as pkl
from selenium.webdriver.common.by import By
import datetime
from bs4 import BeautifulSoup, NavigableString

THIS_YEAR = datetime.date.year
FIRST_OSCARS_YEAR = 1920
# I generally use selenium because of the js compatibility and the ability to navigate a page.
# It might be kind of overkill for this one, but I would prefer to not have to rewrite this with
# requests
class award_category:
    def __init__(self,  winner, *nominations,year = 0):
        self.year = year
        self.nominations = list(nominations)
        self.winner = winner

    def nominated(self, nomination):
        self.nominations.append(nomination)


class award:
    def __init__(self,views_row_div):
        self.raw = views_row_div


# Here I use the fact that Dictionaries are pass-by-reference in python to create the2
# python approximation similar to Go Channels

def read_oscars_page(output_dict,year):
    ic("creating webdriver...")
    driver = selenium.webdriver.Chrome()
    ic("opening website...")
    driver.get("https://www.oscars.org/oscars/ceremonies/"+str(year))

    ic("getting html...")
    root_el= driver.find_element(By.XPATH,"//*")

    source = root_el.get_attribute("outerHTML")
    soup = BeautifulSoup(source.encode("utf-8"),"lxml")

    ic("finding the 'quicktabs-tabpage-honorees-0' div \non Enter...")

    info = soup.find("div", id = "quicktabs-tabpage-honorees-0")

    if info == None: 
        raise Exception("could not find a div with id=\"quicktabs-tabpage-honorees-0\"")

    if type(info) == NavigableString:
        raise Exception("What the actual...")

    ic("searching the tree for the view-content div ...")

    info = info.extract()
    ic("step1")
    ic(type(info))
    ic(len(info))
    info = info.contents[0]
    ic("step2")
    ic(type(info))
    ic(len(info))
    info = info.contents
    ic(type(info[0].extract()))
    #THE PROBLEMS ARE IN THE ABOVE SECTION

    categories = {}
    ic("iterating over 'view-grouping's ...")
    for vg_element in info:
        header = vg_element.findChildren(_class = "view-grouping-header")[0]
        content = vg_element.findChildren(_class = "view-grouping-content")
        category = header.h2.string

        working_on_winners = True
        winners = []
        nominees = []
        index = 0
        for elem in content.contents:
            if index != 0:
                if elem.name == "h3":
                    working_on_winners = False
            if working_on_winners:
                winners.append(award(elem))
            else:
                nominees.append(award(elem))

            index+=1

        categories[category] = {"winners": winners,"nominees": nominees,}
    output_dict[str(year)] = categories


if __name__ == "__main__":
    output_dict = dict()
    read_oscars_page(output_dict, 2016)
    with open('dta2016.pkl','wb') as file:
        pkl.dump(output_dict, file)


#
# def read_oscars_async():
#
#     batch_size = 20
#     output = {}
#     i = FIRST_OSCARS_YEAR
#         threading.Thread(target=read_oscars_page())
#         i+=1
# ~
