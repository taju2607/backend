from dao.modules.dao_modules_alll import *

class DAOSALESPREDICTION:
    def generate_sales_predictions(salesadjustmentFactor1,salesadjustmentFactor2,salesadjustmentFactor3,salesalpha,salesbeta,saleswindows):
        # Initialize the configuration parser
        db , collection = DB.my_db()

        data = collection.find(
                    {},
                    {
                        "actual_shipment_date": 1,
                        "product": 1,
                        "Gross_sales": 1,
                        "_id": 0
                    }
                    )

        df = pd.DataFrame(data)
        df.info()

        # client.close()
        df.head()

        def extract_ndc(product):
            if isinstance(product, dict):
                return product.get('ndc')
            else:
                return None

        def extract_description(product):
            if isinstance(product, dict):
                return product.get('description')
            else:
                return None

        # Apply the functions to create the 'ndc' and 'description' columns
        df['ndc'] = df['product'].apply(extract_ndc)
        df['description'] = df['product'].apply(extract_description)
        df.head()
        df.drop('product', axis=1, inplace=True)
        dg = df.groupby(['actual_shipment_date', 'ndc'])['Gross_sales'].sum().reset_index()

        lines = dg['ndc'].unique()
        lines

        import numpy as np
        # Initialize an empty dictionary to store the fitted models
        fit_models = {}

        # Iterate through unique NDC values (assuming 'product' column contains NDC values)
        for ndc in lines:
            # Filter the DataFrame for the current NDC
            frame = dg[dg['ndc'] == ndc].copy()
            
            # Debug print to check the count of rows for each NDC
            print(f"NDC: {ndc}, Rows: {len(frame)}")
            
        
            # Rename columns as required for Prophet
            frame.rename(columns={'actual_shipment_date': 'ds', 'Gross_sales': 'y'}, inplace=True)
            
            # Check if there are at least two non-NaN rows in the 'y' column
            if frame['y'].count() >= 45:
                # Initialize Prophet model with custom seasonality
                m = Prophet(interval_width=0.95, growth='linear')
                m.add_seasonality(name='monthly', period=30.5, fourier_order=10)
                
                # Fit the model to the data
                m.fit(frame)
                
                # Store the trained model in the fit_models dictionary using the NDC as the key
                fit_models[ndc] = m
            elif 3 <= frame['y'].count() < 45:
                print(f"NDC {ndc} have data points less than 45.")
                # Initialize Prophet model with custom seasonality
                m = Prophet(interval_width=0.96, growth='linear', changepoint_prior_scale=7)
                m.add_seasonality(name='yearly', period=300, fourier_order=10)
                
                # Fit the model to the data
                m.fit(frame)
                
                # Store the trained model in the fit_models dictionary using the NDC as the key
                fit_models[ndc] = m
            else:
                print(f"Skipping NDC {ndc} due to insufficient data points.")

        forecasts = {}

        # Iterate through the NDCs in fit_models
        for stock_line, model in fit_models.items():
            frame = dg[dg['ndc'] == stock_line].copy()
            frame.drop('ndc', axis=1, inplace=True)
            frame.columns = ['ds', 'y']
            
            # Generate the forecast for the NDC
            future = model.make_future_dataframe(periods=180, freq='D')
            forecast = model.predict(future)
            forecast = forecast[~forecast['ds'].dt.dayofweek.isin([5, 6])]
            
            if len(frame) < 18:
                # Input values are less than 18, use the first code snippet for smoothing
                future = model.make_future_dataframe(periods=6, freq='MS')

                # Generate the forecast for the NDC
                forecast = model.predict(future)
                forecast['yhat_orig'] = forecast['yhat']

                # Apply Exponential Moving Average (EMA) for global smoothing to the 'yhat' column
                alpha = salesalpha  # Adjust this value as needed (smoothing factor)
                beta = salesbeta   # Adjust this value as needed (weight for the original values)

                forecast['yhat_smoothed'] = forecast['yhat'].ewm(alpha=alpha, adjust=False).mean()

        # Combine original and smoothed values with a weighted average
                forecast['yhat'] = alpha * forecast['yhat'] + beta * forecast['yhat_smoothed'] + (1 - alpha - beta) * forecast['yhat'].shift(1)
            elif 18 <= len(frame) < 45:
                
                future = model.make_future_dataframe(periods=6, freq='MS')

                # Generate the forecast for the NDC
                forecast = model.predict(future)
                forecast['yhat_orig'] = forecast['yhat']
                window_length = saleswindows  # Adjust this value as needed

                # Apply a moving window to smooth the forecasted values
                forecast['yhat_smoothed'] = forecast['yhat'].rolling(window=window_length, min_periods=1).mean()
                Adjusted_index = -6
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= salesadjustmentFactor3
            elif 45 <= len(frame) < 60:
                future = model.make_future_dataframe(periods=180, freq='D')

                # Generate the forecast for the NDC
                Adjusted_index = -135
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= salesadjustmentFactor2

            else:
                Adjusted_index = -135
                Adjusted_yhat = forecast['yhat'].iloc[Adjusted_index:]
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= salesadjustmentFactor1
            forecast['yhat'] = forecast['yhat'].apply(lambda x: max(0, x))
            forecasts[stock_line] = forecast
            forecast['yhat'] = forecast['yhat'].astype(int)

        db , collection = DB.my_db()

        collection.delete_many({})

        for ndc, forecast_data in forecasts.items():
            # Check if there is forecast data for the current NDC
            if not forecast_data.empty:
                # Retrieve the description for the current NDC from ndc_description DataFrame
                description = df.loc[df['ndc'] == ndc, 'description'].values[0]
                
                # Determine the cutoff date dynamically from the tail of the 'shipment_date' column in dg DataFrame
                cutoff_date = dg.loc[dg['ndc'] == ndc, 'actual_shipment_date'].tail(1).values[0]
                
                # convert to timestamp:
                ts = (cutoff_date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

                # standard utctime from timestamp
                dt = datetime.utcfromtimestamp(ts)

                # get the new updated year
                dt = dt.replace(day=1)

                # convert back to numpy.datetime64:
                cutoff_date = np.datetime64(dt)
                # Iterate through the rows in the forecast_data DataFrame
                for index, row in forecast_data.iterrows():
                    # Extract the date directly (assuming it's already in datetime format)
                    date = row['ds']

                    # Check if the date is after the dynamically determined cutoff date
                    if date > cutoff_date:
                        # Create a dictionary for the MongoDB document
                        document = {
                            'Date': date,         # Assuming 'ds' is the date
                            'amount': row['yhat'],     # Assuming 'yhat' is the forecasted value
                            'ndc': ndc,              # NDC value
                            'description': description  # Description value
                        }
            
                        # Insert the document into the MongoDB collection
                        collection.insert_one(document)
                        print(f"Uploaded forecast data for NDC: {ndc} on {date}")
                    else:
                        print(f"Skipped forecast data for NDC: {ndc} on {date} (Date is before the cutoff date)")
            else:
                print(f"No forecast data found for NDC: {ndc}")

        print("Upload completed for all NDCs.")
        message = {'message':'Generating the sales predictions is completed'}
        return message