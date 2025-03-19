
from dao.modules.dao_modules_alll import *

class DAOLOGIN:
    #Login route
    def logins(username , password,credentials , my_collec):

        # Checking the requested user_ID and password
        if username in credentials and credentials[username] == password:
            # companyName = my_collec.find_one({'username': username}, {'_id': 0, 'companyName': 1})['companyName']  # taking the companyNamen

            details = list(my_collec.find({'username': username}, {'_id': 0}))  # storing the details in the variable
            message = {"success": 'Login successful, please wait a moment','login_details': details,"status": "200"}

            return message
        # checking if only the username is correct and password is wrong
        elif username in credentials:
            message = {"message": 'Wrong password, check your password once',"status": "401"}
            return message

        # checking if the username doesn't exist in the database
        else:
            message = {"message": 'No user exists with this username',"status": "400"}
            return message