from dao.modules.dao_modules_alll import *

class DAOGENERATECHARGEBACK:
    def generate_chargeback_predictions(adjustmentFactor1,adjustmentFactor2,adjustmentFactor3,adjustmentFactor4,beta1,beta2):
        # Initialize the configuration parser
        db , collection = DB.my_db()

        data = collection.find({},{"creation_date": 1, "item": 1, "wac_price": 1, "contract_price": 1, "quantity": 1, "_id": 0})

        df = pd.DataFrame(data)
        df.info()

        df['quantity'] = pd.to_numeric(df['quantity'])
        df['wac_price'] = pd.to_numeric(df['wac_price'])
        df['contract_price'] = pd.to_numeric(df['contract_price'])

        # Calculate the new column and assign it to the DataFrame
        df['Final_sales'] = (df['wac_price'] - df['contract_price']) * df['quantity']

        df = df[['item', 'creation_date', 'Final_sales']]

        df.head()

        # Assuming df is your DataFrame

        def get_ndc_description(item):
            if pd.notna(item):
                return item.get('ndc')
            else:
                return None

        # Create the 'ndc' and 'description' columns based on the 'item' column
        df['ndc'] = df['item'].apply(lambda x: get_ndc_description(x))
        df['description'] = df['item'].apply(get_ndc_description)
        df.drop('item', axis=1, inplace=True)

        df['creation_date'] = pd.to_datetime(df['creation_date'])

        # Filter data for dates from 1-1-2023 onwards
        start_date = pd.to_datetime('2023-01-01')
        filtered_df = df[df['creation_date'] >= start_date]

        # Then perform your groupby operation on the filtered DataFrame
        dg = filtered_df.groupby(['creation_date', 'ndc'])['Final_sales'].sum().reset_index()


        lines = dg['ndc'].unique()
        lines

        fit_models = {}

        # Iterate through unique NDC values
        for stock_line in lines:
            frame = dg[dg['ndc'] == stock_line].copy()
            
            # Debug print to check the count of rows for each NDC
            print(f"Stock Line: {stock_line}, Rows: {len(frame)}")

            frame.drop('ndc', axis=1, inplace=True)
            frame.columns = ['ds', 'y']
            
            # Check if there are at least two non-NaN rows in the 'y' column
            if frame['y'].count() >= 2:
                m = Prophet(interval_width=0.95, growth='linear')
                
                # Add US holidays
                m.add_country_holidays(country_name='US')
                
                # Add additional holidays if needed
                # m.add_holidays(your_custom_holidays_dataframe)
                
                m.add_seasonality(name='monthly', period=30.5, fourier_order=25)
                training_run = m.fit(frame)
                
                # Store the trained model in the fit_models dictionary
                fit_models[stock_line] = m
            else:
                print(f"Skipping NDC {stock_line} due to insufficient data points.")


        forecasts = {}

        # Iterate through the NDCs in fit_models
        for stock_line, model in fit_models.items():
            frame = dg[dg['ndc'] == stock_line].copy()
            frame.drop('ndc', axis=1, inplace=True)
            frame.columns = ['ds', 'y']

            # Make a future dataframe for the NDC
            if len(frame) < 16:
                print(f"Condition met for NDC {stock_line}. Length: {len(frame)}")
                future = model.make_future_dataframe(periods=6, freq='MS')

                # Generate the forecast for the NDC
                forecast = model.predict(future)
                forecast['yhat_orig'] = forecast['yhat']  # Store original yhat values for comparison

                # Introduce little peaks by adding random noise to the forecasted values
                noise_factor = 0.02  # Adjust this value to control the magnitude of the peaks
                forecast['yhat'] += np.random.normal(0, noise_factor, len(forecast))

                # Smooth the forecasted values
                #beta = 1
                #forecast['yhat'] = beta * forecast['yhat'] + (1 - beta) * forecast['yhat'].shift(1)

                # Apply a downward adjustment to the last part of the forecast
                Adjusted_index = -6
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= adjustmentFactor4
            elif 16 <= len(frame) < 39:
                future = model.make_future_dataframe(periods=180, freq='D')

                # Generate the forecast for the NDC
                forecast = model.predict(future)
                forecast['yhat_orig'] = forecast['yhat']  # Store original yhat values for comparison
                beta = beta2
                forecast['yhat'] = beta * forecast['yhat'] + (1 - beta) * forecast['yhat'].shift(1)
                Adjusted_index = -180
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= adjustmentFactor3
            elif 40 <= len(frame) < 70:
                future = model.make_future_dataframe(periods=180, freq='D')
                # Generate the forecast for the NDC
                forecast = model.predict(future)
                forecast['yhat_orig'] = forecast['yhat']  # Store original yhat values for comparison
                beta = beta1
                forecast['yhat'] = beta * forecast['yhat'] + (1 - beta) * forecast['yhat'].shift(1)
                Adjusted_index = -180
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= adjustmentFactor2

            else:
                future = model.make_future_dataframe(periods=180, freq='D')
                forecast = model.predict(future)
                forecast['yhat'] = forecast['yhat'].astype(int)
                Adjusted_index = -180
                forecast.loc[forecast.index[Adjusted_index:], 'yhat'] *= adjustmentFactor1
            forecasts[stock_line] = forecast

        db , collection = DB.my_db()

        collection.delete_many({})

        ndc_descriptions = df[['ndc', 'description']].drop_duplicates().set_index('ndc')['description']

        for ndc, forecast_data in forecasts.items():
            # Check if there is forecast data for the current NDC
            if not forecast_data.empty:
                # Retrieve the description for the current NDC
                description = ndc_descriptions.get(ndc)
                
                # If description is not found for the NDC, set it to None
                if description is None:
                    print(f"No description found for NDC: {ndc}")
                
                # Determine the cutoff date dynamically from the tail of the 'shipment_date' column in dg DataFrame
                cutoff_date = dg.loc[dg['ndc'] == ndc, 'creation_date'].tail(1).values[0]

                # convert to timestamp:
                ts = (cutoff_date - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                from datetime import datetime
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
        message = {'message':'Generating the chargeback predictions is completed','status':'201'}
        return message