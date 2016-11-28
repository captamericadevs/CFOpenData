import requests
import pandas

class getAffiliates():   
    def jsonParseHandler(self, element, index):
        try:
            return element[index]
        except KeyError as e:
            return ""
            
    def __init__(self):
        self.Affiliate = pandas.DataFrame(columns=('Name', 'Website', 'Address', 'City', 'State', 'Country', 'Zip', 'Active')) 
        
        url = 'https://www.crossfit.com/cf/find-a-box.php?'
        page = 1
        while True:
            response = requests.get(url, params={
                                    "page":page,
                                    "country":"",
                                    "state":"",
                                    "city":"",
                                    "type":"Commercial"},
                                    headers={
                                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36"
                                    }).json()
            print("Downloading affiliate list page " + str(page) + "...")
            if response["affiliates"] == []:
                break
            else:
                for gym in response['affiliates']:
                    Id = self.jsonParseHandler(gym, 'aid')
                    Name = self.jsonParseHandler(gym, 'name')
                    Web = self.jsonParseHandler(gym, 'website')
                    Addy = self.jsonParseHandler(gym, 'address')
                    City = self.jsonParseHandler(gym, 'city')
                    State = self.jsonParseHandler(gym, 'state_code')
                    Country = self.jsonParseHandler(gym, 'country')
                    Zip = self.jsonParseHandler(gym, 'zip')
                    Active = self.jsonParseHandler(gym, 'active')
                    self.Affiliate.loc[Id] = (Name, Web, Addy, City, State, Country, Zip, Active)
                page = page + 1
  
        filename = 'Affiliate_List.csv'
        self.Affiliate.to_csv(path_or_buf=filename)
        print(filename + " written out.")
        
   
  