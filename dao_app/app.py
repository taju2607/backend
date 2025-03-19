#importing the modules
from dao.modules.dao_modules_alll import *

# creating the app for the flask

app = Flask(__name__)
CORS(app, supports_credentials=True)
  # To allow cross-origin requests
# Global variable login_id  to store company name

login_id = {}
# Index route
@app.route('/')
def index():
    message = "Your API is working successfully"
    return jsonify(success=message),200 # checking the flask is running or not

##################################################################################################################################
# Login route
@app.route('/login', methods=['POST', 'GET'])
def login():
    # Requesting the JSON data from the frontend
    data = request.json

    # Requesting the user_ID and password from the login form
    username, password = data['username'], data['password']

    # Using the user_db method to get the database and collection from dao -> db.py file
    db, my_collec = DB.user_db()

    # Fetching all user credentials from the database into the credentials variable
    credentials = {user['username']: user['password'] for user in my_collec.find({}, {'_id': 0, 'username': 1, 'password': 1})}

    # Checking if the username exists and the password matches
    if username in credentials and credentials[username] == password:
        companyName = my_collec.find_one({'username': username}, {'_id': 0, 'companyName': 1})['companyName']  # taking the companyName
        login_id.update({'companyName': companyName}) # updating the company name in the login_id dictionary

    # calling the login method from the DAOLOGIN class
    message = DAOLOGIN.logins(username, password, credentials, my_collec)
    return jsonify(message)

##################################################################################################################################

# Sample endpoint to fetch sales data for the last 6 months
@app.route('/get_sales_data_last_6_months', methods=['GET', 'POST'])
def get_sales_data_last_6_months():
    try:
        login_id = request.json  # Assuming login_id is passed in the request payload
        companyName = login_id.get('companyName') # taking the company name from the json
        typeofdata = 'pastsales' # defining the type of data we want to display
        # calling the get_data method
        data = DAOGETDATA.get_data(companyName,typeofdata)

        # Return the aggregated data as JSON response
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)})
    
##################################################################################################################################

@app.route('/get_chargeback_data_last_6_months', methods=['GET', 'POST'])
def get_chargeback_data_last_6_months():
    try:
        login_id = request.json  # Assuming login_id is passed in the request payload
        companyName = login_id.get('companyName') 
        typeofdata = 'pastchargeback'
        # Check if company name is provided in login_id
        data = DAOGETDATA.get_data(companyName,typeofdata)

        # Return the aggregated data as JSON response
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)})
    
##################################################################################################################################

@app.route('/get_sales_data_future_6_months', methods=['GET', 'POST'])
def get_sales_data_future_6_months():
    try:
        login_id = request.json  # Assuming login_id is passed in the request payload
        companyName = login_id.get('companyName')
        typeofdata = 'futuresales'
        # Check if company name is provided in login_id
        data = DAOGETDATA.get_data(companyName,typeofdata)

        # Return the aggregated data as JSON response
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)})
##################################################################################################################################

@app.route('/get_chargeback_data_future_6_months', methods=['GET', 'POST'])
def get_chargeback_data_future_6_months():
    try:
        login_id = request.json  # Assuming login_id is passed in the request payload
        companyName = login_id.get('companyName')
        typeofdata = 'futurechargeback'
        # Check if company name is provided in login_id
        data = DAOGETDATA.get_data(companyName,typeofdata)

        # Return the aggregated data as JSON response
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)})
##################################################################################################################################

# Register route
@app.route('/register', methods=['POST','GET'])
def register():

    # requesting the json data from the frontend
    data = request.json

    #taking the database connction from the user_db() method 
    db, my_collec = DB.user_db()

    message = DAOREGISTER.registers(data,my_collec)
    return jsonify(message)

#################################################################################################################################

# Generate sales prediction route
@app.route('/generate_sales_prediction', methods=['POST','GET'])
def generate_sales_prediction():
    # Taking adjustment factors and alpha beta and window length from the user

    salesadjustmentFactor1 = float(request.json.get('salesadjustmentFactor1', 0.9))
    salesadjustmentFactor2 = float(request.json.get('salesadjustmentFactor2', 0.5))
    salesadjustmentFactor3 = float(request.json.get('salesadjustmentFactor3', 0.4))
    salesalpha = float(request.json.get('salesalpha', 0.1))
    salesbeta = float(request.json.get('salesbeta', 1))
    saleswindows = int(request.json.get('saleswindows', 13))

    # calling the generate_sales_predictions method and storing the final output in the message variable
    message = DAOSALESPREDICTION.generate_sales_predictions(salesadjustmentFactor1,salesadjustmentFactor2,salesadjustmentFactor3,salesalpha,salesbeta,saleswindows)

    return jsonify(message), 201

#################################################################################################################################

# Generate chargeback prediction route
@app.route('/generate_chargeback_prediction', methods=['POST', 'GET'])
def generate_chargeback_prediction():
    warnings.filterwarnings('ignore', category=FutureWarning)

    # Taking the adjustment factor and the beta values from the user
    
    adjustmentFactor1 = float(request.json.get('chargebackadjustmentFactor1', 0.9))
    adjustmentFactor2 = float(request.json.get('chargebackadjustmentFactor2', 0.9))
    adjustmentFactor3 = float(request.json.get('chargebackadjustmentFactor3', 0.4))
    adjustmentFactor4 = float(request.json.get('chargebackadjustmentFactor4', 0.4))
    beta1 = float(request.json.get('chargebackbeta1', 0.8))
    beta2 = float(request.json.get('chargebackbeta2', 1))

    # calling the generate_chargeback_predictions method and storing the final output in the message variable
    message = DAOGENERATECHARGEBACK.generate_chargeback_predictions(adjustmentFactor1,adjustmentFactor2,adjustmentFactor3,adjustmentFactor4,beta1,beta2)

    return jsonify(message), 201

##################################################################################################################################

@app.route('/generate_excel_data', methods=['POST'])
def generate_excel_data():
        # Receive base64 encoded Excel data from the request
        encoded_excel = request.json['excelbase64']
        type_of_upload = request.json.get('Typeofupload')

        # calling the geneerate excel datas method
        documents = DAOGENERATEEXCEL.generate_excel_datas(encoded_excel,type_of_upload)

        return jsonify(documents)                                                      


####################################################################################################################################

@app.route('/upload_to_db', methods=['GET', 'POST'])
def upload_to_db():
    try:
        # requesting the data 
        data = request.json
         
        # take the typeofupload and excel_data from the data variable
        typeofupload = data.get('Typeofupload')
        excel_data = data.get('exceldata')

        # calling the upload to dbs method to upload the data
        message = DAOGENERATEEXCEL.upload_to_dbs(typeofupload , excel_data)

        return jsonify(message), 200
    except Exception as e:
        return jsonify({'error': str(e)})

##################################################################################################################################

# Global variables

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    # Taking the username or email id from the user
    username = request.json.get('username')

    # calling the 
    message = DAOFORGOTPASSWORD.forgot_passwords(username)
    return jsonify(message)


##################################################################################################################################

@app.route('/entered_otp', methods=['POST'])
def entered_otp():
    # Taking the username, OTP, new password, and confirm password from the user
    username = request.json.get('username')
    otp_entered = request.json.get('otp')
    new_password = request.json.get('new_password')
    confirm_password = request.json.get('confirm_password')

    message = DAOFORGOTPASSWORD.entered_otp(username , otp_entered , new_password , confirm_password )
    return jsonify(message), 200
    
##################################################################################################################################

# still developing --------------------------
@app.route('/export', methods=['GET', 'POST'])
def export_data():
    companyName = login_id.get('companyName')
    data = request.json
    typeofdata = data.get('Typeofdata')

    config = configparser.ConfigParser()
    config.read('configs/exportdata.config')

    mongodb_uri = config['MongoDBFetch']['mongodb_uri']
    db_name = config['MongoDBFetch']['db_name']

    client = pymongo.MongoClient(mongodb_uri)
    db = client[companyName]

    if typeofdata == 'pastsales':
        collection = companyName + '_sales'
    elif typeofdata == 'pastchargeback':
        collection = companyName + '_chargeback'
    elif typeofdata == 'futuresales':
        collection = companyName + '_futuresales'
    elif typeofdata == 'futurechargeback':
        collection = companyName + '_futurechargeback'
    else:
        return jsonify({'message': "wrong input", 'status': '401'})

    collection_db = db[collection]
    all_data = list(collection_db.find({}))  # Convert cursor to list

    if not all_data:
        return jsonify({'message': "No data found in the collection", 'status': '404'})

    data = pd.DataFrame(all_data)
    excel_file = collection + '_excel.xlsx'
    data.to_excel(excel_file, index=False)

    # Sending the file as a response
    response = send_file(excel_file, as_attachment=True, attachment_filename=excel_file)

    # Adding a success message
    response.headers['X-Suggested-Filename'] = excel_file
    response.headers['X-Message'] = 'Excel file successfully downloaded'

    return response

##################################################################################################################################

# Run the app
if __name__ == "__main__":
    app.run(debug=False, host='192.168.1.2', port=5000)

##################################################################################################################################
