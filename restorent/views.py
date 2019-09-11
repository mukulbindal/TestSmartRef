from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.template.context_processors import csrf
import pyrebase
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
config = {
    "apiKey": "AIzaSyBlMhHgbuXBXtWGblBOJB09_vRet0-LNPE",
    "authDomain": "testpyrebase-f56e0.firebaseapp.com",
    "databaseURL": "https://testpyrebase-f56e0.firebaseio.com",
    "projectId": "testpyrebase-f56e0",
    "storageBucket": "testpyrebase-f56e0.appspot.com",
    "messagingSenderId": "774109652893",
    "appId": "1:774109652893:web:e7f87682de5c63a0"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
moh = None
itemList = []
refresh = 0
def is_logged_in(request):
	return False if request.session['current_user']==None else True
def login(request):
	if is_logged_in(request):
		context = {'message':['already logged in !!']}
		return render(request,"home.html" , context)
	context = {}
	context.update(csrf(request))
	return render(request,"login.html" , context)
def signup(request):
	context = {}
	context.update(csrf(request))
	if is_logged_in(request):
		context = {'message':['already logged in !!']}
		return render(request,"home.html" , context)
	return render(request , "signup.html" , context)
def postsignup(request):
	last_user_id = max(db.child("users").shallow().get().val())
	id_deep = last_user_id.split("-")
	id_deep[1] = "%03d"%(int(id_deep[1])+1)
	new_user_id = "-".join(id_deep).upper()
	pin = request.POST.get("password").__hash__()
	email = request.POST.get("email")
	Refrigerator_id = request.POST.get("refid")
	print(Refrigerator_id)
	data = {
		'pin':pin,
		'Refrigerator_id': Refrigerator_id,
		'email' : email 
	}
	ip = {
		'ip':'set-ip-here'
	}
	db.child("users").child(new_user_id).set(data)
	db.child('ref-id-ip').child(Refrigerator_id).set(ip)
	context = {
	"message":["signed up successfully!","Your userid is "+new_user_id+" Kindly remember it for next login."]
	}
	context.update(csrf(request))
	return render(request,"login.html" , context)
def postlogin(request):
	context = {}
	context.update(csrf(request))
	userid = request.POST.get('userid')
	pin = request.POST.get('password').__hash__()
	try:
		real_pin = db.child('users').child(userid.upper()).get().val()['pin']
	except:
		context['message']=['invalid username']
		return render(request,"login.html" , context)
	if pin!=real_pin:
		context['message']=['invalid username or pin']
		return render(request,"login.html" , context)
	request.session['current_user'] = userid
	return render(request,"home.html" , context)

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
	
def logout(request):
	request.session['current_user'] = None
	context = {
	"message":["Good Bye! Logged out successfully!"]
	}
	context.update(csrf(request))
	return render(request,"login.html" , context)
# Create your views here.
def create_user_in_session(request):
	if 'current_user' not in request.session.keys():
		request.session['current_user'] = None
	return request
def home(request):
	request = create_user_in_session(request)
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