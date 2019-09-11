from django.http import HttpResponse
from django.shortcuts import render
from django.template.context_processors import csrf
#import pyrebase
import random
import cx_Oracle as cx
from . import image_capture
from . import model
import time
conn = cx.connect('sr/sr')
cur = conn.cursor()
'''
#import win10toast
#t = win10toast.ToastNotifier()
'''
moh = None
itemList = []
refresh = 0
def postenter(request):

	item = request.POST.get('item_name')
	exp_per = request.POST.get('expiry_period')
	# auth = firebase.auth()
	# #user = auth.sign_in_with_email_and_password("mukulbindal170299@gmail.com","123456789")
	# print(user['idToken'])
	# db = firebase.database()
	# data = {"ItemName":item , "Period":exp_per}
	cancommit = push_into_expdetails(itemname=item , period = exp_per)
	if not cancommit:
		context = {"updated":False}
	else:
		context = {"updated":True}
	context.update(csrf(request))

	#db.push(data,user['idToken'])	
	return render(request , "home.html" , context)
	

# Create your views here.
def home(request):
	c = {}
	c = {"updated":False}
	c.update(csrf(request))
	return render(request,"home.html",c)

def about(request):

	return render(request,"about.html",{})

def ShowCurrentInventory(request):
	global itemList
	global refresh
	global moh
	
	print(moh)
	image_capture.putimage(1)
	if moh == None:
		print("loading model....")
		moh = model.ModelOfHell()
	else:
		print("model loaded already..")

	start_time = time.clock()
	newTable = moh.apna_model()
	end_time = time.clock()
	print("took ",end_time-start_time," ms to predict")
	refreshRefrigeratorDetails(newTable)
	refresh+=1
	oldsnap = fetchdetails(source = "old")
	newsnap = fetchdetails(source = "new")
	context = {}
	context.update(csrf(request))
	
	setA = set()
	setB = set()
	for items in oldsnap.keys():
		setA.add(items)
	for items in newsnap.keys():
		setB.add(items)
	newlyaddedItems = setB - setA
	#print(newlyaddedItems)
	removedItems = setA - setB

	for items in newlyaddedItems:
		itemList.append(str(newsnap[items]['quantity'])+" "+items+" were placed in the refrigerator ")

	for items in removedItems:
		itemList.append("You are out of "+items+" now")
 

	for key in oldsnap.keys():
		if key not in removedItems:

			if oldsnap[key]['quantity']<newsnap[key]['quantity']:
				itemList.append(str(abs(oldsnap[key]['quantity']-newsnap[key]['quantity']))+' '+key+'(s) were placed in.')
			elif oldsnap[key]['quantity']>newsnap[key]['quantity']:
				itemList.append(str(abs(oldsnap[key]['quantity']-newsnap[key]['quantity']))+' '+key+'(s) were taken out.')
			if newsnap[key]['isrotten']:
				itemList.append(key+' are rotten. Please throw them in dustbin')
	#print(itemList)
	context['details'] = list(set(itemList))
	context['table'] = newsnap
	#t.show_toast('Smart Refrigerator' , "\n".join(itemList) , duration = 5)
	return render(request , 'details.html' , context)

def refreshRefrigeratorDetails(newTable):
	# assuming that newTable is a list of tuples/lists in this form::
	# 		[('banana' , 5 , 0) , ('pinapple' , 1 , 1)]

	cur.execute("truncate table oldsnap")
	cur.execute("insert into oldsnap select * from newsnap")
	cur.execute("truncate table newsnap")
	for key , value in newTable.items():
		cur.execute("insert into newsnap values('"+key+"' , '"+str(value)+"' , '"+str(0)+"')")
	conn.commit()
	#(random.randint()%2)






def fetchdetails(source = None):
	if source =="old":
		records = cur.execute("select * from oldsnap")
	elif source=="new":
		records = cur.execute("select * from newsnap")
	records = records.fetchall()
	returnable = dict()
	for record in records:
		returnable[record[0]] = {'quantity':record[1] , 'isrotten':(True if record[2]==1 else False)}
	#print(returnable)
	return returnable


def push_into_expdetails(itemname=None,period=None):
	try:
		cur.execute("insert into expdetails values('"+itemname+"','"+period+"')")
		conn.commit()
		return True
	except:
		return False