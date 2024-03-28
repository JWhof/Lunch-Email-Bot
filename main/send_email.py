import requests

api_key = open("secret/mailgun_api_key.txt", "r").read()

domain_name = "menu.bot.nu"

def send_simple_message():
    return requests.post(
        f"https://api.mailgun.net/v3/{domain_name}/messages",
        auth=("api", api_key),
        data={"from": f"Excited User <mailgun@{domain_name}>",
              "to": ["jwesterhof@ash.nl", f"lunch@{domain_name}"],
              "subject": "Hello",
              "text": "Testing some Mailgun awesomeness!"})

send_simple_message()