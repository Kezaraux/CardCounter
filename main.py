from __future__ import print_function
from titlecase import titlecase
from urllib.request import urlopen
from bs4 import BeautifulSoup
from operator import itemgetter
import ast
import os.path

cards_to_total = {}
get_info = False
PATH = "./cards.data"
DATA_FILE = "cards.data"



#Methods that allow the user to interact with the dictionary of cards
def update_dict(d):
    """(dict of {str:int}) -> None
    Opens a file and updates the dictionary with the information
    contained within the file.
    """
    fname = input("Enter the file name: ")
    try:
        file = open(fname)
        for line in file:
            text = fix_odd_cards(fix_with(titlecase(line.rstrip())))
            if "=" in text or text.endswith(":") or not text:
                continue
            else:
                d[text] = d.get(text, 0) + 1
    except IOError:
        print("The file name you gave does not exist \n")
        update_dict(d)

def list_cards(d, val):
    """(dict of {str:int}, bool) -> None
    Prints all keys and their values in the dictionary in numerically descending, proper
    alphabetical order, and if the provided boolean is true, provide information for each
    key taken from a website
    """
    for k,v in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]), reverse=False):   #Old sorting code: sorted(d.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        print(k, ": ", v, sep="")
        if val:
            try:
                try:
                    tt = get_card_types(k)
                    ttt = make_readable(tt)
                    print(ttt)
                except IndexError:
                    print("There was an error getting the data")
            except NameError:
                print("Brendan sucks at finding error names")

def find_cards(phrase, d):
    """(str, dict of {str:int}) -> None
    Prints all keys containing the search phrase in the dictionary and their values
    """
    ls = ("%s: %s" % (k, d.get(k)) for k in d if phrase.lower().strip() in k.lower())
    total_uni = 0
    for k in d:
        if phrase.lower().strip() in k.lower():
            total_uni += 1
    print("Search returned %s unique cards." % total_uni)
    total_card = 0
    for k in d:
        if phrase.lower().strip() in k.lower():
            total_card += d.get(k)
    print("You own %s cards returned from the search." % total_card)
    for item in ls:
        print(item)

def find_with_filter(d):
    """(dict of {str:int}) -> None

    """
    q = input("[mon] Filter by Monster cards\n[spell] Filter by Spell cards\n[trap] Filter by Trap cards\nEnter your filter: ").lower()
    if q == "mon":
        phr = input("Enter the phrase you would like to search for: ")
        ls = ("%s: %s" % (k, d.get(k)) for k in d if phr.lower().strip() in k.lower())
        print("")
        for item in ls:
            if (not get_card_types(item[:item.find(":")])[0] == "Spell") and (not get_card_types(item[:item.find(":")])[0] == "Trap"):
                print(item)
    elif q == "spell":
        phr = input("Enter the phrase you would like to search for: ")
        print("")
        ls = ("%s: %s" % (k, d.get(k)) for k in d if phr.lower().strip() in k.lower())
        for item in ls:
            if get_card_types(item[:item.find(":")])[0] == "Spell":
                print(item)
    elif q == "trap":
        phr = input("Enter the phrase you would like to search for: ")
        print("")
        ls = ("%s: %s" % (k, d.get(k)) for k in d if phr.lower().strip() in k.lower())
        for item in ls:
            if get_card_types(item[:item.find(":")])[0] == "Trap":
                print(item)
    else:
        print("That was not a valid option. Exiting the search.")

def total_cards(d):
    """

    """
    total = 0
    for key in d:
        total += d[key]
    return total



#Methods for getting and processing the information
def convert_to_web(s):
    """(str) -> str
    Replaces all spaces with an underscore
    """
    ret = ""
    for i in range(len(s)):
        if not s[i] == " ":
                if not s[i] == "?":
                    ret += s[i]
                else:
                    ret += "%3F"
        else:
            ret += "_"
    return ret

def fix_with(text):
    """(str) -> str
    Replaces the word With (containing a capital) with a lower case version
    """
    if "With" in text:
        return text.replace("With", "with")
    else:
        return text

def fix_odd_cards(text):
    """(str) -> str
    Fixes any odd card names that don't conform with the usual
    """
    if text == "Abyss-Scale of Cetus":
        return "Abyss-scale of Cetus"
    elif text == "Burial From a Different Dimension":
        return "Burial from a Different Dimension"
    elif text == "Re-Qliate":
        return "Re-qliate"
    elif text == "F.A. Hang on Mach":
        return "F.A. Hang On Mach"
    else:
        return text
        

def get_types(s):
    """(???) -> list of int
    Returns a list of indices where "> was found
    """
    start = 0
    while True:
        start = s.find('">', start)
        if start == -1: return
        yield start
        start += len('">')

def get_types_end(s):
    """(???) -> list of int
    Returns a list of indices where </a> was found
    """
    start = 0
    while True:
        start = s.find('</a>', start)
        if start == -1: return
        yield start
        start += len('</a>')

def get_table_block(item, search_term):
    """(???, str) -> ???
    Returns and object containing the sought phrase
    """
    for thing in item:
        if search_term in str(thing):
            return thing
    return

def get_wanted_info(item):
    """(???) -> list of str
    Returns a list of card types taken from the object
    """
    type_ind = list(get_types(item))
    type_end_ind = list(get_types_end(item))
    info = []
    for index in range(len(type_ind)):
        info.append(item[type_ind[index] + 2:type_end_ind[index]])
    del info[0]
    return info

def get_card_types(mon_name):
    """(str) -> list of str
    Returns all types that a card of provided name is.
    """
    web_name = convert_to_web(mon_name)
    page = urlopen("http://yugioh.wikia.com/wiki/" + web_name)
    soup = BeautifulSoup(page, "html.parser")
    soup.prettify()

    #Get all the tables present on the page
    tables = soup.find_all("table")
    #Generally the first table is the only table we need
    table_tr = tables[0].find_all("tr")
    #Just incase the first table is a notice, that we don't want, we do this
    if "notice.png" in str(table_tr):
        table_tr = tables[1].find_all("tr")
    a_tags = []
    #Find all the a tags in the table, the information we want is there
    for tr in table_tr:
        a_tags.append(tr.find_all("a", href=True))
    #Determine what card type the card is, handle the information accordingly
    test_block = str(get_table_block(a_tags, "Card type"))
    card_type = get_wanted_info(test_block)[0]
    if card_type == "Monster":
        block = str(get_table_block(a_tags, "Type"))
        return get_wanted_info(block)
    else:
        ret = [card_type]
        prop_block = str(get_table_block(a_tags, "Property"))
        ret.append(get_wanted_info(prop_block)[0])
        return ret

def make_readable(lst):
    """(list of str) -> str
    Makes the provided list into something easily readable
    """
    ret = "["
    for item in lst:
        ret += item + "/"
    ret = ret[:-1] + "]"
    return ret


#Methods for reading/writing
def write_to_file(fname, obj):
    """ (str, Object) -> None
    Writes the object to a file
    """
    with open(DATA_FILE, "w") as file:
        file.write(str(cards_to_total))

def read_from_file(fname):
    """ (str) -> Object
    Returns whatever it read from the file
    """
    with open(DATA_FILE, "r") as file:
        dat = file.read()
        return ast.literal_eval(dat)



#The main program, I guess?
if __name__ == "__main__":
    #See if the user wants to update the dictionary on first run
    if not cards_to_total and not os.path.isfile(PATH):
        q = input("The current card list is empty and there is no data file, would you like to update [y/n]? ")
        if q.lower() == "y":
            update_dict(cards_to_total)
    elif os.path.isfile(PATH) and not cards_to_total:
        q = input("There is an existing card list. Do you want to replace it with a new list [y/n]? ")
        if q.lower() == "y":
            cards_to_total = {}
            update_dict(cards_to_total)
        else:
            cards_to_total = read_from_file(DATA_FILE)
    inp = ""
    while inp != "qqq":
        inp = input("[list] to list cards\n[search] to search\n[update] to update\n[opt] for options\n[del] to delete all data (saved and current)\n[qqq] to quit\nMake your selection: ")
        #Main "menu" of options happens here
        if inp.lower() == "list":               #LIST
            print("")
            list_cards(cards_to_total, get_info)
            print("")
        elif inp.lower() == "search":           #SEARCH
            question = input("Did you want to filter the search [y/n]? ").lower()
            if question == "y":
                find_with_filter(cards_to_total)
                print("")
            else:
                phr = input("Enter the search phrase: ")
                print("")
                find_cards(phr, cards_to_total)
                print("")
        elif inp.lower() == "total":
            print("There are %s cards in the current list" % total_cards(cards_to_total))
        elif inp.lower() == "update":           #UPDATE
            update_dict(cards_to_total)
        elif inp.lower() == "opt":              #OPTIONS
            q = input("Display card data when listing [y/n]? ")
            if q.lower() == "y":
                get_info = True
            else:
                get_info = False
        elif inp.lower() == "del":              #DELETION
            cards_to_total = {}
            write_to_file(cards_to_total, "w")
            print("The current list has been deleted.")
        elif inp.lower() == "total":
            total = 0
        elif inp.lower() == "qqq":              #QUIT
            print("Saving current list...")
            write_to_file(DATA_FILE, cards_to_total)
            print("Have a good day!")
        else:
            print("Did not recognize the term.")
