import requests
def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox3507901c13764f08bcdcb1b13b717826.mailgun.org/messages",
  		auth=("api", ""),
  		data={"from": "",
  			"to": ["thanosguruji@gmail.com"],
  			"subject": "Hello",
  			"text": "Testing some Mailgun awesomeness!"})
send_simple_message()