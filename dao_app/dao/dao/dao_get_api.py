from dao.modules.dao_modules_alll import *

class DAOGETDATA:
    def get_data(companyName , typeofdata):
        try:

            # Check if company name is provided in login_id
            if not companyName:
                return jsonify({"error": "Company name not found in login"})

            # Calculate start and end dates for the last 6 months
            start_date = datetime.now()
            end_date = start_date - relativedelta(months=6)

            # Use the my_db function from the DB class to connect to MongoDB
            db, collection = DB.my_db(companyName, typeofdata)
            if typeofdata == 'pastsales':
                pipeline = Pipeline.get_sales_pipeline(start_date, end_date)
            elif typeofdata == 'futuresales':
                pipeline = Pipeline.get_charegeback_pipeline(start_date, end_date)
            elif typeofdata == 'pastchargeback':
                pipeline = Pipeline.get_future_pipeline(start_date, end_date)
            elif typeofdata == 'futurechargeback':
                pipeline = Pipeline.get_future_pipeline(start_date, end_date)
            else :
                return jsonify({'message':"invalid type of data"})

            if db is None or collection is None:
                return jsonify({"error": "Failed to connect to MongoDB"})

            # Use the sales pipeline from the Pipeline class

            # Aggregate the collection using the pipeline
            data = list(collection.aggregate(pipeline))

            # Return the aggregated data as JSON response
            return data
        except Exception as e:
            return jsonify({"error": "An error occurred", "details": str(e)}), 500