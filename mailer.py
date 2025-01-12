import requests
def send_simple_message():
  	return requests.post(
  		"https://api.mailgun.net/v3/sandbox3507901c13764f08bcdcb1b13b717826.mailgun.org/messages",
  		auth=("api", "6df4fcf14864d3279363715cf21184de-f55d7446-734f041f"),
  		data={"from": "Excited User <mailgun@sandbox3507901c13764f08bcdcb1b13b717826.mailgun.org>",
  			"to": ["thanosguruji@gmail.com"],
  			"subject": "Hello",
  			"text": "Testing some Mailgun awesomeness!"})
send_simple_message()