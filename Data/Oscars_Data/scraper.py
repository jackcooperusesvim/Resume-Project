import selenium 
import queue
import threading
from icecream import ic
from selenium.webdriver.common.by import By
import datetime
from bs4 import BeautifulSoup, NavigableString, Tag
import requests

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


id = 0

class award:
    def __init__(self,views_row_div,ncf):
        # ic("award created")
        if ncf:
            self.work = views_row_div.find_all("span",{"class":"field-content"})[0].string
            self.name =views_row_div.find("h4").string
        else:
            self.name= views_row_div.find_all("span",{"class":"field-content"})[0].string.strip()
            self.work= views_row_div.find("h4").string.strip()
        self.year = 0
        self.id= -1
        self.winner = False
        self.category = ""
        # ic(str(self.name))
        # ic(str(self.work))
    def __str__(self):
        if self.winner:
            typestring = "won"
        else:
            typestring = "nominated"

        return "{},{},{},{},{},{}\n".format(self.category,self.work,self.name,str(self.year),typestring)

#NOTE: This function should fix at least 90% of the problem with names entering in the wrong order
def names_come_first(category: str):
    if category.find("Actor") != -1:
        return True
    if category.find("Actress") != -1:
        return True
    return False


def remove_navstrings(elements):
    out = []
    for tag in elements:
        if type(tag) == Tag:
            out.append(tag)
    return out
# Here I use the fact that Dictionaries are pass-by-reference in python to create the
# python approximation similar to Go Channels

def read_oscars_page(queue,year):
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
    ic(info)

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
        #ncf stands for names_come_first. see the function of the same name to see why it is necessary
        ncf = names_come_first(category)
        # ic(category)

        working_on_winners = True
        for elem in remove_navstrings(content.contents)[1:]:
            if elem.name == "h3":
                working_on_winners = False
                # ic("moving on to nominations")
                continue
            else:
                awd = award(elem,ncf)
                awd.year = year 
                awd.category = category
                global id
                awd.id= id
                if working_on_winners:
                    awd.winner = True
                queue.put(awd)
                id+=1

if __name__ == "__main__":
    start = 2020
    end = 2024
    q = queue.Queue()
    concurrent_threads = 15
    current_threadid = 0
    while current_threadid<end:

        current_threads = []
        i=0
        while i<concurrent_threads:
            t = threading.Thread(target=read_oscars_page, args = (q,start+current_threadid))
            t.start()
            current_threads.append(t)
            i+=1
            current_threadid+=1

        for thread in current_threads:
            thread.join()

    outstr = ""
    while not q.empty():
        award = q.get()
        outstr = outstr+str(award)
        ic(str(award))

    with open('oscars.csv','w') as file:
        file.write(outstr)

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
