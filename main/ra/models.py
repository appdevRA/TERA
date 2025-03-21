from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import BookmarkQuerySet, GroupQuerySet

class Department (models.Model):
	abbv = models.CharField(max_length=50, null = False, blank= False, default='')
	name = models.CharField(max_length=200, null = False, blank= False)
	class Meta:
		db_table = "Department"

class User (AbstractUser):
	department= models.ForeignKey(Department, null = True, blank = True, on_delete = models.CASCADE)

	REQUIRED_FIELDS = ['first_name', 'last_name','department','password']
	
	def __str__(self) -> str:
		return f"{self.id} / {self.username}"

	class Meta:
		db_table = "User"


class Admin (models.Model):
	user = models.ForeignKey(User, null = False, blank = False, on_delete = models.CASCADE)
	class Meta:
		db_table = "Admin"


class Folder(models.Model):
	name = models.CharField(max_length=25)
	user = models.ForeignKey(User, null = False, blank = False, on_delete = models.CASCADE, default=None)
	date_created = models.DateTimeField(default=timezone.now)
	is_removed = models.IntegerField(default=0)

	class Meta:
		db_table = "Folder"	

class Bookmark_detail (models.Model):
	websiteTitle = models.CharField(max_length = 1000, null = False)
	itemType = models.CharField(max_length = 50,null=False)
	url = models.CharField(max_length = 2000,null=False)
	title = models.CharField(max_length = 1000,null=False)
	subtitle = models.CharField(max_length = 1000,null=True)
	author =  models.CharField(max_length = 1000,blank= True)
	description =  models.CharField(max_length = 1000,blank= True)
	journalItBelongs = models.CharField(max_length = 1000,blank= True)
	volume = models.CharField( max_length = 50, blank= True )
	numOfCitation = models.CharField(max_length = 1000,blank= True)
	numOfDownload = models.CharField(max_length = 1000,blank= True)
	numOfPages = models.CharField(max_length = 1000,blank= True)
	edition =models.CharField(max_length = 20,blank= True)
	publisher = models.CharField(max_length = 1000)
	publicationYear = models.CharField(max_length= 20)
	DOI = models.CharField(max_length = 200,blank= True)	
	ISSN = models.CharField(max_length = 100,blank= True)


	class Meta:
		db_table = "Bookmark_detail"



class Group(models.Model):
	name = models.CharField(max_length=50, null = False, blank = False) #add not null and not blank here
	owner = models.ForeignKey(User, related_name='User', on_delete = models.CASCADE)
	date_created = models.DateTimeField(auto_now_add= True)
	is_removed = models.IntegerField(default=0)
	member = models.ManyToManyField(User)
	
	objects = GroupQuerySet.as_manager()
	
	class Meta:
		db_table = "Group"

	def get_members(self):
		member_list = self.member.all().values("first_name","last_name")

		return member_list

		

class Bookmark(models.Model):
	user = models.ForeignKey(User, null = True, blank = True, on_delete = models.CASCADE)
	owner = models.ForeignKey(User,null = True, blank = True, related_name='owner', on_delete = models.CASCADE)
	group = models.ForeignKey(Group, null = True, blank = True, on_delete = models.CASCADE)
	bookmark = models.ForeignKey(Bookmark_detail, null = False, blank = False, on_delete = models.CASCADE) #add related_name="bookmarks", before null
	isFavorite = models.BooleanField(default=False)
	dateAccessed = models.DateTimeField(default = timezone.now)
	dateAdded = models.DateTimeField(auto_now_add = True )
	isRemoved = models.IntegerField(default = 0)	
	date_removed = models.DateTimeField(null = True)
	keyword= models.CharField(max_length = 200,blank= False, null=False, default="")
	folders = models.ManyToManyField(Folder, blank=True)

	class Meta:
		db_table = "Bookmark"

	objects = BookmarkQuerySet.as_manager()

	def archive(self):
		self.isRemoved = 1
		self.date_removed = timezone.now()
		self.save()
		return self

	def unarchive(self):
		self.isRemoved = 0
		self.date_removed = None
		self.save()
		return self

	def delete(self):
		self.isRemoved = 2
		self.date_removed = timezone.now()
		self.save()
		return self

class Dissertation(models.Model):
	title = models.CharField(max_length=1000, null = False, blank = False)
	abstract = models.CharField(max_length=2000, null = False, blank = False)
	author = models.CharField(max_length=200, null = False, blank = False)
	date_published = models.DateTimeField(auto_now_add = True )
	num_of_access = models.IntegerField(default = 0)
	is_active = models.BooleanField(default = False)
	department = models.ForeignKey(Department, null = False, blank = False, on_delete = models.CASCADE) #edit null to False
	file = models.FileField(
		upload_to ='dissertation/', 
		blank = False, 
		null = False, 
		default = 'setting.MEDIA_ROOT/teralogo.png'
		)

	
	class Meta:
		db_table = "Dissertation"

# class Dissertation_authors(models.Model):
# 	first_name = models.CharField(max_length=50)
# 	last_name = models.CharField(max_length=30)

# 	class Meta:
# 		db_table = "Dissertation_authors"





# class Group_bookmark(models.Model):
# 	group =models.ForeignKey(User_group, null = False, blank = False, on_delete = models.CASCADE)
# 	bookmark = models.ForeignKey(Bookmark_detail, null = False, blank = False, on_delete = models.CASCADE)
# 	added_by = models.ForeignKey(User, null = False, blank = False, on_delete = models.CASCADE)
# 	date_added = models.DateTimeField(default=timezone.now)
# 	is_removed = models.IntegerField(default=0)
# 	date_removed = models.DateTimeField(blank=True,null = True)

# 	class Meta:
# 		db_table = "Group_bookmark"



class Site (models.Model):
	name = models.CharField(max_length= 100)
	url= models.CharField(max_length= 300)
	is_active = models.BooleanField(default=False)

	class Meta:
		db_table = "Site"	


class UserSite_access(models.Model):
	user = models.ForeignKey(User, null = True, blank = True, on_delete = models.CASCADE)
	site = models.ForeignKey(Site, null = False, blank = False, on_delete = models.CASCADE)
	date_of_access = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "UserSite_access"	

class User_login(models.Model):
	user = models.ForeignKey(User, null = False, blank = False, on_delete = models.CASCADE)
	date = models.DateTimeField(default=timezone.now)
	# department = models.ForeignKey(Department, null = True, blank = False, on_delete = models.CASCADE) #change null to True
	class Meta:
		db_table = "User_login"	


# class Site_exception(models.Model):
# 	description = models.CharField(max_length= 100)
# 	filename = models.CharField(max_length= 100)
# 	line_number = models.CharField(max_length= 100)
# 	site = models.CharField(max_length= 100)
# 	date = models.DateTimeField(auto_now_add=True)
# 	search_keyword = models.CharField(max_length= 400) 
# 	link = models.CharField(max_length = 2000)
# 	class Meta:
# 		db_table = "Site_exception"	


# class Practice (models.Model):
# 	text =  models.CharField(max_length = 5)
# 	time = models.DateTimeField(default=timezone.now)


# 	class Meta:
# 		db_table = "Practice"



# class Proxies (models.Model):
# 	proxy = models.CharField(max_length = 100)
# 	isUsed = models.BooleanField(default = False)

# 	class Meta:
# 		db_table = "Proxies"
