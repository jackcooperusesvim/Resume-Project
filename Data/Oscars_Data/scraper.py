import selenium 
from icecream import ic
import pickle as pkl
from selenium.webdriver.common.by import By
import datetime
from bs4 import BeautifulSoup, NavigableString, Tag

THIS_YEAR = datetime.date.year
FIRST_OSCARS_YEAR = 1920
# I generally use selenium because of the js compatibility and the ability to navigate a page.
# It might be kind of overkill for this one, but I would prefer to not have to rewrite this with
# requests.

# TODO: At this point the parser is pretty much complete. The only problem is that the 
# order of Names and Works seems to change according to the category. In Actor and Actress name 
# comes first but not so in other categories

# NOTE:
#This comment is after I made the first commit. I spent like a good 3 hours getting mad at bs4, 
#but it turns out that something with the way selenium reads the html results in this weird parsing from 
# BeautifulSoup where completely empty NavigableStrings are parsed according to regular patterns between tags. 
#I should have just used requests, but now that I know how it works I can finish the rest with selenium
class award_category:
    def __init__(self,  winner, *nominations,year = 0):
        self.year = year
        self.nominations = list(nominations)
        self.winner = winner

    def nominated(self, nomination):
        self.nominations.append(nomination)


class award:
    def __init__(self,views_row_div):
        ic("award created")
        try:
            self.work = views_row_div.find_all("span",{"class":"field-content"})[0].string
        except:
            self.work = None
        try:
            self.name =views_row_div.find("h4").string
        except:
            self.name = None
        ic("    "+str(self.name))
        ic("    "+str(self.work))


def remove_navstrings(elements):
    out = []
    for tag in elements:
        if type(tag) == Tag:
            out.append(tag)
    return out
# Here I use the fact that Dictionaries are pass-by-reference in python to create the
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

    ic("finding the 'quicktabs-tabpage-honorees-0' div...")

    info = soup.find("div", id = "quicktabs-tabpage-honorees-0")
    ic("step1")
    ic(type(info))
    ic(len(info))

    if info == None: 
        raise Exception("could not find a div with id=\"quicktabs-tabpage-honorees-0\"")

    if type(info) == NavigableString:
        raise Exception("What the actual...")

    ic("searching the tree for the view-content div ...")

    info = info.contents
    test_case = info[0]
    ic("step2")
    ic(type(test_case))
    ic(len(info))
    ic("Searching...")
    info = info[0].contents
    ic("step3")
    for div in info:
        ic(type(div))
    ic(type(info))
    ic(len(info))
    # Magic number. I know. I don't care. I am leaving this section unexplained. Deal with it.
    ic("removing NavigableStrings")
    info = remove_navstrings(info)
    ic("Searching...")
    info = info[2].contents
    ic("step4")
    for div in info:
        ic(type(div))
    ic(type(info))
    ic(len(info))

    # This line is necessary to prevent NavigableStrings from messing stuff up
    ic("removing NavigableStrings")
    info = remove_navstrings(info)
    ic(len(info))

    categories = {}
    ic("iterating over 'view-grouping's ...")
    iter = 0
    for vg_element in info:
        ic(iter)
        iter+=1
        vg_element = vg_element("div",recursive = False)
        header = vg_element[0]
        content = vg_element[1]

        category = header.h2.string
        ic(category)

        working_on_winners = True
        winners = []
        nominees = []
        for elem in remove_navstrings(content.contents)[1:]:
            if elem.name == "h3":
                working_on_winners = False
                ic("moving on to nominations")
                continue
            else:
                if working_on_winners:
                    winners.append(award(elem))
                else:
                    nominees.append(award(elem))


        categories[category] = {"winners": winners,"nominees": nominees,}
    output_dict[str(year)] = categories


if __name__ == "__main__":
    output_dict = dict()
    read_oscars_page(output_dict, 2016)
    # with open('dta2016.pkl','wb') as file:
    #     pkl.dump(output_dict, file)


#
# def read_oscars_async():
#
#     batch_size = 20
#     output = {}
#     i = FIRST_OSCARS_YEAR
#         threading.Thread(target=read_oscars_page())
#         i+=1
# ~
