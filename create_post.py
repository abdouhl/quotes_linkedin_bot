import json
import random
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
from supabase import create_client, Client
import urllib.request

load_dotenv(join(dirname(__file__), '.env'))

access_token = os.environ.get("QUOTES_LINKEDIN_BOT_ACCESS_TOKEN")

api_url_base = 'https://api.linkedin.com/v2/'

URN= os.environ.get("QUOTES_LINKEDIN_BOT_URN")

headers = {'X-Restli-Protocol-Version': '2.0.0',
           'Content-Type': 'application/json',
           'Authorization': f'Bearer {access_token}'}


supabase: Client = create_client(os.environ.get("SUPABASE_URL"),os.environ.get("SUPABASE_KEY"))

quote_kkey = random.choice(range(0,200000))

data =supabase.table("quotes").select('*').eq('lang','en').range(quote_kkey,quote_kkey+1).execute().data

quote_text = data[0]['text']
author_name = data[0]['username']
quote_key = data[0]['key']
auth_tag = author_name.lower()
quote_image_link = os.environ.get("URLL")+str(quote_key)
quote_link = "https://www.quotesandsayings.net/quotes/"+author_name

text_tags = f'#{auth_tag} #quotes #quotesandsayings #motivation #inspiration #sayings #quote #quoteoftheday'

def post_on_linkedin():
	api_url = 'https://api.linkedin.com/v2/assets?action=registerUpload'

	post_data = {
	   "registerUploadRequest":{
		  "owner":URN,
		  "recipes":[
		     "urn:li:digitalmediaRecipe:feedshare-image"
		  ],
		  "serviceRelationships":[
		     {
		        "identifier":"urn:li:userGeneratedContent",
		        "relationshipType":"OWNER"
		     }
		  ],
		  "supportedUploadMechanism":[
		     "SYNCHRONOUS_UPLOAD"
		  ]
	   }
	}

	response = requests.post(api_url, headers=headers, json=post_data)

	uploadurl = response.json()['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
	imageurn = response.json()['value']['asset'].replace('digitalmediaAsset','image')
	opener=urllib.request.build_opener()
	opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
	urllib.request.install_opener(opener)

	# setting filename and image URL 
	filename =  join(dirname(__file__),'og_card_image.png')
	product_img_url = quote_image_link

	# calling urlretrieve function to get resource
	urllib.request.urlretrieve(product_img_url, filename)

	os.system(f'''curl -i --upload-file {join(dirname(__file__),'og_card_image.png')} -H 'Authorization: Bearer {access_token}' "{uploadurl}"''')

	api_url = 'https://api.linkedin.com/v2/posts'

	post_data = {
	  "author": URN,
	  "commentary": text_tags,
	  "content": {
		    "article": {
		        "title": quote_text,
		        "source": quote_link,
		        "thumbnail": imageurn
		    }
		},
	  "contentLandingPage":quote_link,
	   "visibility": "PUBLIC",
	   "distribution": {
		   "feedDistribution": "MAIN_FEED",
		   "targetEntities": [],
		   "thirdPartyDistributionChannels": []
	   },
	   "lifecycleState": "PUBLISHED",
	   "isReshareDisabledByAuthor": False
	}

	response = requests.post(api_url, headers=headers, json=post_data)

	if response.status_code == 201:
		print("Success")
		print(response.content)
	else:
		print(response.content)
post_on_linkedin()



