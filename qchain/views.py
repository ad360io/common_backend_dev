import account.views
import qchain.forms
import time
import datetime
import random
import unicodedata
from django.shortcuts import render
from .models import Adspace, Website, Contract,\
    RequestForAdv, AD_TYPES, GENRE_CHOICES, Stat, Agent
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from qchain.forms import RequestForm, AdspaceForm, DetailForm
from qchain.serializers import AdspaceSerializer, \
    AdSerializer, RequestForAdvSerializer, WebsiteSerializer, \
    ContractSerializer, StatSerializer
from rest_framework.decorators import api_view
from rest_framework import response

# class AdspaceViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = Adspace.objects.all()
#     serializer_class = DinosaurSerializer


@login_required
def marketplace(request):
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
                my_adreq_list = my_adreq_list.filter(adsp__adtype__in=qstr)
            if 'genre' in request.GET:
                qstr = [dict(GENRE_CHOICES)[a_genre] for a_genre in
                        request.GET.getlist('genre')]
                qstr = request.GET.getlist('genre')
                my_adreq_list = my_adreq_list.filter(adsp__genre__in=qstr)
            if 'minrate' in request.GET and 'maxrate' in request.GET:
                if request.GET.get('minrate') != u'' and request.GET.get('maxrate') != u'':
                    print(request.GET.getlist('minrate'),request.GET.getlist('maxrate'))
                    if request.GET.get('minrate') > request.GET.get('maxrate'):
                        print("incorrect rates")
                        context['ferrors'].append(("Invalid rates. Min rate should"
                                                   " be less than max rate"))
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
        my_adsp_list = [areq.adsp.all()[0] for areq in my_adreq_list]
        # context['my_adsp_list'] = my_adsp_list
        print(context)
        form = RequestForm()
        context['my_adreq_list'] = my_adreq_list
        context['form'] = form
        if not(context['ferrors']):
            context['my_both_list'] = zip(my_adreq_list,my_adsp_list)
            context['my_adreq_list'] = my_adreq_list
        return render(request, 'marketplace_ad.html', context)
    else:
        form = RequestForm()
        my_ad_list = Adspace.objects.all()
        context = {'my_ad_list': my_ad_list, 'form': form}
        print("Got 2 list function")
        # TODO: FILTER BY PREFERENCES
        return render(request, 'marketplace_ad.html', context)

@api_view(['GET', 'POST'])
def marketplace_ser(request):
    """
    List of all adspaces.
    User should be able to filter/search.
    Returns rest_framework response.Response objects.
    """

    if request.method == "GET":
        # TODO Swap out the commented lines below
        # my_adreq_list = RequestForAdv.objects.filter(adsp__publisher=request.user)
        my_adreq_list = RequestForAdv.objects.all()
        context = {}
        if request.data:
            # TODO Test out one filter like currency and then the rest.
            # if 'currency' in request.data:
            #     my_adreq_list = my_adreq_list.filter(currency__iexact=
            #                                          request.GET['currency'])
            if 'adtype' in request.GET:
                qstr = [dict(AD_TYPES)[a_type] for a_type in
                        request.GET.getlist('adtype')]
                my_adreq_list = my_adreq_list.filter(adsp__adtype__in=qstr)
            # if 'genre' in request.GET:
            #     qstr = [dict(GENRE_CHOICES)[a_genre] for a_genre in
            #             request.GET.getlist('genre')]
            #     qstr = request.GET.getlist('genre')
            #     my_adreq_list = my_adreq_list.filter(adsp__genre__in=qstr)
            # if 'minrate' in request.GET and 'maxrate' in request.GET:
            #     if request.GET.get('minrate') != u'' and request.GET.get('maxrate') != u'':
            #         print(request.GET.getlist('minrate'),request.GET.getlist('maxrate'))
            #         if request.GET.get('minrate') > request.GET.get('maxrate'):
            #             print("incorrect rates")
            #             context['ferrors'].append(("Invalid rates. Min rate should"
            #                                        " be less than max rate"))
            # if 'minrate' in request.GET:
            #     if request.GET.get('minrate') is not u'':
            #         minrate = request.GET.get('minrate')
            #         my_adreq_list = my_adreq_list.filter(asking_rate__gte=
            #                                              minrate)
            # if ('maxrate' in request.GET):
            #     if request.GET.get('maxrate') is not u'':
            #         maxrate = request.GET.get('maxrate')
            #         my_adreq_list = my_adreq_list.filter(asking_rate__lte=
            #                                              maxrate)
        my_adsp_list = [areq.adsp.all()[0] for areq in my_adreq_list]
        serializer = AdSerializer(my_adsp_list, many=True)
        context['my_adsp_list'] = serializer.data
        serializer = RequestForAdvSerializer(my_adreq_list, many=True)
        context['my_adreq_list'] = serializer.data
        # if not(context['ferrors']):
        #     context['my_both_list'] = zip(my_adreq_list,my_adsp_list)
        #     context['my_adreq_list'] = my_adreq_list
        return response.Response(context)
    elif request.method=="POST":
        form = RequestForm()
        print(request.user)
        my_adreq_list = RequestForAdv.objects.filter(adsp__publisher=request.user)
        context = {'my_ad_list': my_adreq_list, 'form': form}
        return response.Response(context)

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

# @login_required
@api_view(['GET', 'POST'])
def testview0(request):
    """
    Test view to act as placeholder while developing. Remove during production.
    """
    print(type(request))
    # help(request)
    print(request.content_type)
    if request.method == "GET":
        print("testview0")
        print(request.user)
        # return response.Response({"message": "Hello, world!", "m2": 2, "m3": 2.5})
        x = Adspace.objects.get(pk=1)
        x = AdspaceSerializer(x)
        y = Adspace.objects.all()
        y = AdspaceSerializer(y, many=True)
        y2 = [1,2,3,3,4]
        return response.Response({"j":"jetti", "x":x.data, "y":y.data, "y2":y2})
    elif request.method == "POST":
        print("testview1")
        obj = AdspaceSerializer(data=request.data)
        print(type(obj),obj)
        if obj.is_valid():
            print("Valid tooo")
            obj.save()
            print("Saved the objects to database")

        return response.Response({"j":"jetti2"})

def testview1(request, ctype1):
    """
    Test view to act as placeholder while developing. Remove during production.
    """
    print(ctype1)
    return render(request, 'test_page.html')

def testview_ser(request):
    """
    View to
    """
    print("GOt to testview_ser")
    # x = 5
    # data = JSONRenderer().render(x)
    temp = Adspace.objects.get(pk=1)
    ser = AdspaceSerializer(temp)
    print(ser.data)
    return JsonResponse(ser.data)

def create_adsp(request):
    """
    View to create adspace for publisher
    """
    context = {}
    context['ferrors'] = []
    if request.method == "GET":
        # TODO in front end create teh form.
        return response.Response({"junk":42.5})
    elif request.method == "POST":
        print("Other method")
        ## TODO: Save form
        serializer = AdspaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("Saved the object to database")
        else:
            print("Form not valid for some reason : ")
            raise ValidationError(_(serializer.errors))
        return response.Response({"junk":42.5})
    return response.Response({"junk":42.5}) #Maybe 404

@api_view(['GET', 'POST'])
def create_ad(request):
    """
    To do like above.
    """

@api_view(['GET', 'POST'])
def create_requestforadsp(request):
    """
    To do like above.
    """

@api_view(['GET', 'POST'])
def create_requestforad(request):
    """
    To do like above.
    """

# @login_required
@api_view(['GET', 'POST'])
def create_adsp_ser(request):
    """
    View to create adspace for publisher (serializer)
    """
    print("reqiest method is : " + request.method)
    context = {}
    context['ferrors'] = []
    if request.method == "GET":
        print("Get method in create_adsp_ser")
        # data = Adspace.objects.get(pk=1)
        # serializer = AdspaceSerializer(data)
        # print("Serialized data is: ", serializer.data)
        print(request.user)
        websites = list(set([an_adsp.website for an_adsp in \
        Adspace.objects.filter(publisher=request.user)]))
        print(websites, type(websites))
        serializer = WebsiteSerializer(websites, many=True)
        context = {'websites' : serializer.data}
        # return render(request, 'create_adsp.html', context)
        # return JsonResponse(ser.data, safe=False)
        # TODO Somehow use this to make a form.
        return response.Response({"data":serializer.data})
    elif request.method=="POST":
        print("Post method")
        ## TODO: Save form
        # data = JSONParser().parse(request)
        # print(data)
        print(request.data)
        serializer = AdspaceSerializer(data=request.data)
        if serializer.is_valid():
            # TODO have to set the user somehow and test it too. And then save.
            # Will commit=False work? serializer.publisher prob won't work.
            print("Valid serializer")
            # serializer.save(commit=False)
            # serializer.publisher = request.user
            # serializer.save()
            return response.Response(serializer.data) #Code 201
        else:
            print("Invalid serializer")
        return response.Response(serializer.errors) #Code 400

    return render(request, 'create_adsp.html')


@login_required
def pub_dashboard(request, ctype1=0, ctype2=0):
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
    print("User is  : ",request.user)
    print("Ctype1 : ",ctype1)
    print("Ctype2 : ",ctype2)
    try:
        # GET ADSPACES AND DATA ANALYSIS
        # get adspaces owned by user
        my_adsp_list = Adspace.objects.filter(publisher=request.user)
        my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        print("Ads : ", my_adsp_list)
        print("Contracts : ", my_cont_list)
        print("Stats : ", my_stat_list)
        # my_stat_list = sorted(my_stat_list,key=lambda a_stat: a_stat.stat_date)
        context['my_ad_list'] = my_adsp_list
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
        # print(datetime.datetime(2017, 5,1), type(datetime.datetime(2017, 5,1)))
        # print(datetime.datetime(2017, 5,1).timetuple(), type(datetime.datetime(2017, 5,1).timetuple()))
        # print(time.mktime(datetime.datetime(2017, 5,1).timetuple())*10000,
        # type(time.mktime(datetime.datetime(2017, 5,1).timetuple())))
        # start_time = int(time.mktime(datetime.datetime(2017, 5,
        #                                                1).timetuple()) * 1000)
        # xdata = range(nb_element)
        # xdata = map(lambda x: start_time + x * 100000000, xdata)
        # print("xdata is : ",xdata,type(xdata))
        times = [int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]
        times2 = [a_stat.stat_date for a_stat in my_stat_list]

        tooltip_date = "%d %b %Y %H:%M:%S %p"
        extra_serie = {"tooltip": {"y_start": "There are ", "y_end": " calls"},
                       "date_format": tooltip_date}
        chartdata = {'x': sorted(times)}
        charttype = "lineWithFocusChart"
        print(my_adsp_list)
        for ind1,an_adsp in enumerate(my_adsp_list):
            # Find all contracts with this adspace, and get all the stats for
            # that contract. Currently only earnings
            if ind1<5:
                chartdata['name' + str(ind1)] = an_adsp.name
                related_cont_list = my_cont_list.filter(adspace=an_adsp)
                for a_cont in related_cont_list:
                    related_stat_list = my_stat_list.filter(contract=a_cont)
                    related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                    stat2plot = []
                    for a_stat in related_stat_list:
                        if ctype1==u'0' or ctype1==0:
                            stat2plot.append(float(a_stat.revenue))
                        elif ctype1==u'1':
                            stat2plot.append(float(a_stat.clicks))
                        elif ctype1==u'2':
                            stat2plot.append(float(a_stat.impressions))
                chartdata['y' + str(ind1)] = stat2plot
                chartdata['extra' + str(ind1)] = extra_serie

        count = 1

        # CREATE PLOT
        data = {'charttype': charttype,
                'chartdata': chartdata
                }
        chartcontainer = "linewithfocuschart_container"
        context['charttype1'] = charttype
        context['chartdata1'] = chartdata
        context['chartcontainer1'] = chartcontainer
        context['extra1'] = {'x_is_date': True,
                             'x_axis_format': '%d %b %Y',
                             'tag_script_js': True,
                             'jquery_on_ready': False,
                             }

        # context['metric1_today'] = round(earnings_today / clicks_today, 2)
        # context['metric1_30day'] = round(earnings_30day / clicks_30day, 2)
        # context['metric1_change'] = round(100 * earnings_today /
        #                                   clicks_today /
        #                                   (earnings_30day /
        #                                    clicks_30day) - 100, 2)
        # context['metric2_today'] = round(earnings_today / impressions_today, 2)
        # context['metric2_30day'] = round(earnings_30day / impressions_30day, 2)
        # context['metric2_change'] = round(100 * earnings_today /
        #                                   impressions_today /
        #                                   (earnings_30day /
        #                                    impressions_30day) - 100, 2)
        print(datetime.date.today())
        today_stats = my_stat_list.filter(stat_date=datetime.date.today())
        if today_stats:
            nstats = len(today_stats)
            context['revenue_today'] = round(sum([today_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
            context['impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            context['rpm_today'] = round(sum([today_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['revenue_today'] = 0
            context['clicks_today'] = 0
            context['impressions_today'] = 0
            context['rpm_today'] = 0

        month_stats = my_stat_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
        if month_stats:
            nstats = len(month_stats)
            context['revenue_30day'] = round(sum([month_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
            context['impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            context['rpm_30day'] =  round(sum([month_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['revenue_30day'] = 0
            context['clicks_30day'] = 0
            context['impressions_30day'] = 0
            context['rpm_30day'] = 0

        context['metric1_today'] = 2
        context['metric1_30day'] = 2
        context['metric1_change'] = 2
        context['metric2_today'] = 2
        context['metric2_30day'] = 2
        context['metric2_change'] = 2
    except Adspace.DoesNotExist:
    #    context['views_ts'] = False
        context['my_ad_list'] = False

    # SECOND PLOT
    xdata, ydata = [], []
    for ind in range(len(my_cont_list)):
        xdata.append(my_cont_list[ind].name)
        related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
        # tydata = [float(a_str) for a_str in str(my_cont_list[ind].stats1).
        #           split(",")]
        try:
            if ctype2 == u'0' or ctype2 == 0:
                deltaval = -7
                # ydata.append(tydata[-1])
            elif ctype2 == u'1':
                deltaval = -30
                ydata.append(sum(tydata[-7:]))
            elif ctype2 == u'2':
                deltaval = -100000
        except:
            print("no ctype 2")
            deltaval = -7
            # ydata.append(tydata[-1])
        related_stat_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(deltaval))
        if sum([a_stat.revenue for a_stat in related_stat_list]):
            ydata.append(sum([a_stat.revenue for a_stat in related_stat_list]))
        else:
            ydata.append(0)
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

# @login_required
@api_view(['GET', 'POST'])
def pub_dashboard_ser(request):
    """
    Publisher dashboard.
    """
    context = {}
    print("Got to pub_dashboard_ser")
    # print("User is  : ",request.user)
    ## TODO
    ## 1. Make this work with request.user (Django Sessions)
    ## 2. Fill up more data
    ## 3. Add a balance and account number to the profile.
    ## 4. Verify filters and sent data when awake :D
    ## 5. Little green box - daily change should be calculated

    try:
        # get adspaces owned by user
        t = Agent.objects.all()
        print(t,t[2].user, type(t[2]))
        # my_adsp_list = Adspace.objects.filter(publisher=request.user)
        # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        my_adsp_list = Adspace.objects.filter(publisher=t[2].user)
        my_cont_list = Contract.objects.filter(adspace__publisher=t[2].user)
        my_stat_list = Stat.objects.filter(contract__adspace__publisher=t[2].user)
        print("Ads : ", my_adsp_list)
        print("Contracts : ", my_cont_list)
        print("Stats : ", my_stat_list)

        ser = AdspaceSerializer(my_adsp_list, many=True)
        context['my_ad_list'] = ser.data
        # ser = ContractSerializer(my_cont_list, many=True)
        # context['my_cont_list'] = my_cont_list

        # SUMMARY STATS
        earnings_today = 0
        clicks_today = 0
        impressions_today = 0
        earnings_30day = 0
        clicks_30day = 0
        impressions_30day = 0
        # TIME SERIES PLOT
        nb_element = 30

        times = [int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]
        times2 = [a_stat.stat_date for a_stat in my_stat_list]
        ## SHIVA: Don't know which format you want time in, replace times with
        ## times2 in the next line if needed. Seems like times is more versatile
        ## and can be converted to other formats in front end as was happening
        ## earlier. Times2 is more restricted but is hard to transform.
        context['c1_x'] = sorted(times)
        context['c1_adspnames'] = []

        for ind1,an_adsp in enumerate(my_adsp_list):
            context['c1_y_revenue'+str(ind1)] = [0]*len(times)
            context['c1_y_clicks'+str(ind1)] = [0]*len(times)
            context['c1_y_impression'+str(ind1)] = [0]*len(times)
            # Find all contracts with this adspace, and get all the stats for
            # those contracts and sum. Currently only earnings
            if ind1<5:
                context['c1_adspnames'].append(an_adsp.name)
                related_cont_list = my_cont_list.filter(adspace=an_adsp)
                for a_cont in related_cont_list:
                    related_stat_list = my_stat_list.filter(contract=a_cont)
                    related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                    for a_stat in related_stat_list:
                        time_index = times2.index(a_stat.stat_date)
                        context['c1_y_revenue'+str(ind1)][time_index]+=float(a_stat.revenue)
                        context['c1_y_clicks'+str(ind1)][time_index]+=float(a_stat.clicks)
                        context['c1_y_impression'+str(ind1)][time_index]+=float(a_stat.impressions)

        today_stats = my_stat_list.filter(stat_date=datetime.date.today())
        if today_stats:
            nstats = len(today_stats)
            context['topstat_revenue_today'] = round(sum([today_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['topstat_clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
            context['topstat_impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            context['topstat_rpm_today'] = round(sum([today_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['topstat_revenue_today'] = 0
            context['topstat_clicks_today'] = 0
            context['topstat_impressions_today'] = 0
            context['topstat_rpm_today'] = 0

        month_stats = my_stat_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
        if month_stats:
            nstats = len(month_stats)
            context['topstat_revenue_30day'] = round(sum([month_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['topstat_clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
            context['topstat_impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            context['topstat_rpm_30day'] =  round(sum([month_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['topstat_revenue_30day'] = 0
            context['topstat_clicks_30day'] = 0
            context['topstat_impressions_30day'] = 0
            context['topstat_rpm_30day'] = 0

    except Adspace.DoesNotExist:
        context['is_error'] = "No adspaces found"

    # SECOND PLOT
    xdata = []
    context['c2_y_weekrevenue'] = [0]*len(my_cont_list)
    context['c2_y_day30revenue'] = [0]*len(my_cont_list)
    context['c2_y_alltimerevenue'] = [0]*len(my_cont_list)
    for ind in range(len(my_cont_list)):
        xdata.append(my_cont_list[ind].name)
        related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
        week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
        day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
        alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
        context['c2_y_weekrevenue'][ind] = sum([a_stat.revenue for a_stat in week_list])
        context['c2_y_day30revenue'][ind] = sum([a_stat.revenue for a_stat in day30_list])
        context['c2_y_alltimerevenue'][ind] = sum([a_stat.revenue for a_stat in alltime_list])
        # In the front end, sum up the correct list, round to 0 places and display.

    context['c2_xdata'] = xdata

    return response.Response(context)

# INSTANCE CREATION & MANAGEMENT FOR WEBSITE, ADSPACE, CAMPAIGN, CONTRACT


# LOW PRIORITY
# @login_required
# def create_ad(request):
#     """
#     Create a new adspace.
#     """
#     if request.method == 'POST':
#         form = AdspaceForm(request.POST)
#         if form.is_valid():
#             new_ad = form.save(commit=False)
#             new_ad.user = request.user
#             new_ad.save()
#             # increment website adcount
#             current_website = form.cleaned_data["website"]
#             current_website.save()
#     else:
#         form = AdspaceForm()
#         form.fields['website'].queryset = Website.objects.filter(user=request.user)
#     return render(request, 'create_ad.html', {'form': form})
