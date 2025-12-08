import requests

email = 'mpestudante12@gmail.com'
api_key = '90af93e7-34b7-4368-a8ee-a412ba8b2fc0'
url = f'https://api.mails.so/v1/validate?email={email}'

headers = {
    'x-mails-api-key': api_key
}

response = requests.get(url, headers=headers)
data = response.json()
print(data)
  