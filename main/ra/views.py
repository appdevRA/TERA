from django.http import Http404
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.utils import timezone
from .forms import *
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core import serializers
from django.db import connection
from django.db.models import Q, Count, Max
from datetime import datetime
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core import serializers as s
from . import serializers
from .links import *
from .models import *
import ast
import json
from bs4 import BeautifulSoup
from .links import *
import requests
import csv
import io
from django.db.models import DateTimeField, ExpressionWrapper, F, Count, Case, When, Value, CharField, IntegerField, Func
import sys
from datetime import timedelta
import re
from django.core.paginator import Paginator
from django.db.models.functions import Concat
import calendar

class adminSiteView(View):
	def get(self, request):
		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")

		sites = Site.objects.all().values()
		return render(request, 'adminSite.html', {"sites": list(sites)})

	def post(self, request):
		if request.is_ajax():
			action = request.POST["action"]

			if action == "activate":
				Site.objects.filter(id = request.POST["siteID"]).update(is_active = True)
			elif action == "deactivate":
				Site.objects.filter(id = request.POST["siteID"]).update(is_active = False)

			return HttpResponse("")

class adminChartView(View):
	def get(self, request):
		return render(request, 'adminCharts.html')


class adminIndexView(View):
	def get(self, request):
		
		
		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")

		if datetime.today().month <10:
			todaysMonth = str(datetime.today().year) +"-0" + str(datetime.today().month)
		else:
			todaysMonth = str(datetime.today().year) +"-" + str(datetime.today().month)


		user= User.objects.select_related("department").filter(is_staff= False).values("username", "first_name", "last_name", "last_login", "department__name")

		activeUser= User_login.objects.filter(date__contains=todaysMonth, user__is_staff= False).annotate(day=ExpressionWrapper(
            																							Func(F('date'), 
            																								Value('%Y-%m-%d'), 
            																								function='DATE_FORMAT'
            																								), 
            																							output_field=CharField()
        																								)
																					).values('day').annotate(count=Count('id')).order_by("day")
		try:
			activeUserMax = activeUser.latest("count")["count"]
		except:
			activeUserMax = 0

		siteAccess= UserSite_access.objects.filter(date_of_access__contains=todaysMonth, user__is_staff = False).annotate(day=ExpressionWrapper(
            																							Func(F('date_of_access'), 
            																								Value('%Y-%m-%d'), 
            																								function='DATE_FORMAT'
            																								), 
            																							output_field=CharField()
        																								)
																								).values('day').annotate(count=Count('id')).order_by("day")
		try:
			siteAccessMax = siteAccess.latest("count")["count"]
		except:
			siteAccessMax = 0
			
		colleges= User_login.objects.select_related("user__department").filter(date__contains=todaysMonth, user__is_staff= False).values('user__department__abbv').annotate(count=Count('id')).order_by("user__department__abbv")
		# for item in user:
		# 		item["last_login"] = item["day"].strftime("%Y-%m-%d")

		context ={
			"users": list(user), 
			"activeUser": list(activeUser),
			"activeUserMax": activeUserMax,
			"siteAccess": list(siteAccess),
			"siteAccessMax": siteAccessMax,
			"colleges": list(colleges)	

		}

		return render(request,'adminIndex.html',context)



class adminActiveUserView(View):
	def get(self, request):

		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")


		if datetime.today().month <10:
			todaysMonth = str(datetime.today().year) +"-0" + str(datetime.today().month)
		else:
			todaysMonth = str(datetime.today().year) +"-" + str(datetime.today().month)


		queryset= User_login.objects.filter(date__contains=todaysMonth, user__is_staff= False).annotate(day=ExpressionWrapper(
            																							Func(F('date'), 
            																								Value('%Y-%m-%d'), 
            																								function='DATE_FORMAT'
            																								), 
            																							output_field=CharField()
        																								)
																					).values('day').annotate(count=Count('id')).order_by("day")
		try:
			maxCount = queryset.latest("count")["count"]
		except:
			maxCount = 0


		tableData= User.objects.select_related("department").filter(user_login__date__contains=todaysMonth, is_staff= False).annotate(
										visitCount=Count('user_login')
										).values("username", "last_name", "department__name", "first_name", "visitCount").order_by("-visitCount")
	

		context ={
			"tableData": list(tableData),
			"data": list(queryset),
			"maxCount": maxCount
		}
		return render(request, 'adminActiveUser.html', context)
	def post(self, request):

		if request.is_ajax():
			startDate = request.POST["startDate"]
			endDate = request.POST["endDate"]
			# start_dt = datetime(int(startDate.split("-")[0]), int(startDate.split("-")[1]), int(startDate.split("-")[2]))
			# end_dt = datetime(int(endDate.split("-")[0]), int(endDate.split("-")[1]), int(endDate.split("-")[2]))
			queryset= User_login.objects.filter(date__range= [startDate, endDate], user__is_staff= False).annotate(day=ExpressionWrapper(
        																							Func(F('date'), 
        																								Value('%Y-%m-%d'), 
        																								function='DATE_FORMAT'
        																								), 
        																							output_field=CharField()
    																								)
																				).values('day').annotate(count=Count('id')).order_by("day")
 
			
			try:	
				maxCount = queryset.latest("count")["count"]
			except:
				maxCount = 0

			tableData= User.objects.select_related("department").filter(user_login__date__range= [startDate, endDate], is_staff= False).annotate(
										visitCount=Count('user_login')
										).values("username","last_name", "department__name", "first_name", "visitCount").order_by("-visitCount")

			context ={
				"tableData": list(tableData),
				"data": list(queryset),
				"maxCount": maxCount
			}
			return JsonResponse(context)



class adminCollegesView(View):
	def get(self, request):

		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")


		if datetime.today().month <10:
			todaysMonth = str(datetime.today().year) +"-0" + str(datetime.today().month)
		else:
			todaysMonth = str(datetime.today().year) +"-" + str(datetime.today().month)

		queryset = list(Department.objects.values("abbv").annotate(count= Count("user__user_login", filter= Q(user__user_login__date__contains=todaysMonth))))
		tableData = list(Department.objects.annotate(registeredUser = Count("user__id", filter= ~Q(user__last_login = None) & Q(user__is_staff = False))).annotate(activeUser= Count("user", filter= Q(user__user_login__date__contains=todaysMonth) )).values("abbv", "registeredUser", "activeUser")  )
		
		siteVisit = UserSite_access.objects.select_related("user__department").filter(date_of_access__contains=todaysMonth, user__is_staff = False).values("user__department__abbv").annotate(count = Count("id"))
		
		for a in tableData:
			for innerloopIndex,b in enumerate(list(siteVisit)):
				if a["abbv"] == b["user__department__abbv"]:
					a["siteVisit"] = b["count"]
					break

				if innerloopIndex == len(list(siteVisit)) - 1:
					a["siteVisit"] = 0

		context ={
			"siteVisits": siteVisit,
			"tableData": list(tableData),
			"data": list(queryset)
		}
		return render(request, 'adminColleges.html', context)

	def post(self, request):
		if request.is_ajax():
			startDate = request.POST["startDate"]
			endDate = request.POST["endDate"]
			

			queryset = list(Department.objects.values("abbv").annotate(count= Count("user__user_login", filter= Q(user__user_login__date__range=[startDate, endDate]))))

			tableData = list(Department.objects.values("abbv").annotate(registeredUser = Count("user")).annotate(activeUser= Count("user", filter= Q(user__user_login__date__range=[startDate, endDate]) ))  )
			siteVisit = UserSite_access.objects.select_related("user__department").filter(date_of_access__range=[startDate, endDate], user__is_staff = False).values("user__department__abbv").annotate(count = Count("id"))
			
			for a in tableData:
				if len(list(siteVisit)) == 0:
					a["siteVisit"] = 0

				for innerloopIndex,b in enumerate(list(siteVisit)):
					if a["abbv"] == b["user__department__abbv"]:
						a["siteVisit"] = b["count"]
						break

					if innerloopIndex == len(list(siteVisit)) - 1:
						a["siteVisit"] = 0


			context ={
				"siteVisits": list(siteVisit),
				"tableData": list(tableData),
				"data": list(queryset)
			}
			return JsonResponse(context)

class adminSiteAccessView(View):
	def get(self, request):

		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")


		if datetime.today().month <10:
			todaysMonth = str(datetime.today().year) +"-0" + str(datetime.today().month)
		else:
			todaysMonth = str(datetime.today().year) +"-" + str(datetime.today().month)

		queryset= UserSite_access.objects.filter(
												date_of_access__contains=todaysMonth
												, user__is_staff = False).annotate(day=ExpressionWrapper(
																				Func(F('date_of_access'), 
																					Value('%Y-%m-%d'), 
																					function='DATE_FORMAT'
																					), 
																				output_field=CharField()
																				)
															).values('day').annotate(count=Count('id')).order_by("day")
		
		try:
			maxCount = queryset.latest("count")["count"]
		except:
			maxCount = 0

		tableData= Site.objects.all().annotate(
										visitCount=Count('id', filter=Q(usersite_access__date_of_access__contains=todaysMonth))
										).values().order_by("-visitCount")

		
		context ={
			"tableData": list(tableData),
			"data": list(queryset),
			"maxCount": maxCount
		}
		return render(request, 'adminSiteAccess.html', context)

	def post(self, request):
		if request.is_ajax():
			startDate = request.POST["startDate"]
			endDate = request.POST["endDate"]


			queryset= UserSite_access.objects.filter(
													date_of_access__range=[startDate, endDate]
													, user__is_staff = False).annotate(day=ExpressionWrapper(
																					Func(F('date_of_access'), 
																						Value('%Y-%m-%d'), 
																						function='DATE_FORMAT'
																						), 
																					output_field=CharField()
																					)
																).values('day').annotate(
																						count=Count('id')
																						).order_by("day")
				
			try:
				maxCount = queryset.latest("count")["count"]
			except:
				queryset = []
				maxCount = 0

			tableData= Site.objects.all().annotate(
										visitCount=Count('id', filter=Q(usersite_access__date_of_access__range=[startDate, endDate]))
										).values().order_by("-visitCount")

			
			context ={
				"tableData": list(tableData),
				"data": list(queryset),
				"maxCount": maxCount
			}
			return JsonResponse(context)



class adminDissertationsAccessView(View):
	def get(self, request):
		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")
				
		queryset = Dissertation.objects.select_related("department").annotate(department_name= F('department__abbv')).order_by("num_of_access")

		
				
		context ={
			"dissertations": queryset
		}
		return render(request, 'dissertationAccess.html', context)

	def post(self, request):

		if request.is_ajax():
			if request.POST.get("action") == "add":

				title = request.POST.get("title") 
				
				authors = request.POST.get("authors") 
				abstract = request.POST.get("abstract") 
				department = request.POST.get("college") 
				file = request.FILES.get('file')


				if Dissertation.objects.filter(title= title).exists():
					return JsonResponse({"didError": 1, "message": "Title already exist"})


				print(authors, abstract, file)
				if file == None or len(authors) == 0 or len(abstract) == 0:
					return JsonResponse({"didError": 1, "message": "Some Fields are missing"})


				createdObject = Dissertation.objects.create(title = title, author = authors, abstract = abstract, file = file, department = Department.objects.get(abbv = department), is_active = True)
				
				queryset = list(Dissertation.objects.filter(id = createdObject.id).select_related("department").annotate(department_name= F('department__abbv')).values())
				# json = s.serialize('python', [queryset], ensure_ascii=False)
				queryset[0]['file'] = "http://"+ request.get_host()+"/images/"+queryset[0]['file']
				context = {
					"didError": 0,
					"createdObject": queryset
				}
				return JsonResponse(context)



			elif request.POST.get("action") == "delete":
				ID = request.POST.get("id")
				Dissertation.objects.filter(id=ID).delete()
				return HttpResponse("")




			elif request.POST.get("action") == "get_row":
				ID = request.POST.get("id") 
				queryset = list(Dissertation.objects.filter(id = ID).select_related("department").values("title", "author", "abstract").annotate(department_name= F('department__abbv')))
				context = {
					"didError": 0,
					"object": queryset
				}
				return JsonResponse(context)




			elif request.POST.get("action") == "submit_edit":
				ID = request.POST.get("id") 
				oldTitle = request.POST.get("oldTitle") 
				title = request.POST.get("title") 
				
				authors = request.POST.get("authors") 
				abstract = request.POST.get("abstract") 
				department = request.POST.get("college") 
				file = request.FILES.get('file')
				
				if oldTitle != title and Dissertation.objects.filter(title= title).exists():
					return JsonResponse({"didError": 1, "message": "Title already exist"})

				if len(authors) == 0 or len(abstract) == 0:
					return JsonResponse({"didError": 1, "message": "Some Fields are missing"})

				if file == None:
					Dissertation.objects.filter(id = ID).update(title = title, author = authors, abstract = abstract, department = Department.objects.get(abbv = department))
				else:
					a = Dissertation.objects.get(id = ID)
					a. title = title
					a. author = authors
					a.abstract = abstract
					a.department = Department.objects.get(abbv = department)
					a.file = file
					a.save()
				queryset = list(Dissertation.objects.filter(id = ID).select_related("department").annotate(department_name= F('department__abbv')).values())
				
				queryset[0]['file'] = "http://"+ request.get_host()+"/images/"+queryset[0]['file']
				context = {
					"didError": 0,
					"createdObject": queryset
				}
				return JsonResponse(context)


			elif request.POST.get("action") == "activate":
				ID = request.POST.get("id").replace("switch","")
				print(ID)
				Dissertation.objects.filter(id = ID).update(is_active = True)
				return HttpResponse("")



			elif request.POST.get("action") == "deactivate":
				ID = request.POST.get("id").replace("switch","")
				print(ID)
				Dissertation.objects.filter(id = ID).update(is_active = False)
				return HttpResponse("")



class adminUserUpdateView(View):
	def get(self, request):
		return render(request, 'adminUserUpdate.html')

	def post(self, request):
		print("post")

		if 'back_to_tables' in request.POST:
			return redirect("ra:admin_tables_view"  )

class adminTableView(View):

	def get(self, request):

		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")

				
		user= User.objects.select_related("department").filter(is_staff= False).values("username", "first_name", "last_name", 
																"last_login", "department__name",
																"department__abbv", "last_login"
																)


		activeUser_perCollege =  Department.objects.values('name').annotate(activeCount=Count('id', filter=Q(user__last_login__contains=timezone.now().date())))
		userSite =  Site.objects.values('name', 'url').annotate(accessCount=Count('usersite_access__id')).distinct()
		dissertations = Dissertation.objects.select_related("department").annotate(department_name = F('department__abbv'))
		context ={
			"users": list(user),
			"activeUser_perCollege": list(activeUser_perCollege),
			"siteAccess": list(userSite),
			"dissertations": list(dissertations)		
		}
		return render(request, 'adminTables.html', context)
	def post(self, request):
		
		if 'update' in request.POST:
			form =UpdateUserForm(request.POST)
			
			if form.is_valid():
				username = request.POST['username']
				firstname = request.POST['first_name']	
				lastname = request.POST['last_name']	
				college = request.POST['college']
				password = request.POST['password']

				

			else:
				messages.success(request, form.errors)
				return redirect("ra:admin_tables_view")
				context = {
					"form": form
				}
				return render(request, 'adminTables.html', context)

		elif request.is_ajax():
			
			action = request.POST["action"]

			if action == "delete_user":
				User.objects.filter(username = request.POST['username']).delete()
				return HttpResponse("")

			elif action =="update_user":
				
				firstname = request.POST["first_name"]
				lastname = request.POST["last_name"]
				oldUsername = request.POST["oldUsername"]
				newUsername = request.POST["newUsername"]
				department = request.POST["department"]
				password = request.POST["password"]
 				
				
				if newUsername == "" or firstname == "" or lastname == "":
					return JsonResponse({"isError": 1,"errorMessage": "please fill out required fields"})
				
			
				elif oldUsername != newUsername:
					NewUsername_exist =  User.objects.filter(username = newUsername).exists()
					if NewUsername_exist:
						return JsonResponse({"isError": 1,"errorMessage": "username already exist"})
					else:
						if password == "":

							User.objects.filter(username=oldUsername).update(username= newUsername, 
																			first_name = firstname, 
																			last_name = lastname, 
																			department= Department.objects.get(abbv=department))
						else:
							User.objects.filter(username=oldUsername).update(username= newUsername, 
																			first_name = firstname, 
																			last_name = lastname, 
																			department= Department.objects.get(abbv=department),
																			password = make_password(password))


						user= User.objects.select_related("department").filter(username=newUsername).values(
																											"username", "first_name", "last_name", 
																											"last_login", "department__name",
																											"department__abbv", "last_login"
																											)
						context = {
						"isError": 0,
						"user": list(user)

						}
						print("success")
						return JsonResponse(context)
				else:
					if password == "":
						User.objects.filter(username=newUsername).update( 
																			first_name = firstname, 
																			last_name = lastname, 
																			department= Department.objects.get(abbv=department)
																		)
					else:
						User.objects.filter(username=newUsername).update( 
																			first_name = firstname, 
																			last_name = lastname, 
																			department= Department.objects.get(abbv=department),
																			password= make_password(password)
																		)
					user= User.objects.select_related("department").filter(username=newUsername).values(
																											"username", "first_name", "last_name", 
																											"last_login", "department__name",
																											"department__abbv", "last_login"
																										)

				


					context = {
						"isError": 0,
						"user": list(user)

					}
					print("success")
					return JsonResponse(context)
				
			# elif not user.exists() and  User.objects.filter(username=username).exists():
			# 	return JsonResponse({"isError": 1,"errorMessage": "username already exist"})

			# elif not user.exists() and  User.objects.filter(student_id=newStudent_id).exists():
			# 	return JsonResponse({"isError": 1,"errorMessage": "id number already exist"})
						


class adminRegistrationView(View):
	def get(self, request, rtype):

		if not request.user.is_authenticated:
			return redirect("ra:tera_login_view")
		if not request.user.is_staff:
			try:
				return redirect("ra:"+ request.session.get("previousPage"))
			except:
				logout(request)
				return redirect("ra:tera_login_view")

				
		return render(request, 'adminRegistration.html',{"type": rtype})#, context)
	def post(self, request, rtype):
		

		if 'btnRegister' in request.POST: 
			form = CreateUserForm(request.POST)
			if form.is_valid():
				username=request.POST['username']
				password=request.POST['password']
				first_name=request.POST['first_name']
				last_name=request.POST['last_name']
				department=request.POST['department']
				user = User(
							username=username,
							password = make_password(password),
							first_name = first_name,
							last_name= last_name,
							department = Department.objects.get(abbv=department),
							last_login = None
							)
				user.save()
				messages.success(request, "User added")
				return redirect('ra:admin_registration_view',  rtype=rtype)
			else:
				return render(request, 'adminRegistration.html', {"form":form,"type": rtype})

		if request.is_ajax():

			if request.POST['action'] == "register_csv":
				users = json.loads(request.POST.get('users'))
				didExcept = 0
				errorRows=[]
				for row in users:
					user = User(
						username = row['username'], 
						password=make_password(row['password']),
						first_name= row['first_name'], 
						last_name=row['last_name'], 
						department =  Department.objects.get(abbv=row['department']),
						last_login = None
						)
					try:
						user.save()
					except Exception as e:
						didExcept +=1
						errorRows.append(row)

				context ={
					"didExcept": didExcept,
					"errorRows": errorRows,
					"usersCount": len(users)
				}
				return JsonResponse(context)

			


		# elif 'readCSV' in request.POST:

		try: #read csv form
			myfile = request.FILES['file']
			file = myfile.read().decode('utf-8')
			dict_reader = csv.DictReader(io.StringIO(file))
			users =  list(dict_reader)

			return render(request, 'adminRegistration.html', {"users":users, "type": rtype})
		except:
			messages.success(request, "please select a file first")
			return redirect('ra:admin_registration_view', rtype=rtype)

		



class practice(View):
	
	def get(self, request):
		a= Department.objects.create(name='College of Computer Studies', abbv='CCS')

		# User.objects.create(username='18-5126-269', password =make_password('12345'), first_name="yanni", last_name="mondejar", department=a)
		User.objects.create(username='admin', password =make_password('teraadmin2022'), first_name="admin1", last_name="admin1", department= None, is_staff = True)


		# User.objects.create(username='18-5126-270', password =make_password('12345'), first_name="jarry", last_name="emorecha", department=a)

		# User.objects.create(username='18-5126-271', password = make_password('12345'), first_name="ryan ", last_name="talatagod", department = a)
		

		Department.objects.create(name='College of Engineering and Architecture', abbv='CEA')
		Department.objects.create(name='College of Nursing and Allied Health Sciences', abbv='CNAHS')
		Department.objects.create(name='College of Management, Business Accountancy', abbv='CMBA')
		Department.objects.create(name='College of Arts, Sciences and Education', abbv='CASE')
		Department.objects.create(name='College of Criminal Justice', abbv='CCJ')


		Site.objects.create(name ="Springeropen", url="https://Springeropen.com", is_active = True)
		Site.objects.create(name ="UNESCO Digital Library", url="https://unesdoc.unesco.org/", is_active = True)
		Site.objects.create(name ="Open Textbook Library", url="https://open.umn.edu/opentextbooks/", is_active = True)
		Site.objects.create(name ="OER Commons", url="https://www.oercommons.org/", is_active = True)

		return render(request,'practice.html')#,context)

	def post(self, request):
		
		
		myfile = request.FILES['file']
		file = myfile.read().decode('utf-8')
		dict_reader = csv.DictReader(io.StringIO(file))
			
		return HttpResponse('practice post')
		
			
		
		


class TeraLoginUser(View): 

	def get(self,request):

		if( request.user.id != None):
			if request.user.is_staff == True:
				return redirect("ra:admin_index_view")
			else:
				try:
					return redirect("ra:" + request.session.get('previousPage'))
				except:
					request.session['previousPage'] = 'index_view'
					return redirect("ra:index_view")
		else:
			
			return render(request,'login.html')	
		
		

	def post(self, request):
		
	
		
		if 'buttonlogin' in request.POST:
			username = request.POST.get('username')
			password = request.POST.get('password')

			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				if not User_login.objects.filter(user = request.user,date__contains=timezone.now().date()).exists() and request.user.is_staff == False:
					User_login.objects.create(user = request.user)
				
				if request.user.is_staff == True:
					return redirect("ra:admin_index_view")

				else:
					if request.session.get('previousPage') == None:
						return redirect("ra:index_view")
					else:
						return redirect('ra:'+ request.session.get('previousPage'))
			else:
				messages.success(request, "Invalid Username or password")
				return redirect('ra:tera_login_view')
				
				
		
		
					
		
		 
			
class TeraIndexView(View):
	def get(self, request):

		
		if request.user.is_authenticated and not User_login.objects.filter(user = request.user, date__contains=timezone.now().date()).exists():
			User_login.objects.create(user= request.user)

		if request.user.is_authenticated and not User.objects.filter(id = request.user.id, last_login__contains=timezone.now().date()).exists():
			User.objects.filter(id= request.user.id).update(last_login = timezone.now())
		request.session['previousPage'] = 'index_view'
	
		context ={
			"user":request.user.is_authenticated
		}
		
	
		
		return render(request,'landingpage.html',context)

	def post(self, request):

		if 'buttonLogin' in request.POST:
			request.session['previousPage'] = request.POST['previousPage']
			return redirect('ra:tera_login_view')

		elif 'btnLogout' in request.POST:
			proxy = request.session.get('proxy')
			logout(request)

			return redirect("ra:index_view")

		elif 'btnSearch' in request.POST:
			request.session['word'] = request.POST.get("keyword")
			
			return redirect('ra:search_result_view')
		


class TeraSearchResultsView(View):
	def get(self,request):
		if request.user.is_authenticated and not User_login.objects.filter(user = request.user, date__contains=timezone.now().date()).exists():
			User_login.objects.create(user= request.user)
		if request.user.is_authenticated and not User.objects.filter(id = request.user.id, last_login__contains=timezone.now().date()).exists():
			User.objects.filter(id= request.user.id).update(last_login = timezone.now())

		if request.session.get('website') != None:
			active_site = request.session.get('website')
		else:
			active_site = "CIT"

		if request.session.get('itemType') != None:
			itemType = request.session.get('itemType')
		else:
			itemType = "Dissertations"
		
		request.session['previousPage'] ='search_result_view'
		word = request.session.get('word')


		sites = Site.objects.filter(is_active=True).values("name")
		context = {
							"host": request.get_host(),
							'keyword': word,
							'active_site': active_site,
							'itemType': itemType,
							"isGet": "true",
							'is_authenticated': str(request.user.is_authenticated),
							'sites': list(sites)
		}
		
		return render(request,'searchresults.html', context)

	def post(self, request):
		
		if request.method == 'POST' and request.is_ajax():
			action = request.POST['action']

			if action == "search":
				
				if request.POST['isPage'] == "false":
					word = request.POST['word']
					request.session['word'] = word
					isGet = request.POST['isGet']
					website = request.POST['site']
					isSite = request.POST['isSite']

					itemType = request.POST['itemType']
					request.session['website'] =website
					request.session['itemType'] = itemType 
					page = 1
				
				else:
					page = request.POST['pageNumber']
					word = request.session['word'] 
					website  = request.session['website']
					itemType  = request.session['itemType'] 
					isGet = request.POST['isGet']
					isSite = request.POST['isSite']

				if website == "CIT":
		
					disser = Dissertation.objects.filter(Q(title__iregex=r"[[:<:]]"+word+"[[:>:]]") | Q(author__iregex=r"[[:<:]]"+word+"[[:>:]]") | Q(department__name__iregex=r"[[:<:]]"+word+"[[:>:]]") | Q(department__abbv__iregex=r"[[:<:]]"+word+"[[:>:]]"), is_active= True).order_by("num_of_access").values()
					p = Paginator(disser,10)
					results = p.page(page)
					context = {
						'results': list(results),
						'is_authenticated': request.user.is_authenticated,
						'isGet': "false"
					}
				
				else:
					if isSite == "true" and isGet == "false":
						if request.user.is_authenticated and not UserSite_access.objects.filter(user=request.user, site = Site.objects.get(name=website.replace("_"," ")), date_of_access__contains =timezone.now().date()).exists():
							UserSite_access.objects.create(user=request.user, site = Site.objects.get(name=website.replace("_"," ")))
						
					results = scrape(word, itemType, website,' ', page)

				
					context = {
						'results': results,
						'is_authenticated': request.user.is_authenticated,
						'isGet': "false"
					}
				return JsonResponse(context)

			elif action == "add":
				keyword = request.POST['word']
				bookmark = request.POST['bookmark']
				website = request.POST['website']
				reftype = request.POST['reftype']
				string = bookmark.split('||')
				title = string[0]
				url = string[1]
				# return HttpResponse("")
				if not Bookmark.objects.filter(user = request.user, bookmark__url = url, isRemoved = 0).exists() and not Bookmark.objects.filter(user = request.user, bookmark__url = url, isRemoved = 1).exists():
					if Bookmark_detail.objects.filter(url = url).exists():
						Bookmark.objects.create(user = request.user,bookmark=Bookmark_detail.objects.get(url = url),keyword=keyword)
						print("diri")
						return HttpResponse("")

					else:
						
						detail = details(url, request.session.get('proxy'),website, reftype)
						itemType = detail['itemType']
						author = detail['author']
						description = detail['description'][0:995]
						journalItBelongs = detail['journalItBelongs']
						volume = detail['volume']
						doi = detail['doi']
						publicationYear = detail['publishYear']
						subtitle = detail['subtitle']
						citation = detail['citation']
						downloads = detail['downloads']
						publisher = detail['publisher']
						edition = detail['edition']
						pages = detail['pages']
						try:
							ISSN = detail['ISSN']
						except:
							ISSN = ""

						
						if reftype == "article" or reftype == "Programme_and_meeting_document":
							detail = Bookmark_detail.objects.create(
								title = title,websiteTitle= website.replace("_"," "),itemType= itemType,
								author = author, description= description, url = url, journalItBelongs= journalItBelongs, 
								volume = volume, DOI = doi,publicationYear = publicationYear
								)
							Bookmark.objects.create(user = request.user,bookmark=detail,keyword=keyword)

							

							
						elif itemType == "book":
							detail = Bookmark_detail.objects.create(title = title,websiteTitle= website.replace("_"," "),
								subtitle = subtitle, itemType= itemType,author = author,numOfCitation = citation,
								numOfDownload= downloads,publisher=publisher, description= description, url = url, 
								edition = edition,numOfPages = pages, DOI = doi)

							Bookmark.objects.create(user = request.user,bookmark=detail,keyword=keyword)

						elif itemType == "Text_book":
							detail = Bookmark_detail.objects.create(title = title,websiteTitle= website.replace("_"," "),
								itemType= "text book",author = author,
								 description= description, url = url, 
								publicationYear = publicationYear,ISSN = ISSN)

							Bookmark.objects.create(user = request.user,bookmark=detail,keyword=keyword)

						return HttpResponse("")
				else:
					return HttpResponse("")
				
			elif action == "increment_access":
				ID = request.POST["id"]
				instance = Dissertation.objects.get(id = ID)
				instance.num_of_access = F("num_of_access") + 1
				instance.save()
				return HttpResponse("")
			else:
				bookmark = request.POST['bookmark']
				string = bookmark.split('||')

				title = string[0].replace('\n','').replace('  ','')
				detail = Bookmark_detail.objects.get(title=title)
				Bookmark.objects.filter(user = request.user, bookmark=detail).delete()
				return HttpResponse('')



class TeraDashboardView(View):

	def get(self,request):

		if request.user.is_authenticated and request.user.is_staff == 0 and not User_login.objects.filter(user = request.user, date__contains=timezone.now().date()).exists():
			User_login.objects.create(user= request.user)
		if request.user.is_authenticated and request.user.is_staff == 0 and not User.objects.filter(id = request.user.id, last_login__contains=timezone.now().date()).exists():
			User.objects.filter(id= request.user.id).update(last_login = timezone.now())

		request.session['previousPage'] = "tera_dashboard_view"
	

		if request.user.is_authenticated:

			
			recommendation = []
			if Bookmark.objects.filter(user=request.user).exists():
				if Bookmark_detail.objects.filter(~Q(bookmark__user = request.user),bookmark__group__isnull=True).exists():
					recommendationQuery= Bookmark_detail.objects.select_related("bookmark").filter(bookmark__user__isnull=False,
																									bookmark__group__isnull=True, 
																									
																									).annotate(count=Count(Case(
																													        When(Q(bookmark__isRemoved=False) 
																													        	& Q(bookmark__group__isnull=True) 
																													        	& Q(bookmark__user__isnull=False), 
																													        	then=Value(1)),
																													    	))
																									).annotate(isOwn = Count(Case(
																													        When(Q(bookmark__user= request.user) & Q(bookmark__isRemoved= False), 
																													        then=Value(1)),
																													    	))
																									).annotate(isMyRemoved = Count(Case(
																										        When(Q(bookmark__user= request.user) & (Q(bookmark__isRemoved = 1) | Q(bookmark__isRemoved=2)), 
																										        then=Value(1)),
																										    	))
																									).order_by("-count").values("id",
																										"title", "url" ,"itemType",
																										"websiteTitle", 
																										 "isOwn", "count", "isMyRemoved")
					
					recommendation = modes(list(recommendationQuery), request.user.id)

			
			queryset = Bookmark.objects.select_related("bookmark").filter(
																		( Q(user=request.user) ) & 
																		( Q(isRemoved=1) | Q(isRemoved=0) ), 
																		group__isnull=True
																		).values(
																			"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																			"isRemoved", "date_removed",
																			"bookmark__websiteTitle", "bookmark__itemType",
																			"bookmark__url", "bookmark__title", "bookmark__subtitle",
																			
																				).distinct().order_by("dateAdded")
											



               
			folders =	Folder.objects.filter(user_id=request.user, is_removed = 0).values()
			groups= Group.objects.select_related("owner").filter((Q(owner= request.user) | Q(member=request.user)),
																			 is_removed=0).values(
																			 						"id","name", "date_created",
																			 						"owner__first_name",
																			 						"owner__last_name"
																			 						)
			a = json.dumps(list(queryset), default=str)
			folder_list = json.dumps(list(folders), default=str)
			group_list = json.dumps(list(groups), default=str)

			context = {
				"bookmark_list": a,
			    "folder_list": folder_list,
			    "group_list":group_list,
			    "recommendation": recommendation

			}
			return render(request,'collections.html', context)
		else:
			return redirect('ra:tera_login_view')


	def post(self, request):

		if request.method == 'POST' and request.is_ajax():
			action = request.POST['action']

			if action == 'addFav':
				tab = request.POST['tab']
				b_id = request.POST['b_id']

				if tab != "groups":
					Bookmark.objects.filter(id=b_id, user= request.user, group = None).update(isFavorite=True)
				else:
					Bookmark.objects.filter(group__id=request.POST['group_id'], id=b_id).update(isFavorite=True)
				return HttpResponse('')
			elif action == 'remFav':
				tab = request.POST['tab']
				b_id = request.POST['b_id']

				if tab != "groups":
					Bookmark.objects.filter(id=b_id, user= request.user, group = None).update(isFavorite=False)
				else:
					Bookmark.objects.filter(group__id=request.POST['group_id'], id=b_id).update(isFavorite=False)

				return HttpResponse('')


			elif action == 'trashItem':
				tab = request.POST['tab']
				bookmark_id = request.POST['b_id']

				if tab != "folders" and tab != "groups":
					Bookmark.objects.filter(id=bookmark_id, user= request.user, group = None).update(isRemoved=1, date_removed= timezone.now())
					return HttpResponse('')

				elif tab == "folders":
					faction_id = request.POST['faction_id']
					bookmark_id = request.POST['b_id']
					instance = Bookmark.objects.get(
											id=bookmark_id,
											user= request.user
											 )
					instance.folders.remove(Folder.objects.get(id = faction_id))
					return HttpResponse("")

				elif tab == "groups":
					faction_id = request.POST['faction_id']
					bookmark_id = request.POST['b_id']
					instance = Bookmark.objects.filter(
											group__id = faction_id,
											id = bookmark_id
											 ).update(isRemoved=1, date_removed= timezone.now())
					return HttpResponse("")


			elif action == 'unTrashItem':
				Bookmark.objects.filter(id=request.POST['bID'], user= request.user, group = None).update(isRemoved=0,date_removed= None)
				return HttpResponse('')


			elif action == 'deleteItem':
				Bookmark.objects.filter(id=request.POST['bID'], user= request.user, group = None).update(isRemoved=2, date_removed= timezone.now())
				return HttpResponse('')


			elif action == 'get_bookmarks':
				tab = request.POST['tab']

				if tab == "all":
					queryset = Bookmark.objects.select_related("bookmark_detail").filter(
																		user=request.user,
																		isRemoved=False, 
																		group__isnull=True
																		).values(
																			"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																			"isRemoved", "date_removed",
																			"bookmark__websiteTitle", "bookmark__itemType",
																			"bookmark__url", "bookmark__title"
																				).order_by("dateAdded")
					return JsonResponse({"bookmarks": list(queryset)})
				elif tab == "recentlyAdded":
					time = timezone.now().date() - timedelta(days=7)
					queryset = Bookmark.objects.select_related("bookmark_detail").filter(
																		user=request.user,
																		isRemoved=False, 
																		group__isnull=True,
																		dateAdded__gte=time
																		).values(
																			"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																			"isRemoved", "date_removed",
																			"bookmark__websiteTitle", "bookmark__itemType",
																			"bookmark__url", "bookmark__title"
																				).order_by("dateAdded")
					return JsonResponse({"bookmarks": list(queryset)})

				elif tab == "recentlyRead":
					time = timezone.now().date() - timedelta(days=3)
					queryset = Bookmark.objects.select_related("bookmark_detail").filter(
																		user=request.user,
																		isRemoved=False, 
																		group__isnull=True,
																		dateAccessed__gte=time
																		).values(
																			"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																			"isRemoved", "date_removed",
																			"bookmark__websiteTitle", "bookmark__itemType",
																			"bookmark__url", "bookmark__title"
																				).order_by("dateAdded")
					return JsonResponse({"bookmarks": list(queryset)})

				elif tab == "favorite":
					time = timezone.now().date() - timedelta(days=3)
					queryset = Bookmark.objects.select_related("bookmark_detail").filter(
																		user=request.user,
																		isRemoved=False, 
																		group__isnull=True,
																		isFavorite=True
																		).values(
																			"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																			"isRemoved", "date_removed",
																			"bookmark__websiteTitle", "bookmark__itemType",
																			"bookmark__url", "bookmark__title"
																				).order_by("dateAdded")
					return JsonResponse({"bookmarks": list(queryset)})

				elif tab == "trash":
					time = timezone.now().date() - timedelta(days=3)
					queryset = Bookmark.objects.select_related("bookmark_detail").filter(
																		user=request.user,
																		isRemoved=True, 
																		group__isnull=True,
																		).values(
																			"id", "bookmark__id", "isFavorite", "dateAccessed",  
																			"isRemoved", "date_removed",
																			"bookmark__websiteTitle", "bookmark__itemType",
																			"bookmark__url", "bookmark__title"
																				).order_by("dateAdded")
					return JsonResponse({"bookmarks": list(queryset)})

				elif tab =="folders":
					# return HttpResponse("")
					fID = request.POST['faction_id']
					a= []
					if Bookmark.objects.filter( folders__id=fID, user=request.user, isRemoved=0).exists():
						queryset = Bookmark.objects.select_related("bookmark").filter(
																				folders__id=fID, user=request.user, isRemoved=0
																				).values(
																					"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																					"isRemoved", "date_removed",
																					"bookmark__websiteTitle", "bookmark__itemType",
																					"bookmark__url", "bookmark__title"
																						)
						a = list(queryset)
					context = {
				    "bookmarks": a
					}
					
					return JsonResponse(context)


				elif tab =="groups":
					# return HttpResponse("")
					gID = request.POST['faction_id']
					a= []
					m= []
					if Bookmark.objects.filter(group__id = gID, isRemoved=0).exists():
						queryset = Bookmark.objects.select_related("bookmark").filter(
																				group__id=gID, isRemoved=0
																				).values(
																					"id", "bookmark__id", "isFavorite", "dateAccessed", "dateAdded", 
																					"isRemoved", "date_removed",
																					"bookmark__websiteTitle", "bookmark__itemType",
																					"bookmark__url", "bookmark__title"
																						)
						a = list(queryset)

					group =Group.objects.get(id=gID)
					members = group.get_members()
					m = list(members)
					context = {
				    "bookmarks": a,

				    "member": m
					}
					
					return JsonResponse(context)
					

			
			elif action == 'get_folders':
				folders =	Folder.objects.filter(user=request.user, is_removed = 0).values()
				return JsonResponse( { "list": list(folders) } )

			elif action == 'get_groups':
				groups= Group.objects.select_related("owner").filter((Q(owner= request.user) | Q(member=request.user)),
																				 is_removed=0).annotate(
																				 						 ownerName = Concat('owner__first_name',
																				 						 					Value(' '), 
																				 						 					'owner__last_name',
																				 						 					output_field=CharField()
																				 						 					)
																				 						 ).values(
																						 						"id","name", "date_created", "ownerName"
																						 						).distinct()
				
				return JsonResponse( { "list": list(groups) } )

			elif action == 'get_factions':
				folders =	Folder.objects.filter(user=request.user, is_removed = 0).values()
				groups= Group.objects.select_related("owner").filter((Q(owner= request.user) | Q(member=request.user)),
																				 is_removed=0).values(
																				 						"id","name", "date_created",
																				 						"owner__first_name",
																				 						"owner__last_name"
																				 						)
				return JsonResponse( { "folders": list(folders), "groups": list(groups) } )

			elif action == "get_detail":
				detailID = request.POST['detailID']

				queryset = Bookmark_detail.objects.filter(id = detailID).values(
																			
																			"websiteTitle", "itemType",
																			"url", "title", "subtitle",
																			"subtitle", "author", "description",
																			"journalItBelongs", "volume",
																			"numOfCitation", "numOfPages",
																			"publisher", "publicationYear",
																			"DOI", "ISSN", "edition", "numOfDownload"
																				)
				return JsonResponse( { "detail": list(queryset) } )

			elif action == 'add_bookmark_to_faction':
				factionID = request.POST['faction_id']
				bookmarkID = request.POST['b_id']
				faction = request.POST['faction']
				
				if faction =="folder":
					
					instance = Bookmark.objects.get(id = bookmarkID)
					instance.folders.add(Folder.objects.get(id= factionID))
					
					return HttpResponse('')

				elif faction =="groups":

					instance = Bookmark.objects.get(id=bookmarkID, isRemoved=0)
					
					# bookmark = User_bookmark.objects.get(id=bID)
					if Bookmark.objects.filter(group__id= factionID,bookmark=instance.bookmark, isRemoved=0).exists():
						return HttpResponse('')
					else:
						Bookmark.objects.create(
												group=Group.objects.get(id=factionID), 
												bookmark = instance.bookmark
												)
						# print("bookmark added to group")
						return HttpResponse('')
					
					

			

			elif action == 'add_folder':
				name = request.POST['name']
				
				
				if not Folder.objects.filter(user = request.user, name = name, is_removed=0).exists():
					folder = Folder.objects.create(user=request.user, name = name)
					folders = Folder.objects.filter(id=folder.id).values()

					context = {
				    "createdFolder": list(folders),
				    "did_exist": False
					}
				else:
					context = {
				    "did_exist": True
					}
				
				return JsonResponse(context)


			elif action == 'add_group':
				name = request.POST['name']

				if not Group.objects.filter(owner=request.user, name = name, is_removed=False).exists():
					group = Group.objects.create(owner=request.user, name = name)
					query_group= Group.objects.select_related("owner").filter(id = group.id,
																				 ).annotate(
																				 						 ownerName = Concat('owner__first_name',
																				 						 					Value(' '), 
																				 						 					'owner__last_name',
																				 						 					output_field=CharField()
																				 						 					)
																				 						 ).values(
																						 						"id","name", "date_created", "ownerName"
																						 						).distinct()
					
					

					context = {
				    "createdGroup": list(query_group),
				    "did_exist": False
					}
				else:
					context = {
				    "did_exist": True
					}

				return JsonResponse(context)

			

			
			
			


			elif action == 'open_link':
				bID = request.POST['bID']
				tab = request.POST['tab']
				faction_id = request.POST['faction_id']

				if tab == "groups":
					Bookmark.objects.filter(id= bID, group__id = faction_id).update(dateAccessed = timezone.now())
				else:
					Bookmark.objects.filter(id = bID, user=request.user, group = None).update(dateAccessed = timezone.now())
				return HttpResponse('')

			elif action == 'delete_faction':
				faction_type = request.POST['faction_type']


				if faction_type == 'folder':
					ID = request.POST['id']
					Folder.objects.filter(id = ID).update(is_removed = 1)
					return HttpResponse('')

				elif faction_type == 'groups':
					ID = request.POST['id']
					Group.objects.filter(id = ID).update(is_removed = 1)
					return HttpResponse('')

			elif action == 'add_member':
				username = request.POST['id']
				gID = request.POST['gID']

				if not User.objects.filter(username=username).exists():
					context={
					"result":"not exist"
					}
					return JsonResponse(context)

				elif Group.objects.filter(id = gID,member__username= username).exists():
					context={
					"result":"member"
					}
					return JsonResponse(context)

				elif Group.objects.filter(id = gID,owner__username= username).exists():
					context={
					"result":"owner"
					}
					return JsonResponse(context)

				

				elif User.objects.filter(username=username).exists():
					Group.objects.get(id=gID).member.add(User.objects.get(username=username))
					member= User.objects.filter(username=username).values("first_name", "last_name")
					context={
					"result":"added",
					"member": list(member)
					}
					return JsonResponse(context)

				

			elif action == "add_recommended":
				detailID = request.POST['detailID']
				a = Bookmark.objects.create(user= request.user, bookmark= Bookmark_detail.objects.get(id= detailID))
				addedBookmark = Bookmark.objects.select_related("bookmark").filter(
																					id=a.id
																					).values(
																						"id", "bookmark__id", 
																						"isFavorite", "dateAccessed", 
																						"dateAdded", "isRemoved",
																						"date_removed", "bookmark__websiteTitle", 
																						"bookmark__itemType", "bookmark__url", 
																						"bookmark__title"
																							)
				
				return JsonResponse({"addedBookmark":list(addedBookmark)})




def TeraLogoutView(request):
	if request.user.is_staff == True:
		logout(request)
		return redirect("ra:tera_login_view")							
	else:
		word = request.session.get('word')
		proxy = request.session.get('proxy')
		pp = request.session.get('previousPage')
		logout(request)
		request.session['previousPage'] = pp
		request.session['word'] = word
		request.session['proxy'] = proxy
		return redirect("ra:"+pp)							

def TeraAccountSettingsView(request):
	if request.method == 'POST':
		form = PasswordChangeForm(data=request.POST, user=request.user)
	    
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)  
			messages.success(request, 'Your password was successfully updated!' )
			return redirect('ra:tera_account_settings')
		else:

			messages.info(request, str(form.errors))
	else:

	    form = PasswordChangeForm(request.user)
	return render(request, 'accountsettings.html', {
	    'form': form})




class FolderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Folder.objects.all()
    serializer_class = serializers.FolderModelSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.FolderRetrieveModelSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = serializers.FolderQuerySerializer(data=self.request.query_params)

        if not serializer.is_valid():
            return queryset

        user = serializer.validated_data.get("user")
        if user:
            queryset = queryset.filter(user=user)

        return queryset.order_by("name")


class BookmarkViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Bookmark.objects.all()
    serializer_class = serializers.BookmarkModelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # return all rows of Bookmark if no query params
        if not len(self.request.query_params):
            return queryset

        serializer = serializers.BookmarkQuerySerializer(data=self.request.query_params)

        if not serializer.is_valid():
            return queryset

        user = serializer.validated_data.get("user")
        if user:
            queryset = queryset.user(user)

        recently_added = serializer.validated_data.get("recently_added")
        if recently_added:
            queryset = queryset.recently_added()

        recently_read = serializer.validated_data.get("recently_read")
        if recently_read:
            queryset = queryset.recently_read()

        favorite = serializer.validated_data.get("favorite")
        if favorite is not None:
            queryset = queryset.favorites(favorite)

        groups_only = serializer.validated_data.get("groups_only")
        if groups_only is not None:
            queryset = queryset.groups_only(groups_only)

        removed = serializer.validated_data.get("removed")
        queryset = queryset.removed() if removed else queryset.unarchived()

        group = serializer.validated_data.get("group")
        folder = serializer.validated_data.get("folder")
        if group or folder:
            queryset = queryset.group(group) if group else queryset.folder(folder)

        return queryset

    @action(methods=["POST"], detail=True, url_path="toggle-favorite")
    def toggle_favorite(self, *args, **kwargs):
        instance = self.get_object()

        instance.isFavorite = not instance.isFavorite
        instance.save()

        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True)
    def unarchive(self, *args, **kwargs):
        instance = self.get_object()
        instance.unarchive()
        return Response(status=status.HTTP_200_OK)


class UserViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()
    serializer_class = serializers.UserModelSerializer

    @action(
        methods=["POST"],
        detail=False,
        serializer_class=serializers.LoginRequestSerializer,
    )
    def login(self, *args, **kwargs):
        request_serializer = self.get_serializer(data=self.request.data)

        if not request_serializer.is_valid():
            return Response(request_serializer.errors, 400)

        username = request_serializer.validated_data.get("username")
        password = request_serializer.validated_data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response(serializers.UserModelSerializer(user).data)
        return Response("Incorrect username or password.", 401)

    @action(
        methods=["POST"],
        detail=True,
        url_path="change-password",
        serializer_class=serializers.ChangePasswordRequestSerializer,
    )
    def change_password(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        password = serializer.validated_data.get("password")

        user = self.get_object()
        user.set_password(password)
        user.save()

        return Response(status=200)


class GroupViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Group.objects.all()
    serializer_class = serializers.GroupModelSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        serializer = serializers.GroupQuerySerializer(data=self.request.query_params)
        if not serializer.is_valid():
            return queryset

        bookmark_id = serializer.validated_data.get("available_for_bookmark_detail")
        if bookmark_id:
            queryset = queryset.available_for_bookmark_detail(bookmark_id)

        user_id = serializer.validated_data.get("for_user")
        if user_id:
            queryset = queryset.for_user(user_id)

        return queryset.order_by("name")


class BookmarkDetailViewSet(viewsets.GenericViewSet):
    queryset = Bookmark_detail.objects.all()
    serializer_class = serializers.BookmarkDetailModelSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="add-to-group",
        serializer_class=serializers.AddToGroupRequestSerializer,
    )
    def add_to_group(self, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(data=self.request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, 400)

        Bookmark.objects.create(
            user_id=serializer.validated_data.get("user_id"),
            group=Group.objects.get(id=serializer.validated_data.get("group_id")),
            bookmark=Bookmark_detail.objects.get(id=instance.id),
        )

        return Response(status=200)
