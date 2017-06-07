import account.views
import qchain.forms
import time, datetime, random
from django.shortcuts import render
from .models import Adspace, Website, WebsiteForm, AdspaceForm
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required


# CREATE A BUNCH OF STUFF
@login_required
def godlike(request):
	user = request.user
	# create a website
	title = user.username
	url = 'https://wwww.' + user.username + '.com'
	keywords = 'Tech, finance'
	website = Website(user=user, link=url, name=title,
		description=keywords, category='NONPOL')
	website.save()
	# create ads
	for i in range(5):
		name = 'space' + str(i)
		current_ad = Adspace(user=user, website=website, name=name,
			height=400, width=200, adtype='BANNER')
		current_ad.save()



# MEDIUM PRIORITY
def list(request):
	"""
	List of all adspaces.
	User should be able to filter/search.
	"""
	latest_ad_list = Adspace.objects.all()
	context = {'latest_ad_list': latest_ad_list}
	# TODO: FILTER BY PREFERENCES
	return render(request, 'list.html', context)


# LOW PRIORITY
def ad_detail(request, ad_id):
	"""
	Adspace details.
	Static without actual functionality.
	"""
	try:
		ad = Adspace.objects.get(pk=ad_id)
	except Adspace.DoesNotExist:
		raise Http404("Adspace does not exist")
	return render(request, 'ad_detail.html', {'ad': ad})


# TEMPORARILY DEPRECATED
def ad_list(request, web_id):
	"""
	List of adspaces on a website.
	"""
	try:
		site = Website.objects.get(pk=web_id)
		ad_list = Adspace.objects.filter(website=site)
	except Adspace.DoesNotExist:
		raise Http404("Website does not exist")
	return render(request, 'ad_list.html', {'ad_list': ad_list})


# LOW PRIORITY
@login_required
def agent_details(request):
	"""
	Edit agent details/user profile.
	"""
	if request.method == 'POST':
		form = qchain.forms.DetailForm(request.POST)
		if form.is_valid():
			agent = request.user.agent # agent and user are one-to-one
			agent.birthdate = form.cleaned_data["birthdate"] # get form info (only birthdate for now)
			agent.save()
	else:
		form = qchain.forms.DetailForm()
	# TODO: display current details and confirm changes
	return render(request, 'details.html', {'form': form})


# SHORT TERM GOAL
@login_required
def pub_dashboard(request):
	"""
	Publisher dashboard.
	"""
	context = {}
	#try:
		#my_website_list = Website.objects.filter(user=request.user) # get websites owned by user
		#context['my_website_list'] = my_website_list
	#except Website.DoesNotExist:
		#context['my_website_list'] = False
	try:
		# GET ADSPACES AND DATA ANALYSIS
		my_ad_list = Adspace.objects.filter(user=request.user) # get adspaces owned by user
		context['my_ad_list'] = my_ad_list
		# SUMMARY STATS
		earnings_today = 0
		clicks_today = 0
		impressions_today = 0
		earnings_30day = 0
		clicks_30day = 0
		impressions_30day = 0
		# TIME SERIES PLOT
		nb_element = 30
		start_time = int(time.mktime(datetime.datetime(2017, 5, 1).timetuple()) * 1000)
		xdata = range(nb_element)
		xdata = map(lambda x: start_time + x * 100000000, xdata)
		tooltip_date = "%d %b %Y %H:%M:%S %p"
		extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
		"date_format": tooltip_date}
		chartdata = {'x': xdata}
		charttype = "lineWithFocusChart"
		count = 1
		# MAIN LOOP
		for e in my_ad_list:
			# earnings
			earnings = e.stats1
			earnings_as_list = earnings.split(',')
			earnings_series = [float(i) for i in earnings_as_list]
			earnings_today += earnings_series[-1]
			earnings_30day += sum(earnings_series)
			# top five earnings
			if count < 6:
				chartdata['name' + str(count)] = e.name
				chartdata['y' + str(count)] = earnings_series
				chartdata['extra' + str(count)] = extra_serie
			# clicks
			clicks = e.stats2
			clicks_as_list = clicks.split(',')
			clicks_series = [float(i) for i in clicks_as_list]
			clicks_today += clicks_series[-1]
			clicks_30day += sum(clicks_series)
			# impressions
			impressions = e.stats3
			impressions_as_list = impressions.split(',')
			impressions_series = [float(i) for i in impressions_as_list]
			impressions_today += impressions_series[-1]
			impressions_30day += sum(impressions_series)
			count += 1
		# CREATE PLOT
		data = {
		'charttype': charttype,
		'chartdata': chartdata
		}
		chartcontainer = "linewithfocuschart_container"
		context['charttype1'] = charttype
		context['chartdata1'] = chartdata
		context['chartcontainer1'] = chartcontainer
		context['extra1'] = {
		'x_is_date': True,
		'x_axis_format': '%d %b %Y %H',
		'tag_script_js': True,
		'jquery_on_ready': False,
		}
		# SUMMARY STATS CALCULATION
		context['earnings_today'] = round(earnings_today, 2)
		context['earnings_30day'] = round(earnings_30day / 30.0, 2)
		context['clicks_today'] = clicks_today
		context['clicks_30day'] = round(clicks_30day / 30.0, 2)
		context['impressions_today'] = impressions_today
		context['impressions_30day'] = round(impressions_30day / 30.0, 2)
		context['metric1_today'] = round(earnings_today / clicks_today, 2)
		context['metric1_30day'] = round(earnings_30day / clicks_30day, 2)
		context['metric1_change'] = round(100 * earnings_today / clicks_today / (earnings_30day / clicks_30day) - 100, 2)
		context['metric2_today'] = round(earnings_today / impressions_today, 2)
		context['metric2_30day'] = round(earnings_30day / impressions_30day, 2)
		context['metric2_change'] = round(100 * earnings_today / impressions_today / (earnings_30day / impressions_30day) - 100, 2)
	except Adspace.DoesNotExist:
	#	context['views_ts'] = False
		context['my_ad_list'] = False

	# SECOND PLOT
	xdata = ["bank1", "apparel2", "media2", "bank2", "shopping1"]
	ydata = [23, 12, 10, 15, 3]

	extra_serie1 = {"tooltip": {"y_start": "", "y_end": " cal"}}
	chartdata = {
	'x': xdata, 'name1': '', 'y1': ydata, 'extra1': extra_serie1,
	}
	charttype = "discreteBarChart"
	data = {
	'charttype': charttype,
	'chartdata': chartdata,
	}
	chartcontainer = "discretebarchart_container"
	context['charttype2'] = charttype
	context['chartdata2'] = chartdata
	context['chartcontainer2'] = chartcontainer
	context['extra2'] = {
	'x_is_date': False,
	'x_axis_format': '',
	'tag_script_js': True,
	'jquery_on_ready': True,
	}

	# DON'T WANT TO HANDLE FORMS ON THE DASHBOARD
	#if request.method == 'POST':
		#web_form = WebsiteForm(request.POST) # NOTE: TWO FORMS DON'T WORK AT THE SAME TIME
		#if form.is_valid():
			#new_website = web_form.save(commit=False)
			#new_website.user = request.user
			#new_website.save()
	#else:
		#web_form = WebsiteForm()
		#ad_form = AdspaceForm()
	#context['web_form'] = web_form
	#context['ad_form'] = ad_form
	# TODO: WEBSITE DELETION
	return render(request, 'pub_dashboard.html', context)


############################ INSTANCE CREATION & MANAGEMENT FOR WEBSITE, ADSPACE, CAMPAIGN, CONTRACT

# LOW PRIORITY
@login_required
def create_ad(request):
	"""
	Create a new adspace.
	"""
	if request.method == 'POST':
		form = AdspaceForm(request.POST) 
		if form.is_valid():
			new_ad = form.save(commit=False)
			new_ad.user = request.user
			new_ad.save()
			# increment website adcount
			current_website = form.cleaned_data["website"]
			current_website.save()
	else:
		form = AdspaceForm()
		form.fields['website'].queryset = Website.objects.filter(user=request.user)
	return render(request, 'create_ad.html', {'form': form})