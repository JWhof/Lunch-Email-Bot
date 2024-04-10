import requests

api_key = open("secret/mailgun_api_key.txt", "r").read()

domain_name = "sandbox9f74cd3c9c8943feaba6c15f177944d0.mailgun.org"

def send_simple_message():
	return requests.post(
		f"https://api.mailgun.net/v3/{domain_name}/messages",
		auth=("api", f"{api_key}"),
		data={"from": f"Lunch Menu Bot<lunch@{domain_name}>",
			"to": ["jwesterhof@ash.nl"],
			"subject": "Hello",
			"text": "Testing some Mailgun awesomeness!"})

print(send_simple_message())