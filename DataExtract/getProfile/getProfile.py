import bs4
import requests
import pandas

class getProfile:
    file_enum = {'\Data\Profile_Men.csv', '\Data\Profile_Women.csv', '\Data\Profile_Master_Men_45.csv', '\Data\Profile_Master_Women_45.csv',
             '\Data\Profile_Master_Men_50.csv', '\Data\Profile_Master Women_50.csv', '\Data\Profile_Master_Men_55.csv', '\Data\Profile_Master_Women_55.csv',
             '\Data\Profile_Master_Men_60.csv', '\Data\Profile_Master_Women_60.csv', '\Data\Profile_Team.csv', '\Data\Profile_Master_Men_40.csv',
             '\Data\Profile_Master_Women_40.csv', '\Data\Profile_Teen_Boy_14.csv', '\Data\Profile_Teen_Girl_14.csv', '\Data\Profile_Teen_Boy_16.csv',
             '\Data\Profile_Teen_Girl_16.csv'}
            
    #Open the CSV and read in the data
    Athletes = pandas.DataFrame(columns=('Name', 'Affiliate', 'Age', 'Height', 'Weight', 'Sprint 400m', 
                                   'Clean & Jerk', 'Snatch', 'Deadlift', 'Back Squat', 'Max Pull-ups'))
                                   
    def download(self, ID, div):
        #loop through out athlete ID list accessing each profile
        for profile in ID:
            url = 'http://games.crossfit.com/athlete/' + str(profile)
            response = requests.get(url, 
                                    headers={
                                   "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                                    })
            response.raise_for_status()
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            
            #grab name, affiliate
            name = soup.find(id="page-title").string.extract()
            name = name[9:]
            affiliate_txt = soup.find("dt", text="Affiliate:").parent.findNextSiblings("dd")[0].string
            
            #collect age, height, weight
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

            #collect maxes
            sprint = soup.find("td", text="Sprint 400m").parent.findNextSiblings("td")[0].string
            clean_jerk = soup.find("td", text="Clean & Jerk").parent.findNextSiblings("td")[0].string
            snatch = soup.find("td", text="Snatch").parent.findNextSiblings("td")[0].string
            deadlift = soup.find("td", text="Deadlift").parent.findNextSiblings("td")[0].string
            back_squat = soup.find("td", text="Back Squat").parent.findNextSiblings("td")[0].string
            pullups = soup.find("td", text="Max Pull-ups").parent.findNextSiblings("td")[0].string
            
            Athletes.loc[profile] = (name, affiliate_txt, age, height, weight, sprint, clean_jerk, snatch, deadlift, back_squat, pullups)
            Athletes.to_csv(path_or_buf=file_enum[div-1])