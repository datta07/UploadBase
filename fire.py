import requests
import json


def set_firebase(date,value,link):
	url1='https://eenadu.firebaseio.com/een/'+date+'/.json'
	r = json.dumps({value:link})
	to_database = json.loads(r)
	requests.patch(url = url1 , json = to_database)


def get_firebase(date,value):
	url1='https://eenadu.firebaseio.com/een/'+date+'/'+value+'/.json'
	auth_key = 'BhzzvcWDRhSjLCwfcekcBvdXKNy0hXuqju19GD4Z'
	try:
		r1=requests.get(url1 + '?auth=' + auth_key)
		return r1.json()
	except Exception as e:
		print("internet fault")
		return None
