import account.views
import qchain.forms
import time
import datetime
import random
import unicodedata
from django.shortcuts import render
from .models import Adspace, Website, AdspaceForm, Contract,\
    RequestForAdv, AD_TYPES, GENRE_CHOICES
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from .forms import RequestForm


# DEPRECATED
@login_required
def godlike(request):
    user = request.user
    # create a website
    title = user.username
    url = 'https://wwww.' + user.username + '.com'
    keywords = 'Tech, finance'
    website = Website(user=user, link=url, name=title, description=keywords,
                      category='NONPOL')
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
    print("reqiest method is : " + request.method)
    context = {}
    context['ferrors'] = []
    if request.method == "GET":
        my_adreq_list = RequestForAdv.objects.all()
        if request.GET:
            if 'currency' in request.GET:
                my_adreq_list = my_adreq_list.filter(currency__iexact=
                                                     request.GET['currency'])
            if 'adtype' in request.GET:
                qstr = [dict(AD_TYPES)[a_type] for a_type in
                        request.GET.getlist('adtype')]
                my_adreq_list = my_adreq_list.filter(adtype__in=qstr)
            if 'genre' in request.GET:
                qstr = [dict(GENRE_CHOICES)[a_genre] for a_genre in
                        request.GET.getlist('genre')]
                qstr = request.GET.getlist('genre')
                my_adreq_list = my_adreq_list.filter(genre__in=qstr)
            if 'minrate' in request.GET and 'maxrate' in request.GET:
                if request.GET.get('minrate') > request.GET.get('maxrate'):
                    print("incorrect rates")
                    context['ferrors'].append(("Invalid rates. Max rate should"
                                               " be less than min rate"))
            if 'minrate' in request.GET:
                if request.GET.get('minrate') is not u'':
                    minrate = request.GET.get('minrate')
                    my_adreq_list = my_adreq_list.filter(asking_rate__gte=
                                                         minrate)
            if ('maxrate' in request.GET):
                if request.GET.get('maxrate') is not u'':
                    maxrate = request.GET.get('maxrate')
                    my_adreq_list = my_adreq_list.filter(asking_rate__lte=
                                                         maxrate)

        form = RequestForm()
        context['my_ad_list'] = my_adreq_list
        context['form'] = form
        return render(request, 'marketplace_ad.html', context)
    else:
        form = RequestForm()
        my_ad_list = Adspace.objects.all()
        context = {'my_ad_list': my_ad_list, 'form': form}
        print("Got 2 list function")
        # TODO: FILTER BY PREFERENCES
        return render(request, 'marketplace_ad.html', context)


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


def testview(request, ctype1):
    """
    Test view to act as placeholder while developing. Remove during production.
    """
    print(ctype1)
    return render(request, 'test_page.html')


# DEPRECATED
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
            agent = request.user.agent  # agent and user are one-to-one
            # get form info (only birthdate for now)
            agent.birthdate = form.cleaned_data["birthdate"]
            agent.save()
    else:
        form = qchain.forms.DetailForm()
    # TODO: display current details and confirm changes
    return render(request, 'details.html', {'form': form})


@login_required
def pub_dashboard(request):
    """
    Publisher dashboard.
    """
    context = {}
    #try:
        # # get websites owned by user
        #my_website_list = Website.objects.filter(user=request.user)
        #context['my_website_list'] = my_website_list
    #except Website.DoesNotExist:
        #context['my_website_list'] = False
    print("Got to pub_dashboard")
    try:
        # GET ADSPACES AND DATA ANALYSIS
        # get adspaces owned by user
        my_ad_list = Adspace.objects.filter(user=request.user)
        my_cont_list = Contract.objects.filter(advertiser=request.user)
        print(my_cont_list)
        context['my_ad_list'] = my_ad_list
        context['my_cont_list'] = my_cont_list
        # SUMMARY STATS
        earnings_today = 0
        clicks_today = 0
        impressions_today = 0
        earnings_30day = 0
        clicks_30day = 0
        impressions_30day = 0
        # TIME SERIES PLOT
        nb_element = 30
        start_time = int(time.mktime(datetime.datetime(2017, 5,
                                                       1).timetuple()) * 1000)
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
            clicks_series = [int(float(i)) for i in clicks_as_list]
            clicks_today += clicks_series[-1]
            clicks_30day += sum(clicks_series)
            # impressions
            impressions = e.stats3
            impressions_as_list = impressions.split(',')
            impressions_series = [int(float(i)) for i in impressions_as_list]
            impressions_today += impressions_series[-1]
            impressions_30day += int(sum(impressions_series))
            count += 1
        # CREATE PLOT
        data = {'charttype': charttype,
                'chartdata': chartdata
                }
        chartcontainer = "linewithfocuschart_container"
        context['charttype1'] = charttype
        context['chartdata1'] = chartdata
        context['chartcontainer1'] = chartcontainer
        context['extra1'] = {'x_is_date': True,
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
        context['metric1_change'] = round(100 * earnings_today /
                                          clicks_today /
                                          (earnings_30day /
                                           clicks_30day) - 100, 2)
        context['metric2_today'] = round(earnings_today / impressions_today, 2)
        context['metric2_30day'] = round(earnings_30day / impressions_30day, 2)
        context['metric2_change'] = round(100 * earnings_today /
                                          impressions_today /
                                          (earnings_30day /
                                           impressions_30day) - 100, 2)
    except Adspace.DoesNotExist:
    #    context['views_ts'] = False
        context['my_ad_list'] = False

    # SECOND PLOT
    xdata, ydata = [], []
    print("GOing to try to check for ctype2")
    for ind in range(len(my_cont_list)):
        xdata.append(my_cont_list[ind].adspace.name)
        tydata = [float(a_str) for a_str in str(my_cont_list[ind].stats1).
                  split(",")]
        try:
            print("Got here")
            if ctype2 == u'0':
                ydata.append(tydata[-1])
            elif ctype2 == u'1':
                ydata.append(sum(tydata[-7:]))
            elif ctype2 == u'2':
                ydata.append(sum(tydata))
        except:
            print("Exception generated for plot2")
            ydata.append(tydata[-1])
    ydata = [int(round(x)) for x in ydata]

    extra_serie1 = {"tooltip": {"y_start": "", "y_end": " cal"}}
    chartdata = {'x': xdata, 'name1': '', 'y1': ydata, 'extra1': extra_serie1,
                 }
    charttype = "discreteBarChart"
    data = {'charttype': charttype, 'chartdata': chartdata, }
    chartcontainer = "discretebarchart_container"
    context['charttype2'] = charttype
    context['chartdata2'] = chartdata
    context['chartcontainer2'] = chartcontainer
    context['extra2'] = {'x_is_date': False,
                         'x_axis_format': '',
                         'tag_script_js': True,
                         'jquery_on_ready': True, }

    # DON'T WANT TO HANDLE FORMS ON THE DASHBOARD
    #if request.method == 'POST':
        # # NOTE: TWO FORMS DON'T WORK AT THE SAME TIME
        #web_form = WebsiteForm(request.POST)
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


@login_required
def pub_dashboard2(request, ctype1=0, ctype2=0):
    """
    Publisher dashboard.
    """
    context = {}
    #try:
        #my_website_list = Website.objects.filter(user=request.user)
        # # get websites owned by user
        #context['my_website_list'] = my_website_list
    #except Website.DoesNotExist:
        #context['my_website_list'] = False
    try:
        # GET ADSPACES AND DATA ANALYSIS
        # get adspaces owned by user
        my_ad_list = Adspace.objects.filter(user=request.user)
        my_cont_list = Contract.objects.filter(advertiser=request.user)
        context['my_ad_list'] = my_ad_list
        context['my_cont_list'] = my_cont_list
        # SUMMARY STATS
        earnings_today = 0
        clicks_today = 0
        impressions_today = 0
        earnings_30day = 0
        clicks_30day = 0
        impressions_30day = 0
        # TIME SERIES PLOT
        nb_element = 30
        start_time = int(time.mktime(datetime.datetime(2017, 5,
                                                       1).timetuple()) * 1000)
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
            # clicks
            clicks = e.stats2
            clicks_as_list = clicks.split(',')
            clicks_series = [int(float(i)) for i in clicks_as_list]
            clicks_today += clicks_series[-1]
            clicks_30day += sum(clicks_series)
            # impressions
            impressions = e.stats3
            impressions_as_list = impressions.split(',')
            impressions_series = [int(float(i)) for i in impressions_as_list]
            impressions_today += impressions_series[-1]
            impressions_30day += int(sum(impressions_series))

            if count < 6:
                chartdata['name' + str(count)] = e.name
                if ctype1 == u'0':
                    chartdata['y' + str(count)] = earnings_series
                elif ctype1 == u'1':
                    chartdata['y' + str(count)] = clicks_series
                else:
                    chartdata['y' + str(count)] = impressions_series
                chartdata['extra' + str(count)] = extra_serie

            count += 1
        # CREATE PLOT
        data = {'charttype': charttype, 'chartdata': chartdata}
        chartcontainer = "linewithfocuschart_container"
        context['charttype1'] = charttype
        context['chartdata1'] = chartdata
        context['chartcontainer1'] = chartcontainer
        context['extra1'] = {'x_is_date': True,
                             'x_axis_format': '%d %b %Y',
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
        context['metric1_change'] = round(100 * earnings_today /
                                          clicks_today /
                                          (earnings_30day /
                                           clicks_30day) - 100, 2)
        context['metric2_today'] = round(earnings_today / impressions_today, 2)
        context['metric2_30day'] = round(earnings_30day / impressions_30day, 2)
        context['metric2_change'] = round(100 * earnings_today /
                                          impressions_today /
                                          (earnings_30day /
                                           impressions_30day) - 100, 2)
        if isinstance(ctype1, unicode):
            context['c1'] = unicodedata.digit(ctype1)
        else:
            context['c1'] = ctype1
        if isinstance(ctype2, unicode):
            context['c2'] = unicodedata.digit(ctype2)
        else:
            context['c2'] = ctype2
        # context['c2'] =. unicodedata.digit(ctype2)
    except Adspace.DoesNotExist:
    #    context['views_ts'] = False
        print('Adspace doest not exist')
        context['my_ad_list'] = False

    # SECOND PLOT
    xdata, ydata = [], []
    for ind in range(len(my_cont_list)):
        xdata.append(my_cont_list[ind].adspace.name)
        tydata = [float(a_str) for a_str in str(my_cont_list[ind].stats1
                                                ).split(",")]
        if ctype2 == u'0' or ctype2==0:
            ydata.append(tydata[-1])
        elif ctype2 == u'1':
            ydata.append(sum(tydata[-7:]))
        elif ctype2 == u'2':
            ydata.append(sum(tydata))
        else:
            print("ctype2 was none of those : ",ctype2)
    ydata = [int(round(x)) for x in ydata]

    extra_serie1 = {"tooltip": {"y_start": "", "y_end": " cal"}}
    chartdata = {'x': xdata, 'name1': '', 'y1': ydata, 'extra1': extra_serie1,
                 }
    charttype = "discreteBarChart"
    data = {'charttype': charttype, 'chartdata': chartdata, }
    chartcontainer = "discretebarchart_container"
    context['charttype2'] = charttype
    context['chartdata2'] = chartdata
    context['chartcontainer2'] = chartcontainer
    context['extra2'] = {'x_is_date': False, 'x_axis_format': '',
                         'tag_script_js': True, 'jquery_on_ready': True, }

    # DON'T WANT TO HANDLE FORMS ON THE DASHBOARD
    #if request.method == 'POST':
        # NOTE: TWO FORMS DON'T WORK AT THE SAME TIME
        #web_form = WebsiteForm(request.POST)
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

# INSTANCE CREATION & MANAGEMENT FOR WEBSITE, ADSPACE, CAMPAIGN, CONTRACT


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
