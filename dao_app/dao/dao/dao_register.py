from dao.modules.dao_modules_alll import *

class DAOREGISTER:
    # Register route
    def registers(data , my_collec):

        # requesting the json data from the frontend
        # data = request.json
        # Handling the  registration , like storing data in MongoDb

        #initialising the configparser
        # db, my_collec = DB.user_db()

        
        #taking the companyName 
        global companyName

        # taking the all entered data from the form 
        companyName= data['companyName']
        companyType = data['companyType']
        username = data['username']
        password = data['password']
        confirmPassword = data['confirmPassword']

        # Check if the username already exists 
        if my_collec.find_one({'username': username}) :
            print('user already exist')
            message = {"message": "Username already exists","status":"403"}
            return message
        
        # checking the company name already exists or not
        if my_collec.find_one({'companyName':companyName}):
            print("company already exist")
            message = {"message": "companyName already exists","status":"403"}
            return message

        # if the data not exist in the database
        # Storing the requested form details into a variable
        new_rec = {'companyName': companyName,'companyType': companyType,'username': username,'password': password,'confirmPassword': confirmPassword}
        
        # Inserting the details into the collection
        my_collec.insert_one(new_rec)

        # creating the two dbs for the company
        db_name_company = companyName # taking the db name as the company name
        chargeback_collection_name = f"{companyName}_chargeback" # taking the company name along with extensions
        sales_collection_name = f"{companyName}_sales"

        # # Inserting dummy values into the collection, because empty collection does not show in the database
        client = DAOCLIENT.mongo_client()
        db = client[db_name_company]
        db[chargeback_collection_name].insert_one({'welcome': companyName})
        db[sales_collection_name].insert_one({'welcome': companyName})

        # Deleting the dummy data which is inside the collections
        db[chargeback_collection_name].delete_many({})
        db[sales_collection_name].delete_many({})
        print('successfully registered')
        message = {"success" : "Company registered successfully!","status":"201"}
        return message