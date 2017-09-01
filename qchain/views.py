import account.views
import qchain.forms
import time
import datetime
import random
import unicodedata
import numpy as np
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from qchain.models import Adspace, Ad, Website, Contract,\
    RequestForAdv, AD_TYPES, GENRE_CHOICES, Stat, Agent
from qchain.forms import RequestForm, AdspaceForm, DetailForm
from qchain.serializers import AdspaceSerializer, \
    AdSerializer, RequestForAdvSerializer, WebsiteSerializer, \
    ContractSerializer, StatSerializer
from rest_framework import response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_401_UNAUTHORIZED
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

# class AdspaceViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = Adspace.objects.all()
#     serializer_class = DinosaurSerializer
@api_view(["GET"])
def dashboard_tables(request):
    context = {}
    if(request.GET.get("userMode") and request.GET.get("currencyType") and request.GET.get("userName")):
        userMode = request.GET.get("userMode").lower()
        currencyType = request.GET.get("currencyType").lower()
        userName = request.GET.get("userName")
        currentAgent = Agent.objects.filter(user__username=userName)
        currentUser = currentAgent[0].user
        t = Agent.objects.all()

        if(userMode == "publisher"):
            my_cont_list = Contract.objects.filter(adspace__publisher=currentUser,
                                                   currency=currencyType)

            my_adsp_list = Adspace.objects.filter(publisher=currentUser)

            context['t2_col1'] = [str(a_cont.ad.advertiser) for a_cont in my_cont_list]
            context['t2_col2'] = [a_cont.start_time.date() for a_cont in my_cont_list]
            context['t1_col1'] = [an_adsp.website.name for an_adsp in my_adsp_list]
            context['t1_col2'] = [an_adsp.adtype for an_adsp in my_adsp_list]
            context['t1_col3'] = [an_adsp.genre for an_adsp in my_adsp_list]
            print(context)
            return response.Response(context)
        elif (userMode == "advertiser"):
            my_cont_list = Contract.objects.filter(ad__advertiser=currentUser,
                                                   currency=currencyType)
            my_ad_list = Ad.objects.filter(advertiser=currentUser)
            context['t2_col1'] = [str(a_cont.adspace.publisher) for a_cont in my_cont_list]
            context['t2_col2'] = [a_cont.start_time.date() for a_cont in my_cont_list]
            context['t1_col1'] = [ad.content for ad in my_ad_list]
            context['t1_col2'] = [an_ad.adtype for an_ad in my_ad_list]
            context['t1_col3'] = [an_ad.genre for an_ad in my_ad_list]
            print(context)
            return response.Response(context)
    else:
        return response.Response({"error" : "Incorrect parameters specified"})

@api_view(["GET"])
def display_marketplace(request):
    ## As a publisher, I am looking for Ads paying me x.
    ##
    context = {}
    context['ferrors'] = []
    my_adreq_list = RequestForAdv.objects.all()
    userMode = request.GET.get("userMode").lower()
    currencyType = request.GET.get("currencyType").lower()
    adTypeList = request.GET.get("adType")
    adGenreList = request.GET.get("adGenre")
    minrate = int(request.GET.get("minrate"))
    maxrate = int(request.GET.get("maxrate"))
    if currencyType != "" :
        my_adreq_list = my_adreq_list.filter(currency__iexact=
                                             currencyType)
    # if adTypeList != [] :
    #     qstr = [dict(AD_TYPES)[a_type] for a_type in
    #             adTypeList]
    #     my_adreq_list = my_adreq_list.filter(adsp__adtype__in=qstr)
    # if adGenreList != []:
    #     qstr = [dict(GENRE_CHOICES)[a_genre] for a_genre in
    #             adGenreList]
    #     qstr = adGenreList
    #     my_adreq_list = my_adreq_list.filter(adsp__genre__in=qstr)

    if minrate > maxrate:
        print("incorrect rates")
        context['ferrors'].append(("Invalid rates. Min rate should"
                                   " be less than max rate"))

    my_adreq_list = my_adreq_list.filter(asking_rate__gte=
                                         minrate)

    my_adreq_list = my_adreq_list.filter(asking_rate__lte=
                                         maxrate)

    if not(context['ferrors']):
        temp = [my_adreq.adsp.all()[0] for my_adreq in my_adreq_list]
        ser = AdspaceSerializer(temp, many=True)
        context['adspaces'] = ser.data
        ser = RequestForAdvSerializer(my_adreq_list, many=True)
        context['adreqs'] = ser.data
        # context['my_both_list'] = zip(my_adreq_list,my_adsp_list)
        # context['my_adreq_list'] = my_adreq_list
        return response.Response(context)
    else:
        my_ad_list = Adspace.objects.all()
        context = {'my_ad_list': my_ad_list}
        return response.Response(context)

@api_view(["GET"])
def dashboard_stats(request):
    context = {}
    if(request.GET.get("userMode") and request.GET.get("currencyType") and request.GET.get("userName")):
        userMode = request.GET.get("userMode").lower()
        currencyType = request.GET.get("currencyType").lower()
        userName = request.GET.get("userName")
        currentAgent = Agent.objects.filter(user__username=userName)
        currentUser = currentAgent[0].user
        eqc_balance = currentAgent[0].e_balance
        xqc_balance = currentAgent[0].x_balance
        context["eqc_balance"]=eqc_balance
        context["xqc_balance"]=xqc_balance
        if( userMode == "publisher" ):
            user_stats_list = Stat.objects.filter(contract__adspace__publisher=currentUser,contract__currency=currencyType)
            today_stats = user_stats_list.filter(stat_date=datetime.date.today())
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

            month_stats = user_stats_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
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
            print("------------------------------------------------------------------")
            return response.Response(context)
            #print(dashboard_stats)
        elif( userMode.lower() == "advertiser" ):
            print(userMode.lower())
            user_stats_list = Stat.objects.filter(contract__ad__advertiser=currentUser,contract__currency=currencyType)
            today_stats = user_stats_list.filter(stat_date=datetime.date.today())
            if today_stats:
                nstats = len(today_stats)
                context['topstat_clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
                context['topstat_impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            else:
                context['topstat_clicks_today'] = 0
                context['topstat_impressions_today'] = 0
            month_stats = user_stats_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
            if month_stats:
                nstats = len(month_stats)
                context['topstat_clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
                context['topstat_impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            else:
                context['topstat_clicks_30day'] = 0
                context['topstat_impressions_30day'] = 0
            return response.Response(context)

        else:
            print("Unknown mode specified")
    else:
        print("Incorrect parameters specified. What should I do now?")
        return response.Response({"error":"Incorrect parameters specified"})

    return response.Response({"j":"jetti"})


@api_view(["GET","POST"])
def login3210(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if not user:
        return response.Response({"error": "Login failed"})

    token, _ = Token.objects.get_or_create(user=user)
    return response.Response({"token": token.key})
#    return response.Response({"j":"jetti"})

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
        print(context)
        context['my_adreq_list'] = my_adreq_list
        if not(context['ferrors']):
            context['my_both_list'] = zip(my_adreq_list,my_adsp_list)
            context['my_adreq_list'] = my_adreq_list
        return response.Response(context)
    else:
        form = RequestForm()
        my_ad_list = Adspace.objects.all()
        context = {'my_ad_list': my_ad_list}
        return response.Response(context)
        # print("Got 2 list function")
        # # TODO: FILTER BY PREFERENCES
        # return render(request, 'marketplace_ad.html', context)

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
        serializer = AdspaceSerializer(my_adsp_list, many=True)
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
@authentication_classes((TokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated, ))
def testview0(request, format=None):
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


@api_view(["GET"])
def dashboard_charts(request):
    if(request.GET.get("userMode") and request.GET.get("currencyType") and request.GET.get("userName")):
        userMode = request.GET.get("userMode")
        currencyType = request.GET.get("currencyType")
        userName = request.GET.get("userName")
        currentAgent = Agent.objects.filter(user__username=userName)
        currentUser = currentAgent[0].user
        context = {}
        if( userMode.lower() == "publisher" ):
            my_stat_list = Stat.objects.filter(contract__adspace__publisher=currentUser,contract__currency=currencyType.lower())
            my_cont_list = Contract.objects.filter(adspace__publisher=currentUser,
                                                   currency=currencyType.lower())
            my_adsp_list = Adspace.objects.filter(publisher=currentUser)

            # Times
            # set retrieves unique elements, no internal oredering
            # cast to list again, because list is convenient.
            times = list(set([int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]))
            times2 = list(set([a_stat.stat_date for a_stat in my_stat_list]))
            ## SHIVA: Don't know which format you want time in, replace times with
            ## times2 in the next line if needed. Seems like times is more versatile
            ## and can be converted to other formats in front end as was happening
            ## earlier. Times2 is more restricted but is hard to transform.
            print(times2)
            # sort by ascending order
            context['c1_x'] = sorted(times)

            # array with zeros
            temp = [0]*len(my_adsp_list)
            # Find top 5 that are nonzero
            #enum gives index (loop var) and objects
            for ind1,an_adsp in enumerate(my_adsp_list):
                related_cont_list = my_cont_list.filter(adspace=an_adsp)
                for a_cont in related_cont_list:
                    related_stat_list = my_stat_list.filter(contract=a_cont)
                    for a_stat in related_stat_list:
                        # Lists have .index() which returns index of elem in brackets
                        # ['a','b','c'].index('b') -> 1
                        # time_index = times2.index(a_stat.stat_date)
                        temp[ind1]+=float(a_stat.revenue)
            print(temp)
            # From list of all adspace revenues, get indices of top 5 adspaces
            # [13,11,12] -> np.sort() will give [11,12,13]
            # np.argsort gives [2,0,1]
            # [-5:] return last 5 elements (e.g, 10,20,30,40,50)
            # reversed will make it (50,40,30,20,10)
            chosen_inds = list(reversed(np.argsort(temp)[-5:]))
            print("Chosen indices are : ", chosen_inds)
            adspno = 0
            context['c1_y_revenue'],context['c1_y_clicks'] = [], []
            context['c1_y_impressions'],context['c1_y_rpm'] = [], []
            # choseninds is a list of indices of top5 adspaces in descending order
            for ind1 in range(len(chosen_inds)):
                # Find all contracts with this adspace, and get all the stats for
                # those contracts and sum. Should do all the revenue sums and then add
                # only the top 5 to the list.
                an_adsp = my_adsp_list[chosen_inds[ind1]]
                # revenue0 is the list of y values for the top contract
                context['c1_y_revenue'].append({'data': [0]*len(times), 'label':an_adsp.name})
                context['c1_y_clicks'].append({'data': [0]*len(times), 'label':an_adsp.name})
                context['c1_y_impressions'].append({'data': [0]*len(times), 'label':an_adsp.name})
                context['c1_y_rpm'].append({'data': [0]*len(times), 'label':an_adsp.name})
                # context['c1_y_clicks'+str(ind1)] = {"data" : [0]*len(times)}
                # context['c1_y_impression'+str(ind1)] = [0]*len(times)
                # context['c1_y_rpm'+str(ind1)] = [0]*len(times)
                # context['c1_adspnames'].append(an_adsp.name)
                related_cont_list = my_cont_list.filter(adspace=an_adsp)
                for a_cont in related_cont_list:
                    related_stat_list = my_stat_list.filter(contract=a_cont)
                    related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                    for a_stat in related_stat_list:
                        time_index = times2.index(a_stat.stat_date)
                        context['c1_y_revenue'][ind1]["data"][time_index]+=float(a_stat.revenue)
                        context['c1_y_clicks'][ind1]["data"][time_index]+=float(a_stat.clicks)
                        context['c1_y_impressions'][ind1]["data"][time_index]+=float(a_stat.impressions)
                        context['c1_y_rpm'][ind1]["data"][time_index]+=float(a_stat.rpm)
                        # context['c1_y_impression'+str(ind1)][time_index]+=float(a_stat.impressions)
                        # context['c1_y_rpm'+str(ind1)][time_index]+=float(a_stat.rpm)
            # print(context['c1_adspnames'])

            xdata = []
            context['c2_y_weekrevenue'] = {"data":[0]*len(my_cont_list)}
            context['c2_y_day30revenue'] = {"data":[0]*len(my_cont_list)}
            context['c2_y_alltimerevenue'] = {"data":[0]*len(my_cont_list)}
            for ind in range(len(my_cont_list)):
                xdata.append(my_cont_list[ind].name)
                related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
                week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
                day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
                alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
                context['c2_y_weekrevenue']["data"][ind] = sum([a_stat.revenue for a_stat in week_list])
                context['c2_y_day30revenue']["data"][ind] = sum([a_stat.revenue for a_stat in day30_list])
                context['c2_y_alltimerevenue']["data"][ind] = sum([a_stat.revenue for a_stat in alltime_list])
                # In the front end, sum up the correct list, round to 0 places and display.
            context['c2_xdata'] = xdata
            print("------------------------------------------------------------------")
            return response.Response(context)

        elif( userMode.lower() == "advertiser" ):
            my_stat_list = Stat.objects.filter(contract__ad__advertiser=currentUser,contract__currency=currencyType.lower())
            my_cont_list = Contract.objects.filter(ad__advertiser=currentUser,
                                                   currency=currencyType.lower())
            my_ad_list = Ad.objects.filter(advertiser=currentUser)

            print("Ads : "+str(my_ad_list))
            print("Contracts : ", my_cont_list)
            print("Stats : ", my_stat_list)

            # Times
            times = list(set([int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]))
            times2 = list(set([a_stat.stat_date for a_stat in my_stat_list]))

            context['c1_x'] = sorted(times)
            print(context['c1_x'])
            context['c1_adnames'] = []
            temp = [0]*len(my_ad_list)
            # Find  top 5 ranked by no. of clicks
            for ind1,an_ad in enumerate(my_ad_list):
                related_cont_list = my_cont_list.filter(ad=an_ad)
                for a_cont in related_cont_list:
                    related_stat_list = my_stat_list.filter(contract=a_cont)
                    for a_stat in related_stat_list:
                        time_index = times2.index(a_stat.stat_date)
                        temp[ind1]+=float(a_stat.clicks)
            print(temp)
            chosen_inds = list(reversed(np.argsort(temp)[-5:]))
            print("Chosen indices are : ", chosen_inds)
            adspno = 0
            context['c1_y_clicks'] = []
            context['c1_y_impressions'],context['c1_y_rpm'] = [], []
            for ind1 in range(len(chosen_inds)):
                # Find all contracts with this ad, and get all the stats for
                # those contracts and sum. Should do all the clicks sums and then add
                # only the top 5 to the list.
                an_ad = my_ad_list[chosen_inds[ind1]]
                context['c1_y_clicks'].append({"data":[0]*len(times), 'label':an_ad.name})
                context['c1_y_impressions'].append({"data":[0]*len(times), 'label':an_ad.name})
                context['c1_adnames'].append(an_ad.name)
                related_cont_list = my_cont_list.filter(ad=an_ad)
                for a_cont in related_cont_list:
                    related_stat_list = my_stat_list.filter(contract=a_cont)
                    related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                    for a_stat in related_stat_list:
                        time_index = times2.index(a_stat.stat_date)
                        context['c1_y_clicks'][ind1]["data"][time_index]+=float(a_stat.clicks)
                        context['c1_y_impressions'][ind1]["data"][time_index]+=float(a_stat.impressions)
            print(context['c1_adnames'])


            xdata = []
            context['c2_y_weekclicks'] = {"data":[0]*len(my_cont_list)}
            context['c2_y_day30clicks'] = {"data":[0]*len(my_cont_list)}
            context['c2_y_alltimeclicks'] = {"data":[0]*len(my_cont_list)}
            for ind in range(len(my_cont_list)):
                xdata.append(my_cont_list[ind].name)
                related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
                week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
                day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
                alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
                context['c2_y_weekclicks']["data"][ind] = sum([a_stat.clicks for a_stat in week_list])
                context['c2_y_day30clicks']["data"][ind] = sum([a_stat.clicks for a_stat in day30_list])
                context['c2_y_alltimeclicks']["data"][ind] = sum([a_stat.clicks for a_stat in alltime_list])
                # In the front end, sum up the correct list, round to 0 places and display.
            context['c2_xdata'] = xdata
            return response.Response(context)
            print("------------------------------------------------------------------")

        else:
            print("Unknown mode specified")
    else:
        print("Incorrect parameters specified. What should I do now?")
        return response.Response({"error":"Incorrect parameters specified"})

    return response.Response({"j":"jetti"})

@api_view(['GET', 'POST'])
def pub_dashboard_charts(request):
    """
    Publisher dashboard to work with angular but componentized.
    """
    context = {}
    # print("User is  : ",request.user)
    ## TODO
    ## 1. Make this work with request.user (Django Sessions) - DONE
    ## 2. Fill up more data - DONE but more required
    ## 3. Add a balance and account number to the profile.
    ## 4. Verify filters and sent data when awake :D
    ## 5. Little green box - daily change should be calculated
    print("-----------------------------------------------------------------")
    if request.method=="POST":
        print("It was post")
        currency_tag = request.POST[u'currency']
        print("Currency is : ", type(request.POST[u'currency']))
    else:
        print("in charts It was not post")
    print("-------------------------------------------------------------------")
    currency_tag = "eqc"
    # try:
    # Publisher EQC =======================================================
    t = Agent.objects.all() # 1- team, 2 advertiser1, 3 is publisher1
    #python indexes from 0
    # returns a list

    my_stat_list = Stat.objects.filter(contract__adspace__publisher=t[2].user,
                                       contract__currency=currency_tag)
    # all of these are Python Lists
    # my_adsp_list = Adspace.objects.filter(publisher=request.user)
    # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
    # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
    print("Adspaces : "+str(my_adsp_list))
    print("Contracts : ", my_cont_list)
    # print("Stats : ", my_stat_list)


    # except:
    #     print("Failed somewhere in the body")
    #     context['ERROR'] = "Just"
    #     return response.Response(context)

@api_view(['GET', 'POST'])
def pub_dashboard_topstat(request):
    """
    Publisher dashboard to work with angular but componentized.
    """
    context = {}
    # print("User is  : ",request.user)
    ## TODO
    ## 1. Make this work with request.user (Django Sessions) - DONE
    ## 2. Fill up more data - DONE but more rec1quired
    ## 3. Add a balance and account number to the profile.
    ## 4. Verify filters and sent data when awake :D
    ## 5. Little green box - daily change should be calculated
    print("-----------------------------------------------------------------")
    if request.method=="POST":
        print("It was post")
        currency_tag = request.POST[u'currency']
        print("Currency is : ", type(request.POST[u'currency']))
    else:
        print("in topstat It was not post")
    print("-------------------------------------------------------------------")

    try:
        # Publisher EQC =======================================================
        t = Agent.objects.all() # 1- team, 2 advertiser1, 3 is publisher1
        # TODO : user request.user to get the right internal user instead of hardcoding.
        my_stat_list = Stat.objects.filter(contract__adspace__publisher=t[2].user,
                                           contract__currency=currency_tag)


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
        print("------------------------------------------------------------------")
        return response.Response(context)
    except:
        print("Failed somewhere in the body")
        context['ERROR'] = "Just"
        return response.Response(context)

@api_view(['GET', 'POST'])
def pub_dashboard_tables(request):
    """
    Publisher dashboard to work with angular but componentized.
    """
    context = {}
    # print("User is  : ",request.user)
    ## TODO
    ## 1. Make this work with request.user (Django Sessions) - DONE
    ## 2. Fill up more data - DONE but more required
    ## 3. Add a balance and account number to the profile.
    ## 4. Verify filters and sent data when awake :D
    ## 5. Little green box - daily change should be calculated
    print("-----------------------------------------------------------------")
    if request.method=="POST":
        print("It was post")
        currency_tag = request.POST[u'currency']
        print("Currency is : ", type(request.POST[u'currency']))
    else:
        print("in tables It was not post")
    print("-------------------------------------------------------------------")

    try:
        # Publisher EQC =======================================================
        t = Agent.objects.all() # 1- team, 2 advertiser1, 3 is publisher1
        #python indexes from 0
        # returns a list
        my_cont_list = Contract.objects.filter(adspace__publisher=t[2].user,
                                               currency=currency_tag)
        # filter out a subset of objects
        # if make change to models, do 'makemigations' and then 'migrate'
        # contract has adspace, adspace hath publisher
        # "" - basic STRING
        # u"" - unicode string
        my_adsp_list = Adspace.objects.filter(publisher=t[2].user)

        # all of these are Python Lists
        # my_adsp_list = Adspace.objects.filter(publisher=request.user)
        # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        print("Adspaces : "+str(my_adsp_list))
        print("Contracts : ", my_cont_list)
        # print("Stats : ", my_stat_list)

        ser = AdspaceSerializer(my_adsp_list, many=True)
        context['my_ad_list'] = ser.data
        # ser = ContractSerializer(my_cont_list, many=True)
        # context['my_cont_list'] = my_cont_list
        # short hand notation called 'List Comprehension'
        print(type(my_cont_list[0].ad.advertiser))
        context['t2_col1'] = [str(a_cont.ad.advertiser) for a_cont in my_cont_list]
        context['t2_col2'] = [a_cont.start_time.date() for a_cont in my_cont_list]
        context['t1_col1'] = [an_adsp.website.name for an_adsp in my_adsp_list]
        context['t1_col2'] = [an_adsp.adtype for an_adsp in my_adsp_list]
        context['t1_col3'] = [an_adsp.genre for an_adsp in my_adsp_list]
        # templist = []
        # for a_cont in my_cont_list:
        #     templist.append(a_cont.start_time)
        # return (templist)

        # templist = []
        # for contract_index in range(len(my_cont_list)):
        #     templist.append(my_cont_list[contract_index].start_time)
        # return (templist)


        return response.Response(context)
    except:
        print("Failed somewhere in the body")
        context['ERROR'] = "Just"
        return response.Response(context)


#@login_required
@api_view(['GET', 'POST'])
def pub_dashboard_ser(request):
    """
    Publisher dashboard.
    """
    context = {}
    print("Got to pub_dashboard_ser")
    # print("User is  : ",request.user)
    ## TODO
    ## 1. Make this work with request.user (Django Sessions) - DONE
    ## 2. Fill up more data - DONE but more required
    ## 3. Add a balance and account number to the profile.
    ## 4. Verify filters and sent data when awake :D
    ## 5. Little green box - daily change should be calculated

    try:
        # Publisher EQC =======================================================
        t = Agent.objects.all()
        my_cont_list = Contract.objects.filter(adspace__publisher=t[2].user,
                                               currency=u"eqc")
        my_adsp_list = Adspace.objects.filter(publisher=t[2].user)
        my_stat_list = Stat.objects.filter(contract__adspace__publisher=t[2].user)
        # my_adsp_list = Adspace.objects.filter(publisher=request.user)
        # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        print("Adspaces : "+str(my_adsp_list))
        print("Contracts : ", my_cont_list)
        # print("Stats : ", my_stat_list)

        ser = AdspaceSerializer(my_adsp_list, many=True)
        context['my_ad_list'] = ser.data
        # ser = ContractSerializer(my_cont_list, many=True)
        # context['my_cont_list'] = my_cont_list
        context['pe_t2_col1'] = [str(a_cont.ad.advertiser) for a_cont in my_cont_list]
        context['pe_t2_col2'] = [a_cont.start_time for a_cont in my_cont_list]

        # Times
        times = list(set([int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]))
        times2 = list(set([a_stat.stat_date for a_stat in my_stat_list]))
        ## SHIVA: Don't know which format you want time in, replace times with
        ## times2 in the next line if needed. Seems like times is more versatile
        ## and can be converted to other formats in front end as was happening
        ## earlier. Times2 is more restricted but is hard to transform.
        print(times2)
        context['pe_c1_x'] = sorted(times)
        context['pe_c1_adspnames'] = []
        temp = [0]*len(my_adsp_list)
        # Find top 5 that are nonzero
        for ind1,an_adsp in enumerate(my_adsp_list):
            related_cont_list = my_cont_list.filter(adspace=an_adsp)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    temp[ind1]+=float(a_stat.revenue)
        print(temp)
        chosen_inds = list(reversed(np.argsort(temp)[-5:]))
        print("Chosen indices are : ", chosen_inds)
        adspno = 0
        for ind1 in range(len(chosen_inds)):
            # Find all contracts with this adspace, and get all the stats for
            # those contracts and sum. Should do all the revenue sums and then add
            # only the top 5 to the list.
            an_adsp = my_adsp_list[chosen_inds[ind1]]
            context['pe_c1_y_revenue'+str(ind1)] = [0]*len(times)
            context['pe_c1_y_clicks'+str(ind1)] = [0]*len(times)
            context['pe_c1_y_impression'+str(ind1)] = [0]*len(times)
            context['pe_c1_y_rpm'+str(ind1)] = [0]*len(times)
            context['pe_c1_adspnames'].append(an_adsp.name)
            related_cont_list = my_cont_list.filter(adspace=an_adsp)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    context['pe_c1_y_revenue'+str(ind1)][time_index]+=float(a_stat.revenue)
                    context['pe_c1_y_clicks'+str(ind1)][time_index]+=float(a_stat.clicks)
                    context['pe_c1_y_impression'+str(ind1)][time_index]+=float(a_stat.impressions)
                    context['pe_c1_y_rpm'+str(ind1)][time_index]+=float(a_stat.rpm)
        print(context['pe_c1_adspnames'])
        today_stats = my_stat_list.filter(stat_date=datetime.date.today())
        if today_stats:
            nstats = len(today_stats)
            context['pe_topstat_revenue_today'] = round(sum([today_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['pe_topstat_clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
            context['pe_topstat_impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            context['pe_topstat_rpm_today'] = round(sum([today_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['pe_topstat_revenue_today'] = 0
            context['pe_topstat_clicks_today'] = 0
            context['pe_topstat_impressions_today'] = 0
            context['pe_topstat_rpm_today'] = 0

        month_stats = my_stat_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
        if month_stats:
            nstats = len(month_stats)
            context['pe_topstat_revenue_30day'] = round(sum([month_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['pe_topstat_clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
            context['pe_topstat_impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            context['pe_topstat_rpm_30day'] =  round(sum([month_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['pe_topstat_revenue_30day'] = 0
            context['pe_topstat_clicks_30day'] = 0
            context['pe_topstat_impressions_30day'] = 0
            context['pe_topstat_rpm_30day'] = 0

        xdata = []
        context['pe_c2_y_weekrevenue'] = [0]*len(my_cont_list)
        context['pe_c2_y_day30revenue'] = [0]*len(my_cont_list)
        context['pe_c2_y_alltimerevenue'] = [0]*len(my_cont_list)
        for ind in range(len(my_cont_list)):
            xdata.append(my_cont_list[ind].name)
            related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
            week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
            day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
            alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
            context['pe_c2_y_weekrevenue'][ind] = sum([a_stat.revenue for a_stat in week_list])
            context['pe_c2_y_day30revenue'][ind] = sum([a_stat.revenue for a_stat in day30_list])
            context['pe_c2_y_alltimerevenue'][ind] = sum([a_stat.revenue for a_stat in alltime_list])
            # In the front end, sum up the correct list, round to 0 places and display.
        context['pe_c2_xdata'] = xdata
        print("------------------------------------------------------------------")
        # Publisher XQC =======================================================
        t = Agent.objects.all()
        my_cont_list = Contract.objects.filter(adspace__publisher=t[2].user,
                                               currency=u"xqc")
        # my_adsp_list = Adspace.objects.filter(publisher=t[2].user)
        my_stat_list = Stat.objects.filter(contract__adspace__publisher=t[2].user)
        # my_adsp_list = Adspace.objects.filter(publisher=request.user)
        # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        print("Adspaces : "+str(my_adsp_list))
        print("Contracts : ", my_cont_list)
        # print("Stats : ", my_stat_list)

        ser = AdspaceSerializer(my_adsp_list, many=True)
        context['my_adsp_list'] = ser.data
        # ser = ContractSerializer(my_cont_list, many=True)
        # context['my_cont_list'] = my_cont_list
        context['px_t2_col1'] = [str(a_cont.ad.advertiser) for a_cont in my_cont_list]
        context['px_t2_col2'] = [a_cont.start_time for a_cont in my_cont_list]

        # Times
        times = list(set([int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]))
        times2 = list(set([a_stat.stat_date for a_stat in my_stat_list]))
        ## SHIVA: Don't know which format you want time in, replace times with
        ## times2 in the next line if needed. Seems like times is more versatile
        ## and can be converted to other formats in front end as was happening
        ## earlier. Times2 is more restricted but is hard to transform.
        print(times2)
        context['px_c1_x'] = sorted(times)
        context['px_c1_adspnames'] = []
        temp = [0]*len(my_adsp_list)
        # Find top 5 that are nonzero
        for ind1,an_adsp in enumerate(my_adsp_list):
            related_cont_list = my_cont_list.filter(adspace=an_adsp)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    temp[ind1]+=float(a_stat.revenue)
        print(temp)
        chosen_inds = list(reversed(np.argsort(temp)[-5:]))
        print("Chosen indices are : ", chosen_inds)
        adspno = 0
        for ind1 in range(len(chosen_inds)):
            # Find all contracts with this adspace, and get all the stats for
            # those contracts and sum. Should do all the revenue sums and then add
            # only the top 5 to the list.
            an_adsp = my_adsp_list[chosen_inds[ind1]]
            context['px_c1_y_revenue'+str(ind1)] = [0]*len(times)
            context['px_c1_y_clicks'+str(ind1)] = [0]*len(times)
            context['px_c1_y_impression'+str(ind1)] = [0]*len(times)
            context['px_c1_y_rpm'+str(ind1)] = [0]*len(times)
            context['px_c1_adspnames'].append(an_adsp.name)
            related_cont_list = my_cont_list.filter(adspace=an_adsp)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    context['px_c1_y_revenue'+str(ind1)][time_index]+=float(a_stat.revenue)
                    context['px_c1_y_clicks'+str(ind1)][time_index]+=float(a_stat.clicks)
                    context['px_c1_y_impression'+str(ind1)][time_index]+=float(a_stat.impressions)
                    context['px_c1_y_rpm'+str(ind1)][time_index]+=float(a_stat.rpm)
        print(context['px_c1_adspnames'])
        today_stats = my_stat_list.filter(stat_date=datetime.date.today())
        if today_stats:
            nstats = len(today_stats)
            context['px_topstat_revenue_today'] = round(sum([today_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['px_topstat_clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
            context['px_topstat_impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            context['px_topstat_rpm_today'] = round(sum([today_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['px_topstat_revenue_today'] = 0
            context['px_topstat_clicks_today'] = 0
            context['px_topstat_impressions_today'] = 0
            context['px_topstat_rpm_today'] = 0

        month_stats = my_stat_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
        if month_stats:
            nstats = len(month_stats)
            context['px_topstat_revenue_30day'] = round(sum([month_stats[ind].revenue for ind in range(nstats)])/nstats,8)
            context['px_topstat_clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
            context['px_topstat_impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            context['px_topstat_rpm_30day'] =  round(sum([month_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['px_topstat_revenue_30day'] = 0
            context['px_topstat_clicks_30day'] = 0
            context['px_topstat_impressions_30day'] = 0
            context['px_topstat_rpm_30day'] = 0

        xdata = []
        context['px_c2_y_weekrevenue'] = [0]*len(my_cont_list)
        context['px_c2_y_day30revenue'] = [0]*len(my_cont_list)
        context['px_c2_y_alltimerevenue'] = [0]*len(my_cont_list)
        for ind in range(len(my_cont_list)):
            xdata.append(my_cont_list[ind].name)
            related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
            week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
            day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
            alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
            context['px_c2_y_weekrevenue'][ind] = sum([a_stat.revenue for a_stat in week_list])
            context['px_c2_y_day30revenue'][ind] = sum([a_stat.revenue for a_stat in day30_list])
            context['px_c2_y_alltimerevenue'][ind] = sum([a_stat.revenue for a_stat in alltime_list])
            # In the front end, sum up the correct list, round to 0 places and display.
        context['px_c2_xdata'] = xdata
        print("------------------------------------------------------------------")


        # # Advertiser EQC =======================================================
        t = Agent.objects.all()
        my_cont_list = Contract.objects.filter(ad__advertiser=t[1].user,
                                               currency=u"eqc")
        my_ad_list = Ad.objects.filter(advertiser=t[1].user)
        my_stat_list = Stat.objects.filter(contract__ad__advertiser=t[1].user)
        # my_adsp_list = Adspace.objects.filter(publisher=request.user)
        # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        print("Ads : "+str(my_ad_list))
        print("Contracts : ", my_cont_list)
        print("Stats : ", my_stat_list)

        ser = AdSerializer(my_ad_list, many=True)
        context['my_ad_list'] = ser.data
        context['ae_t2_col1'] = [str(a_cont.ad.advertiser) for a_cont in my_cont_list]
        context['ae_t2_col2'] = [a_cont.start_time for a_cont in my_cont_list]

        # Times
        times = list(set([int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]))
        times2 = list(set([a_stat.stat_date for a_stat in my_stat_list]))
        print(times2)
        context['ae_c1_x'] = sorted(times)
        context['ae_c1_adnames'] = []
        temp = [0]*len(my_adsp_list)
        # Find top 5 ranked by no. of clicks
        for ind1,an_ad in enumerate(my_ad_list):
            related_cont_list = my_cont_list.filter(ad=an_ad)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    temp[ind1]+=float(a_stat.clicks)
        print(temp)
        chosen_inds = list(reversed(np.argsort(temp)[-5:]))
        print("Chosen indices are : ", chosen_inds)
        adspno = 0
        for ind1 in range(len(chosen_inds)):
            # Find all contracts with this ad, and get all the stats for
            # those contracts and sum. Should do all the clicks sums and then add
            # only the top 5 to the list.
            an_adsp = my_ad_list[chosen_inds[ind1]]
            context['ae_c1_y_clicks'+str(ind1)] = [0]*len(times)
            context['ae_c1_y_impression'+str(ind1)] = [0]*len(times)
            # context['ae_c1_y_rpm'+str(ind1)] = [0]*len(times)
            context['ae_c1_adnames'].append(an_ad.name)
            related_cont_list = my_cont_list.filter(ad=an_ad)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    context['ae_c1_y_clicks'+str(ind1)][time_index]+=float(a_stat.clicks)
                    context['ae_c1_y_impression'+str(ind1)][time_index]+=float(a_stat.impressions)
                    # context['ae_c1_y_rpm'+str(ind1)][time_index]+=float(a_stat.rpm)
        print(context['ae_c1_adnames'])
        today_stats = my_stat_list.filter(stat_date=datetime.date.today())
        if today_stats:
            nstats = len(today_stats)
            context['ae_topstat_clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
            context['ae_topstat_impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            # context['ae_topstat_rpm_today'] = round(sum([today_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['ae_topstat_clicks_today'] = 0
            context['ae_topstat_impressions_today'] = 0
            # context['ae_topstat_rpm_today'] = 0

        month_stats = my_stat_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
        if month_stats:
            nstats = len(month_stats)
            context['ae_topstat_clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
            context['ae_topstat_impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            # context['ae_topstat_rpm_30day'] =  round(sum([month_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['ae_topstat_clicks_30day'] = 0
            context['ae_topstat_impressions_30day'] = 0
            # context['ae_topstat_rpm_30day'] = 0

        xdata = []
        context['ae_c2_y_weekclicks'] = [0]*len(my_cont_list)
        context['ae_c2_y_day30clicks'] = [0]*len(my_cont_list)
        context['ae_c2_y_alltimeclicks'] = [0]*len(my_cont_list)
        for ind in range(len(my_cont_list)):
            xdata.append(my_cont_list[ind].name)
            related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
            week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
            day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
            alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
            context['ae_c2_y_weekclicks'][ind] = sum([a_stat.clicks for a_stat in week_list])
            context['ae_c2_y_day30clicks'][ind] = sum([a_stat.clicks for a_stat in day30_list])
            context['ae_c2_y_alltimeclicks'][ind] = sum([a_stat.clicks for a_stat in alltime_list])
            # In the front end, sum up the correct list, round to 0 places and display.
        context['ae_c2_xdata'] = xdata
        print("------------------------------------------------------------------")


        # # Advertiser XQC =======================================================
        t = Agent.objects.all()
        my_cont_list = Contract.objects.filter(ad__advertiser=t[1].user,
                                               currency=u"xqc")
        my_ad_list = Ad.objects.filter(advertiser=t[1].user)
        my_stat_list = Stat.objects.filter(contract__ad__advertiser=t[1].user)
        # my_adsp_list = Adspace.objects.filter(publisher=request.user)
        # my_cont_list = Contract.objects.filter(adspace__publisher=request.user)
        # my_stat_list = Stat.objects.filter(contract__adspace__publisher=request.user)
        print("Ads : "+str(my_ad_list))
        print("Contracts : ", my_cont_list)
        print("Stats : ", my_stat_list)

        ser = AdSerializer(my_ad_list, many=True)
        context['my_ad_list'] = ser.data
        context['ae_t2_col1'] = [str(a_cont.ad.advertiser) for a_cont in my_cont_list]
        context['ae_t2_col2'] = [a_cont.start_time for a_cont in my_cont_list]

        # Times
        times = list(set([int(time.mktime(a_stat.stat_date.timetuple())*1000) for a_stat in my_stat_list]))
        times2 = list(set([a_stat.stat_date for a_stat in my_stat_list]))
        print(times2)
        context['ax_c1_x'] = sorted(times)
        context['ax_c1_adnames'] = []
        temp = [0]*len(my_adsp_list)
        # Find top 5 ranked by no. of clicks
        for ind1,an_ad in enumerate(my_ad_list):
            related_cont_list = my_cont_list.filter(ad=an_ad)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    temp[ind1]+=float(a_stat.clicks)
        print(temp)
        chosen_inds = list(reversed(np.argsort(temp)[-5:]))
        print("Chosen indices are : ", chosen_inds)
        adspno = 0
        for ind1 in range(len(chosen_inds)):
            # Find all contracts with this ad, and get all the stats for
            # those contracts and sum. Should do all the clicks sums and then add
            # only the top 5 to the list.
            an_adsp = my_ad_list[chosen_inds[ind1]]
            context['ax_c1_y_clicks'+str(ind1)] = [0]*len(times)
            context['ax_c1_y_impression'+str(ind1)] = [0]*len(times)
            # context['ax_c1_y_rpm'+str(ind1)] = [0]*len(times)
            context['ax_c1_adnames'].append(an_ad.name)
            related_cont_list = my_cont_list.filter(ad=an_ad)
            for a_cont in related_cont_list:
                related_stat_list = my_stat_list.filter(contract=a_cont)
                related_stat_list = sorted(related_stat_list, key= lambda a_stat: a_stat.stat_date)
                for a_stat in related_stat_list:
                    time_index = times2.index(a_stat.stat_date)
                    context['ax_c1_y_clicks'+str(ind1)][time_index]+=float(a_stat.clicks)
                    context['ax_c1_y_impression'+str(ind1)][time_index]+=float(a_stat.impressions)
                    # context['ax_c1_y_rpm'+str(ind1)][time_index]+=float(a_stat.rpm)
        print(context['ax_c1_adnames'])
        today_stats = my_stat_list.filter(stat_date=datetime.date.today())
        if today_stats:
            nstats = len(today_stats)
            context['ax_topstat_clicks_today'] = round(sum([today_stats[ind].clicks for ind in range(nstats)])/nstats,8)
            context['ax_topstat_impressions_today'] = round(sum([today_stats[ind].impressions for ind in range(nstats)])/nstats,8)
            # context['ax_topstat_rpm_today'] = round(sum([today_stats[ind].rpm for ind in range(nstats)])/nstats,8)
            context['ax_topstat_impressions_30day'] = 0
        else:
            context['ax_topstat_clicks_today'] = 0
            context['ax_topstat_impressions_today'] = 0
            # context['ax_topstat_rpm_today'] = 0

        month_stats = my_stat_list.filter(stat_date__gte=datetime.date.today()-datetime.timedelta(30))
        if month_stats:
            nstats = len(month_stats)
            context['ax_topstat_clicks_30day'] =  round(sum([month_stats[ind].clicks for ind in range(nstats)])/nstats,0)
            context['ax_topstat_impressions_30day'] =  round(sum([month_stats[ind].impressions for ind in range(nstats)])/nstats,0)
            # context['ax_topstat_rpm_30day'] =  round(sum([month_stats[ind].rpm for ind in range(nstats)])/nstats,8)
        else:
            context['ax_topstat_clicks_30day'] = 0
            # context['ax_topstat_rpm_30day'] = 0

        xdata = []
        context['ax_c2_y_weekclicks'] = [0]*len(my_cont_list)
        context['ax_c2_y_day30clicks'] = [0]*len(my_cont_list)
        context['ax_c2_y_alltimeclicks'] = [0]*len(my_cont_list)
        for ind in range(len(my_cont_list)):
            xdata.append(my_cont_list[ind].name)
            related_stat_list = my_stat_list.filter(contract=my_cont_list[ind])
            week_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-7))
            day30_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-30))
            alltime_list = related_stat_list.filter(stat_date__gte=datetime.date.today()+datetime.timedelta(-10000))
            context['ax_c2_y_weekclicks'][ind] = sum([a_stat.clicks for a_stat in week_list])
            context['ax_c2_y_day30clicks'][ind] = sum([a_stat.clicks for a_stat in day30_list])
            context['ax_c2_y_alltimeclicks'][ind] = sum([a_stat.clicks for a_stat in alltime_list])
            # In the front end, sum up the correct list, round to 0 places and display.
        context['ax_c2_xdata'] = xdata
        print("------------------------------------------------------------------")

    except Adspace.DoesNotExist:
        context['is_error'] = "No adspaces found"

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
