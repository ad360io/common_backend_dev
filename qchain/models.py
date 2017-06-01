from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

class Agent(models.Model):
	"""
	Class for user profile. 
	A different class name may be more informative.
	"""
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	birthdate = models.DateField(null=True)

	def __str__(self):        
		return self.user.username


class Website(models.Model):
	"""
	Class for website.
	Each website is owned by a user but a user may have multiple websites.
	"""
	user = models.ForeignKey(User, on_delete=models.CASCADE) 
	link = models.URLField()
	name = models.CharField(max_length=20)
	description = models.CharField(max_length=200)
	# NOTE: USE CONSTANT VARIABLES TO REPRESENT TYPE STRINGS AS RECOMMENDED
	POLITICS = 'POLITI' 
	NONPOLITICS = 'NONPOL' 
	CATEGORY_CHOICES = (
		(POLITICS, 'Politics'),
		(NONPOLITICS, 'Not Politics'),
	)
	category = models.CharField(
		max_length=6,
		choices=CATEGORY_CHOICES)
	adcount = models.IntegerField(default=0) # NOTE: IT IS MUCH EASIER TO STORE COUNTS THAN COUNTING

	def __str__(self):           
		return self.name
		

class WebsiteForm(ModelForm):
	"""
	Form based on website model.
	User should be set separately in view using request.user.
	Adcount should also be modified in the backend rather than by user.
	"""
	class Meta:
		model = Website
		fields = ['link', 'name', 'description', 'category']

class Adspace(models.Model):
	"""
	Class for adspace.
	Adspace is the essential commodity and belongs to a website and its owner.
	"""
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	website = models.ForeignKey(Website, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	height = models.IntegerField()
	width = models.IntegerField()
	#start_time = models.DateTimeField(null=True, blank=True)
	#end_time = models.DateTimeField(null=True, blank=True)
	BANNER = 'BANNER'
	NONBANNER = 'NONBAN'
	ADTYPE_CHOICES = (
		(BANNER, 'Banner'),
		(NONBANNER, 'Not Banner'),
	)
	adtype = models.CharField(
		max_length=6,
		choices=ADTYPE_CHOICES)
	# HACK: SAVE STATS AS STRINGS THEN PARSE IN VIEW
	views = models.CharField(max_length=400, null=True, blank=True)
	clicks = models.CharField(max_length=400, null=True, blank=True)
	total_views = models.IntegerField(default=0) # used for filtering
	total_clicks = models.IntegerField(default=0)

	def __str__(self):             
		return self.name

class AdspaceForm(ModelForm):
	"""
	Form based on adspace model.
	User should be set separately in view using request.user.
	"""
	class Meta:
		model = Adspace
		exclude = ['user', 'views', 'clicks', 'total_views', 'total_clicks']

class Contract(models.Model):
	"""
	Class for contract.
	Some serious design thoughts are needed here.
	"""