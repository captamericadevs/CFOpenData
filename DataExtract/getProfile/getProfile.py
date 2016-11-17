from BeautifulSoup import BeautifulSoup
import urllib3

#Open the CSV and read in the data
def getProfile(ID):
    url = 'http://games.crossfit.com/athlete/' + str(ID)
    req = urllib2.Request(url)
    req.add_header("User-Agent", "Mozilla/5.0")
    source = urllib2.urlopen(req)
    page = source.read()
    soup = BeautifulSoup(page)
    age = int(soup.find("dt", text="Age:").parent.findNextSiblings("dd")[0].string)
    height_txt = soup.find("dt", text="Height:").parent.findNextSiblings("dd")[0].string
    weight_txt = soup.find("dt", text="Weight:").parent.findNextSiblings("dd")[0].string

    if "cm" in height_txt:
        height = int(int(height_txt)/2.54)

    else:
        if len(height_txt) == 14:
            height = int(height_txt[0])*12 + int(height_txt[7])
        else:
            height = int(height_txt[0])*12 + int(height_txt[7:9])

    if "lb" in weight_txt:
        weight = int(weight_txt[:-3])
    else:
        weight = int(int(weight_txt[:-3])*0.453592)

    return weight

print grab_data(4623)
print 'ya'