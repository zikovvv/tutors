import json
import requests as r
import config as cfg

class Client :
    def __init__(self, server_ip, api_key) :
        self.server_ip = server_ip
        self.api_key_path = api_key
        self.session = r.session()
        self.session.cookies['Authorization'] = self.api_key
        print('')

    @property
    def api_key(self):
        with open(self.api_key_path, 'rb') as f :
            return f.read()

    @api_key.setter
    def api_key(self, key : bytes):
        with open(self.api_key_path, 'wb+') as f :
            f.write(key)




if __name__ == '__main__':
    client = Client()


    #res = r.get(f'{server_ip}/signup')



    """print(r.get(
            f'{server_ip}/tutors1',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps({'231' : 1412412}),
            auth = ,
        ).json(),
    )"""




