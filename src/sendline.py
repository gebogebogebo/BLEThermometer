import requests

# LINE通知する
def send_notify(access_token,comment):
        if( len(access_token) <= 0 ):
                return

        url = "https://notify-api.line.me/api/notify"
        headers = {'Authorization': 'Bearer ' + access_token}
        message = comment
        payload = {'message': message}
        print(message)
        requests.post(url, headers=headers, params=payload,)
