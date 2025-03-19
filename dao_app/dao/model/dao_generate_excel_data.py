
from dao.modules.dao_modules_alll import *

class DAOGENERATEEXCEL:
   
    def generate_excel_datas(encoded_excel,type_of_upload):
        try:
            def decode_base64_and_read_excel(encoded_data):
                # Decode the base64 string to binary data
                decoded_excel = base64.b64decode(encoded_data)
                # Use BytesIO to treat the binary data as a file-like object
                excel_data = io.BytesIO(decoded_excel)
                # Read the Excel file using pandas
                data = pd.read_excel(excel_data)
                return data

            # Receive base64 encoded Excel data from the request
            encoded_excel = request.json['excelbase64']
            type_of_upload = request.json.get('Typeofupload')

            # Decode and read the Excel data
            data = decode_base64_and_read_excel(encoded_excel)
            
            # Extract column headers
            headers = list(data.columns)
            header_string = " @@@".join(headers)
            
            # Preserve original data types and handle conversion
            def preserve_types(value):
                try:
                    return json.loads(json_util.dumps(value))
                except Exception:
                    return value

            # Convert datetime columns
            for col in data.columns:
                if pd.api.types.is_datetime64_any_dtype(data[col]):
                    data[col] = data[col].apply(lambda x: x if pd.notnull(x) else None)
                else:
                    data[col] = data[col].apply(preserve_types)

            
            # changing the collection based on the type_of_upload
            if type_of_upload == 'sales':
                header_template =['customer_name',"actual_shipment_date","product","Gross_sales",'quantity']

            elif type_of_upload == 'chargeback':
                header_template = ['customer_name',"creation_date","item","wac_price","contract_price","quantity"]
            else:
                raise ValueError("Invalid type_of_upload")


            # Create the final document structure                                       
            documents = [
                {"Header_template": header_template},
                {"header": header_string},
                {"exceldata": data.to_dict(orient='list')},
                {"type_of_upload": type_of_upload}
            ]

            return documents                                                    

        except Exception as e:
            print(f'Error: {e}')
            return jsonify({'error': str(e)}), 500

    
    def upload_to_dbs(typeofupload , excel_data):
            db , collection = DB.my_db()

            if not typeofupload or not excel_data:
                message = {'error': 'Typeofupload and exceldata are required', 'status': '500'}

            if not isinstance(excel_data, list) or not excel_data:
                message = {'error': 'exceldata must be a non-empty list', 'status': '500'}

            if typeofupload == 'sales':
                collection = db['sales_collection']
                for record in excel_data:
                    if 'actual_shipment_date' in record and isinstance(record['actual_shipment_date'], str):
                        try:
                            record['actual_shipment_date'] = ast.literal_eval(record['actual_shipment_date'])
                        except (ValueError, SyntaxError):
                            return jsonify({'error': f"Invalid format for actual_shipment_date in record: {record}"})
                    
                    if 'product' in record and isinstance(record['product'], str):
                        try:
                            record['product'] = ast.literal_eval(record['product'])
                        except (ValueError, SyntaxError):
                            return jsonify({'error': f"Invalid format for product in record: {record}"})
            elif typeofupload == 'chargeback':
                collection = db['chargeback_collection']
                for record in excel_data:
                    if 'creation_date' in record and isinstance(record['creation_date'], str):
                        try:
                            record['creation_date'] = ast.literal_eval(record['creation_date'])
                        except (ValueError, SyntaxError):
                            return jsonify({'error': f"Invalid format for creation_date in record: {record}"})
                    
                    if 'item' in record and isinstance(record['item'], str):
                        try:
                            record['item'] = ast.literal_eval(record['item'])
                        except (ValueError, SyntaxError):
                            return jsonify({'error': f"Invalid format for item in record: {record}"})
                        
                    if 'customer' in record and isinstance(record['customer'],str):
                        try:
                            record['customer'] = ast.literal_eval(record['customer'])
                        except (ValueError , SyntaxError):
                            return jsonify({'error': f"Invalid format for item in record: {record}"})
            else:
                return jsonify({'error': 'Invalid Typeofupload', 'status': '500'})

            collection.delete_many({})
            collection.insert_many(excel_data)

            return message
        