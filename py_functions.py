import os
import requests
from lxml import html # Oh hello
import hmac, hashlib, base64
from bs4 import BeautifulSoup
import datetime


def hash(password,contextdata):
    '''
    Something that is needed for powerschool login. idk what it does lol
    '''
    return hmac.new(contextdata.encode('ascii'), base64.b64encode(hashlib.md5(password.encode('ascii')).digest()).replace(b"=", b""), hashlib.md5).hexdigest()


def get_user_data(user,pw):
    '''
    Returns a list containg powerschool information: [name, username, classes]; False if incorrect credentials, "Parrent" if they are a parrent
    '''
    s=requests.Session()
    url = os.environ['ps_url']
    result = s.get(url, verify=False)
    tree = html.fromstring(result.text)
    pstoken = list(set(tree.xpath("//*[@id=\"LoginForm\"]/input[1]/@value")))[0]
    contextdata = list(set(tree.xpath("//input[@id=\"contextData\"]/@value")))[0]
    new_pw=hash(pw,contextdata)
    payload={
        'pstoken':pstoken,
        'contextData':contextdata,
        'dbpw':new_pw,
        'ldappassword':pw,
        'account':user,
        'pw':pw
    }
    p = s.post(url, data=payload)

    soup = BeautifulSoup(p.text, 'lxml')
    print(user, pw)
    body = soup.find('body')

    valid_blocks = ('A(A)', 'B(A)', 'C(A)', 'D(A)', 'E(A)', 'F(A)', 'G(A)', 'H(A)')
    return_list = []
    number_of_classes = 0
    for i in soup.find_all('tr', class_='center'): # Block
        for x in i.find_all('td', {'align': 'left'}): # Class Name
            if i.td:
                if i.td.text in valid_blocks:
                    for y in i.find_all('a', class_='button mini dialogM'):
                        teacher = str(y["title"].replace('Details about ', ''))
                        block = i.td.text.replace('(A)', '').rstrip()
                        class_name = x.text.split('Email', 1)[0]
                        class_name = class_name.rstrip()
                        return_list.append([block, teacher, class_name])
                        number_of_classes += 1
    if number_of_classes == 0:
        return False
    if soup.find_all("body", {"class": "psparent Student"}) == 0:
        return "PARENT"
    name = soup.find("span", {"id": "firstlast"}).text
    return [name, user, return_list]

def get_time():
  return datetime.time
