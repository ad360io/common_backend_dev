from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

class Agent(models.Model):
	"""
	Class for agent. 
	An agent is both publisher and advertiser.
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
	stats1 = models.CharField(max_length=400, null=True, blank=True) # earnings time series
	stats2 = models.CharField(max_length=400, null=True, blank=True) # clicks time series
	stats3 = models.CharField(max_length=400, null=True, blank=True) # impressions time series
	stats4 = models.CharField(max_length=400, null=True, blank=True)
	stats5 = models.CharField(max_length=400, null=True, blank=True)
	stats6 = models.CharField(max_length=400, null=True, blank=True)
	stats7 = models.CharField(max_length=400, null=True, blank=True)
	stats8 = models.CharField(max_length=400, null=True, blank=True)
	stats9 = models.CharField(max_length=400, null=True, blank=True)
	stats10 = models.CharField(max_length=400, null=True, blank=True)
	# HACK: SUMMARY STATS FOR CONVENIENCE
	summary1 = models.IntegerField(default=0) 
	summary2 = models.IntegerField(default=0) 
	summary3 = models.IntegerField(default=0) 
	summary4 = models.IntegerField(default=0) 
	summary5 = models.IntegerField(default=0) 
	summary6 = models.IntegerField(default=0) 
	summary7 = models.IntegerField(default=0) 
	summary8 = models.IntegerField(default=0) 
	summary9 = models.IntegerField(default=0) 
	summary10 = models.IntegerField(default=0) 

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

class Campaign(models.Model):
	"""
	Class for campaign.
	Campaign is the adspace equivalent for advertiser.
	"""
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	description = models.CharField(max_length=200)
	category = models.CharField(max_length=200)
	# HACK: SAVE STATS AS STRINGS THEN PARSE IN VIEW
	stats1 = models.CharField(max_length=400, null=True, blank=True)
	stats2 = models.CharField(max_length=400, null=True, blank=True)
	stats3 = models.CharField(max_length=400, null=True, blank=True)
	stats4 = models.CharField(max_length=400, null=True, blank=True)
	stats5 = models.CharField(max_length=400, null=True, blank=True)
	stats6 = models.CharField(max_length=400, null=True, blank=True)
	stats7 = models.CharField(max_length=400, null=True, blank=True)
	stats8 = models.CharField(max_length=400, null=True, blank=True)
	stats9 = models.CharField(max_length=400, null=True, blank=True)
	stats10 = models.CharField(max_length=400, null=True, blank=True)
	# HACK: SUMMARY STATS FOR CONVENIENCE
	summary1 = models.IntegerField(default=0) 
	summary2 = models.IntegerField(default=0) 
	summary3 = models.IntegerField(default=0) 
	summary4 = models.IntegerField(default=0) 
	summary5 = models.IntegerField(default=0) 
	summary6 = models.IntegerField(default=0) 
	summary7 = models.IntegerField(default=0) 
	summary8 = models.IntegerField(default=0) 
	summary9 = models.IntegerField(default=0) 
	summary10 = models.IntegerField(default=0) 

	def __str__(self):             
		return self.name

class Contract(models.Model):
	"""
	Class for contract.
	This is not the actual Ethereum/NEM smart contract.
	"""
	advertiser = models.ForeignKey(User, on_delete=models.CASCADE)
	adspace = models.ForeignKey(Adspace, on_delete=models.CASCADE)
	name = models.CharField(max_length=20)
	start_time = models.DateTimeField(null=True, blank=True)
	end_time = models.DateTimeField(null=True, blank=True)
	active = models.BooleanField()
	currency = models.CharField(max_length=20)
	# HACK: SAVE STATS AS STRINGS THEN PARSE IN VIEW
	stats1 = models.CharField(max_length=400, null=True, blank=True) # earnings time series
	stats2 = models.CharField(max_length=400, null=True, blank=True)
	stats3 = models.CharField(max_length=400, null=True, blank=True)
	stats4 = models.CharField(max_length=400, null=True, blank=True)
	stats5 = models.CharField(max_length=400, null=True, blank=True)
	stats6 = models.CharField(max_length=400, null=True, blank=True)
	stats7 = models.CharField(max_length=400, null=True, blank=True)
	stats8 = models.CharField(max_length=400, null=True, blank=True)
	stats9 = models.CharField(max_length=400, null=True, blank=True)
	stats10 = models.CharField(max_length=400, null=True, blank=True)
	# HACK: SUMMARY STATS FOR CONVENIENCE
	summary1 = models.IntegerField(default=0) 
	summary2 = models.IntegerField(default=0) 
	summary3 = models.IntegerField(default=0) 
	summary4 = models.IntegerField(default=0) 
	summary5 = models.IntegerField(default=0) 
	summary6 = models.IntegerField(default=0) 
	summary7 = models.IntegerField(default=0) 
	summary8 = models.IntegerField(default=0) 
	summary9 = models.IntegerField(default=0) 
	summary10 = models.IntegerField(default=0) 

	def __str__(self):             
		return self.name