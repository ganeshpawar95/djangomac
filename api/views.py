from django.shortcuts import render,redirect
from django.shortcuts import render
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi
from django.views import View
from django.http import HttpResponse
from rest_framework import status

from facebook_business.api import FacebookAdsApi

from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.generics import RetrieveDestroyAPIView
from .models import Post, Adset, AdsetOrignal,Adset_updte_hours
from .serializers import UserRegistrationSerializer, UserLoginSerializer, TokenSerializer
from django.http import JsonResponse
import json
# from datetime import datetime
from datetime import date
import dateutil.parser as parser
import datetime
from datetime import datetime

import pytz

utc = pytz.utc


def campaign(request):
	return render(request,'index.html')


class UserRegistrationAPIView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)
        data = serializer.data
        data["token"] = token.key

        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class UserLoginAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                data=TokenSerializer(token).data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserTokenAPIView(RetrieveDestroyAPIView):
    lookup_field = "key"
    serializer_class = TokenSerializer
    queryset = Token.objects.all()

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user)

    def retrieve(self, request, key, *args, **kwargs):
        if key == "current":
            instance = Token.objects.get(key=request.auth.key)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return super(UserTokenAPIView, self).retrieve(request, key, *args, **kwargs)

    def destroy(self, request, key, *args, **kwargs):
        if key == "current":
            Token.objects.get(key=request.auth.key).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return super(UserTokenAPIView, self).destroy(request, key, *args, **kwargs)



@api_view(['GET'])
def removebg(request):
	if request.method=='GET':
		access_token=request.headers['token']
		adds=[]
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		# id = 'act_2770121319724389'
		id = 'act_' + request.GET.get('userId')
		FacebookAdsApi.init(access_token=access_token)

		fields = [
		  'name',
		  'objective',
		]
		params = {
		  'effective_status': ['ACTIVE','PAUSED'],
		}
		add=AdAccount(id).get_campaigns(
		  fields=fields,
		  params=params)
		data1=[]
		for i in add:
			data={
			'id':i['id'],
			'name':i['name']
			}
			data1.append(data)
		print(data1)

		return JsonResponse(data1, safe=False)
	else:
		return HttpResponse('not found')


@api_view(['GET'])
def getadset(request):
	if request.method == 'GET':
		access_token=request.headers['token']
		campaignId = request.GET.get('campaignId')

		# userId = request.GET.get('userId')
		# id = 'act_2770121319724389'
		print(access_token)
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		CAMPAIGN_ID = campaignId
		FacebookAdsApi.init(access_token=access_token)
		fields = ['name','start_time','end_time','targeting']
		data1=[]
		params = {}
		ads= Campaign(CAMPAIGN_ID).get_ad_sets(
	    	fields=fields,
	    	params=params,
	    	)
		for i in ads:
			orginalid=i['id']
			start_time=i['start_time']
			end_time=i['end_time']
			targetings=i['targeting']
			print(orginalid)
			try:
				print('---------------exit')
				gets=AdsetOrignal.objects.filter(id=orginalid)
				print('>>>>>>>>',gets)
				if list(gets) != []:
					gets = gets[0]
					#updte data in database
					AdsetOrignal.objects.filter(id=orginalid).update(start_time=start_time,end_time=end_time)
				else:
					print('not in db')
			except AdsetOrignal.DoesNotExist:
				AdsetOrignal.objects.create(id=orginalid,start_time=start_time,end_time=end_time,targeting=targetings)
				print('---------------------not exit')
			data={
			'id':i['id'],
			'name':i['name'],
			'start_time':i['start_time'],
			'end_time':i['end_time'],
			'targeting':i['targeting'],
			}
			data1.append(data)
		today = datetime.now(tz=utc)
		#end date then update adset orginal locations
		print('----------------today',today)
		for i in data1:
			ids=i['id']
			orignallocation= AdsetOrignal.objects.filter(id=ids)
			adsts=Adset.objects.filter(id=ids)
			for i in adsts:
				end_times=i.end_time
				if end_times<= today:
					for orignallo in orignallocation:
						targeting=orignallo.targeting
						fields = ['targeting']
						params = {'targeting':targeting}
						AdSet(ids).api_update(fields=fields,params=params,)
						print('change orignal location adset',ids)
						Adset.objects.filter(id=ids).delete()
				else:
					print('end date is greter today date')
		#end code enddate update addset location
        # updte add set locaions usegin start date time
		for i in data1:
		  ids=i['id']
		  adsts=Adset.objects.filter(id=ids)
		  for i in adsts:
		  	start_times=i.start_time
		  	targeting=i.targeting
		  	print('start_time-----',start_times)
		  	if start_times <= today:
		  		fields = ['targeting']
		  		params = targeting
		  		print(params)
		  		AdSet(ids).api_update(fields=fields,params=params,)
		  		print('updte  location adset',ids)
		  	else:
		  		print('start_time is greter today date')
		#end code update adset
		return Response(data1)
	else:
		return HttpResponse('not found')


@api_view(['GET'])
def create_adset(request):
	if request.method == 'GET':
		access_token=request.headers['token']
		campaignId = request.GET.get('campignId')

		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		id = 'act_2770121319724389'
		CAMPAIGN_ID = campaignId
		FacebookAdsApi.init(access_token=access_token)
		fields = []
		params = {
		  'name': 'My Reach Ad Set',
		  'optimization_goal': 'REACH',
		  'billing_event': 'IMPRESSIONS',
		  'end_time': '2020-5-19T23:43:36-0800',
		  'bid_amount': '2',
		  'daily_budget': 20979,
		  'campaign_id': '23844605998330207',
		  'status': 'PAUSED',
		  'targeting': {'facebook_positions':['feed'],'geo_locations':{'countries':['IN']},'user_os':['iOS']},
		}
		adsets= AdAccount(id).create_ad_set(
		  fields=fields,
		  params=params,
		)
		return Response(adsets)
	else:
		return HttpResponse('not found')


@api_view(['GET'])
def get_adset_by_id(request):
	if request.method == 'GET':
		access_token=request.headers['token']

		adsetId = request.GET.get('adsetId')
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		ADSET_ID = adsetId
		FacebookAdsApi.init(access_token=access_token)
		fields = ['name','start_time','end_time','targeting']
		params = {}
		ad_set = AdSet(ADSET_ID).api_get(
                fields=fields,
                params=params,
            )
		print(ad_set)
		return Response(ad_set)
	else:
		return HttpResponse('not found')


@api_view(['POST'])
def update_ad_set_date(request):
	if request.method == 'POST':
		print('----------------------------------')
		access_token=request.headers['token']

		received_json_data = json.loads(request.body)
		endDate = received_json_data['end_time']
		startDate = received_json_data['start_time']
		print('-----------' + endDate)
		adsetId = request.GET.get('adsetId')
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		ADSET_ID = adsetId
		FacebookAdsApi.init(access_token=access_token)
		fields = ['start_time','end_time']
		print('><><>>',fields)
		params = {
			'start_time':startDate,
			'end_time':endDate,
		}
		updateadset= AdSet(ADSET_ID).api_update(
				fields=fields,
				params=params,
				)
		print(updateadset)
		return Response(updateadset)
	else:
		return HttpResponse('not found')


@api_view(['POST'])
def update_ad_set_targeting(request):
	if request.method == 'POST':
		print('----------------------------------')
		access_token=request.headers['token']
		received_json_data = json.loads(request.body)
		latitude = received_json_data['lati']
		latitude = float(latitude)
		print(latitude)
		longitude = received_json_data['long']
		longitude = float(longitude)
		print(longitude)
		adsetId = request.GET.get('adsetId')
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		ADSET_ID = adsetId
		FacebookAdsApi.init(access_token=access_token)
		fields = ['targeting']
		print(fields)
		params = {
		'targeting': {'geo_locations':{'custom_locations':[
          {
            "radius":30,
            "latitude":latitude,
            "longitude":longitude
         }]},},
		}
		updateadset= AdSet(ADSET_ID).api_update(
				fields=fields,
				params=params,
				)
		print(updateadset)
		return Response(updateadset)
	else:
		return HttpResponse('not found')


@api_view(['POST'])
def update_ad_set_data(request):
	if request.method == 'POST':
		print('----------------------------------')
		access_token=request.headers['token']
		received_json_data = json.loads(request.body)
		print('ddddddata ',received_json_data)


		end_time = received_json_data['end_time']
		start_time = received_json_data['start_time']

		latitude = received_json_data['location']['lati']
		latitude = float(latitude)

		longitude = received_json_data['location']['long']
		longitude = float(longitude)

		adsetId = request.GET.get('adsetId')
		targetings={'targeting': {'geo_locations':{'custom_locations':[
	        	{
	            "radius":30,
	            "latitude":latitude,
	            "longitude":longitude
	        }]},},
	        }
		try:
			print('---------------exit')
			gets=Adset.objects.get(id=adsetId)
			if gets:
				Adset.objects.filter(id=adsetId).update(start_time=start_time,end_time=end_time)
			else:
				print('not in db')
		except Adset.DoesNotExist:
			scrapped_url = Adset.objects.create(id=adsetId,start_time=start_time,end_time=end_time,targeting=targetings)
		return Response('adset update set in database')
	else:
		return HttpResponse('not found')


@api_view(['GET'])
def updated_adset(request):
	if request.method=='GET':
		access_token=request.headers['token']

		adsetid = request.GET.get('adsetId')
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		ADSET_ID = adsetid
		data1=[]
		gets=Adset.objects.filter(id=adsetid)
		for i in gets:
			data={
				'id':i.id,
				'start_time':i.start_time,
				'end_time':i.end_time,
				'targeting':i.targeting,
			}
			data1.append(data)
		return Response(data1)
	else:
		return HttpResponse('not found')


@api_view(['GET'])
def update_ad_pr_one_hours(request):
	print('Testing Update')



@api_view(['POST'])
def update_ad_set_mylocations(request):
	if request.method == 'POST':
		print('----------------------------------')
		access_token=request.headers['token']
		received_json_data = json.loads(request.body)
		print('ddddddata ',received_json_data)
		end_time = received_json_data['end_time']
		start_time = received_json_data['start_time']
		latitude = received_json_data['location']['lati']
		latitude = float(latitude)
		longitude = received_json_data['location']['long']
		longitude = float(longitude)
		adsetId = request.GET.get('adsetId')
		user_id=received_json_data['user_id']
		app_secret = 'db4b3037cd105cfd23b6032aecd2c3ff'
		app_id = '263805807945856'
		id = 'act_2770121319724389'
		# adsetId=23844754263620207
		# start_time='2020-07-06 23:33:00'
		# end_time='2020-08-06 23:33:00'
		targetings={'targeting': {'geo_locations':{'custom_locations':[  
	        	{  
	            "radius":30,
	            "latitude":latitude,
	            "longitude":longitude
	        }]},},}
		# user_id=121
		access_token='EAAHIb6WDZBIYBALkhpdevyb25DqUAj7C53KWNT9nWQ6o4pnIKcblMHx9HqHj0UjMisw9lJdxW8jE2hyGZCAmXFPZA0OEqT6Bmh7aa6sMhTtmn8k2U9yauf7PTfUPbkFkZB7LCg2j72FZC34XJrOFKcAHyu1HaGZADQk5hAlamXDuZCR5ucX3owyTcdCcwXaZAIWZBknaSYkSecAZDZD'
		FacebookAdsApi.init(access_token=access_token)
		fields = ['start_time','end_time']
		params = {
			# 'start_time':start_time,
			'end_time':'2020-07-06 23:33:00',
			'targeting': {'geo_locations':{'custom_locations':[  
	        	{  
	            "radius":30,
	            "latitude":latitude,
	            "longitude":longitude
	        }]},},
	        
		}
		try:
				print('---------------exit')
				gets=Adset_updte_hours.objects.filter(id=adsetId)
				if list(gets) != []:
					gets = gets[0]
					#updte data in database
					print('updte ad set')
					Adset_updte_hours.objects.filter(id=adsetId).update(start_time=start_time,end_time=end_time,targeting=targetings,access_token=access_token,user_id=user_id)
				else:
					print('created ad set')
					Adset_updte_hours.objects.create(id=adsetId,start_time=start_time,end_time=end_time,access_token=access_token,targeting=targetings,user_id=user_id)
		except Adset_updte_hours.DoesNotExist:
				Adset_updte_hours.objects.create(id=adsetId,start_time=start_time,end_time=end_time,targeting=targetings,access_token=access_token,user_id=user_id)
				print('---------------------create')
		updateadset= AdSet(adsetId).api_update(
				fields=fields,
				params=params,
				)
		return Response({'status':'True','message':'adset update set in 1 hours'})
	else:
		return HttpResponse('not found')
