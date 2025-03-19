class Pipeline:
    @staticmethod
    def get_sales_pipeline(start_date, end_date):
        pipeline = [
            {'$match': {'actual_shipment_date': {'$gte': end_date, '$lte': start_date}}},
            {'$group': {'_id': {'year': {'$year': '$actual_shipment_date'}, 'month': {'$month': '$actual_shipment_date'}}, 'total_sales': {'$sum': '$Gross_sales'}}},
            {'$sort': {'_id': 1}},
            {'$skip': 0},
            {'$limit': 10}
        ]
        return pipeline

    @staticmethod
    def get_chargeback_pipeline(start_date, end_date):
        pipeline = [
            {'$match': {'creation_date': {'$gte': end_date, '$lte': start_date}}},
            {'$group': {'_id': {'year': {'$year': '$creation_date'}, 'month': {'$month': '$creation_date'}}, 'total_amount': {'$sum': '$amount'}}},
            {'$sort': {'_id': 1}},
            {'$skip': 0},
            {'$limit': 10}
        ]
        return pipeline

    @staticmethod
    def get_future_pipeline(start_date, end_date):
        pipeline = [
            {'$match': {'future_date': {'$gte': start_date, '$lte': end_date}}},
            {'$group': {'_id': {'year': {'$year': '$future_date'}, 'month': {'$month': '$future_date'}}, 'total_amount': {'$sum': '$amount'}}},
            {'$sort': {'_id': 1}},
            {'$skip': 0},
            {'$limit': 10}
        ]
        return pipeline
