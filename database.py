import os
import pymongo
import time
import math




db_url = os.environ['mongo_url']


client = pymongo.MongoClient(db_url)

def addToDatabase(data,username):
  userColl = client.TeacherAssessment.UserData

  if not userColl.find({"_id": username.lower()}).count() > 0:
    userColl.update( {"_id":username}, {"true": True},upsert=True)
  coll = client.TeacherAssessment.TeachData
  for name in data:
    if data[name] == "":
      continue
    key = {"_id": name[:-1]}
    try:
      new_data = {
        "$push":{f"ratings{name[-1]}": [int(data[name]),weeks(),username]},
      }
      coll.update(key,new_data,upsert=True)
    except:
      new_data = {
      "_id":name[:-1],
      f"ratings{name[-1]}": [[int(data[name]),weeks()]]
      }
      coll.update(kewy,new_data,upsert=True)


def createResults():
  coll = client.TeacherAssessment.TeachData
  ml = [[],[],[]]
  
  for doc in coll.find():
    for i in range(3): 
      ml[i].append([doc["_id"][:-1],doc[f'average{i}']])



  ml[0] = sorted(ml[0], key=lambda x: x[1], reverse=True)
  ml[1] = sorted(ml[1], key=lambda x: x[1], reverse=True)
  ml[2] = sorted(ml[2], key=lambda x: x[1], reverse=True)

  temp = [[],[],[]]
  for i in range(len(ml)):
    for j in range(10):
      try:
        temp[i].append(ml[i][j])
      except:
        ...
  return temp


def getRating(elem):
  return elem[1]

''' Input a list of ratings, returns list weighted towards newer entries (depending on weeks)'''
def average_rating(ratings): 
  denominator = 0
  total_rating = 0
  week = ratings[len(ratings) - 1][1]
  for i in range(len(ratings)):
    # scalar = math.log(i+1, 2) * i # 8.2, Pretty weighted, although it staggers after many entries
    # scalar = i # 7.8, Somewhat weighted
    # scalar = i**2 # 8.6, Very weighted, newer entries get a lot more weight
    # scalar = i**3
    weeks_away = week - ratings[i][1]
    if weeks_away > 8:
      scalar = 1
    else:
      scalar = week
    denominator += scalar
    total_rating += ratings[i][0] * scalar
    # print(i, ratings[i])
  if denominator != 0:
    return round((total_rating/denominator),2)

def weeks():
  return math.floor(time.time() / 60 / 60 / 24 / 7) - 2705

def redefAverages():
  coll = client.TeacherAssessment.TeachData

  for doc in coll.find():
    key = {"_id": doc["_id"]}

    for i in range(3):
      newAvg = average_rating(doc[f'ratings{i}'])
      new_data = {'$set': {f"average{i}": newAvg}}
      coll.update(key,new_data,upsert=True)


def check_user_survey(username):
    username = username.lower()
    userColl = client.TeacherAssessment.UserData
    if not userColl.find({"_id":username}).count() > 0:
        return True
    return False

def clearUsernames():
  userColl = client.TeacherAssessment.UserData
  userColl.drop()
  