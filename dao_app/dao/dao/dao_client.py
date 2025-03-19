from dao.modules.dao_modules_alll import *

class DAOCLIENT:
    def mongo_client():
        client = pymongo.MongoClient('locahost:27017')
        return client
    