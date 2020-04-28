from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from ip_data import IpData

app = Flask(__name__)
CORS(app)
api = Api(app)
ipData = IpData()

class IpDataApi(Resource):
    def get(self):
        return ipData.ipmap

class IpDatesApi(Resource):
    def get(self, ip):
        return ipData.getIpTimes(ip)

api.add_resource(IpDataApi, '/')
api.add_resource(IpDatesApi, '/<string:ip>')

if __name__ == '__main__':
    app.run(debug=True)