import requests
from bs4 import BeautifulSoup
import jsonfinder as jf
import time
import pickle

departments = {}

mainurl = 'https://courses.illinois.edu'
f18schedule = "https://courses.illinois.edu/schedule/DEFAULT/DEFAULT"
source_code = requests.get(f18schedule).text
soup = BeautifulSoup(source_code, 'lxml')



txt = soup.find_all('td')

#get departments + link to the page with courses offered by the department
for i in range(0, len(txt) - 1, 2):
    key = txt[i].get_text().strip()
    departments[key] = {}
    departments[key]['link'] = txt[i + 1].find('a')['href'].strip()

#get courses offered by a specific department + link to each of them
for k in departments.keys():
    coursesPage = BeautifulSoup(requests.get(mainurl + departments[k]['link']).text, 'lxml').find_all('td')

    for i in range(0, len(coursesPage) - 1, 2):
        course = coursesPage[i].get_text().strip()
        departments[k][course] = {}
        departments[k][course]['link'] = coursesPage[i + 1].find('a')['href'].strip()


#get all the details about all the courses
for k in departments:
    for cls in departments[k].keys():
        #print(1)
        if(cls != 'link'):
            inst = BeautifulSoup(requests.get(mainurl + departments[k][cls]['link']).text, 'lxml')
            data = jf.only_json(inst.find_all("script")[3].string)[2]
            attrs = ['instructor', 'location', 'time', 'type', 'day']
            for j in range(len(data)):
                crn = data[j]['crn']
                departments[k][cls][crn] = {}
                obj = departments[k][cls][crn]
                for atr in attrs:
                    #print(atr)
                    details = BeautifulSoup(data[j][atr], 'lxml').find_all('div', {"class":"app-meeting"})
                    #print(details[0].text.strip())
                    obj[atr] = details[0].text.strip()
        time.sleep(0.05)

#save the file
with open('data.p', 'wb') as fp:
    pickle.dump(departments, fp, protocol=pickle.HIGHEST_PROTOCOL)

