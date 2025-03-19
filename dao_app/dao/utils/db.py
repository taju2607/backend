from dao.modules.dao_modules_alll import *

class DB:
    @staticmethod
    def my_db( company_name, data_type):
        config = configparser.ConfigParser()

        try:
            # Read the configuration file
            config.read('predictions.config')

            # Extract URI
            mongodb_uri = config['MongoDBFetchURI']['mongodb_uri']

            # Generate dynamic database and collection names
            db_name = company_name
            collection_name = f"{company_name}_{data_type}_collection"

            # Connect to MongoDB
            client = pymongo.MongoClient(mongodb_uri)
            db = client[db_name]
            collection = db[collection_name]
            return db, collection
        except configparser.Error as e:
            print(f"Configuration error: {e}")
            return None, None
        except pymongo.errors.ConnectionError as e:
            print(f"Could not connect to MongoDB: {e}")
            return None, None
        except KeyError as e:
            print(f"Configuration key error: {e}")
            return None, None
        
    def user_db():
        config = configparser.ConfigParser()
        config.read('predictions.config')
        mongodb_uri = config['MongoDBFetchURI']['mongodb_uri']
        db_name_config = config['MongoDBFetchCommon']['db_name']
        collection_name_config = config['MongoDBFetchCommon']['collection_name']

        client = pymongo.MongoClient(mongodb_uri)
        db_name = client[db_name_config]
        collection = db_name[collection_name_config]
        return db_name,collection
