from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
from django.http import HttpResponse, JsonResponse

'''
    Takes in phone number and url to google maps route in JSON object request.
    Sends a request to Twilio to send a given url to given phone number in a
    text message.
'''
def send_directions(request):
    ACCOUNT_SID = "AC713f1165cf353a8f68d1000502d8bc93"
    AUTH_TOKEN = "dda8d0bc7b169ccd4c515179e4dba4a4"

    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

    if request.method == 'GET':
        url = request.GET.get('url', None)
        phone_number = "+1" + request.GET.get('number', None)
        try:
            client.messages.create(
               to=phone_number,
               from_="+14135917043",
               body=url,
            )
            return HttpResponse("OK")
        except TwilioRestException as e:
            return HttpResponse(e.msg)
    else:
        return HttpResponse(
                json.dumps({"error":"unable to send text."}),
                content_type="application/json"
        )
