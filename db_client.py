from boto3 import resource
from boto3.dynamodb.conditions import Key
import boto3
import config

class DBClient:

    global dynamodb
    dynamodb = boto3.client('dynamodb', region_name=config.region_name,
                        aws_access_key_id=config.aws_access_key_id,
                        aws_secret_access_key=config.aws_secret_access_key)
    resource = boto3.resource('dynamodb', region_name=config.region_name,
                        aws_access_key_id=config.aws_access_key_id,
                        aws_secret_access_key=config.aws_secret_access_key)
    
    def create_tables(self):

        if not self.check_for_table('login'):
            dynamodb.create_table(TableName='login', 
                                  KeySchema=[
                                            { 'AttributeName': 'email' , 'KeyType': 'HASH'},
                                            ],
                                  AttributeDefinitions=
                                            [
                                            { 'AttributeName': 'email' , 'AttributeType': 'S'},
                                            ],
                                  ProvisionedThroughput={ 'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
        else:
            print("Table \"login\" already exists")

        self.add_users()

        if not self.check_for_table('music'):
            dynamodb.create_table(TableName='music', 
                                  KeySchema=
                                            [
                                            { 'AttributeName': 'title' , 'KeyType': 'HASH'},
                                            ],
                                  AttributeDefinitions=
                                            [
                                            { 'AttributeName': 'title' , 'AttributeType': 'S'},
                                            ],
                                  ProvisionedThroughput={ 'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5})
            print("Table created successfully")
        else:
            print("Table \"music\" already exists")

        if not self.check_for_table('subscribed'):
            dynamodb.create_table(TableName='subscribed',
                                  KeySchema=
                                            [
                                            { 'AttributeName': 'email', 'KeyType': 'HASH'},
                                            { 'AttributeName': 'title', 'KeyType': 'RANGE'},
                                            ],
                                  AttributeDefinitions=
                                            [
                                            { 'AttributeName': 'email', 'AttributeType': 'S'},
                                            { 'AttributeName': 'title', 'AttributeType': 'S'},
                                            ],
                                  ProvisionedThroughput={ 'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5 })
            print("Table created successfully")
        else:
            print("Table \"subscribed\" already exists")

    def add_users(self):
        table = self.resource.Table('login')
        for i in range(0, 10):
            j = i
            email = 's3855159@student.rmit.edu.au{}'.format(str(i))
            user_name = 'Corbin Peever{}'.format(str(i))
            password = ""
            for j in range(6):
                if j == 10:
                    j = 0
                password += str(j)
                j += 1

        if table.get_item(Key={'email': email}).get('Item') is None:
            item = { 'email': email, 'user_name': user_name, 'password': password }
            table.put_item(Item=item)
            print("User added successfully")
        else:
            print("User already exists")

    def put_item(self, table_name, item):
        table = self.resource.Table(table_name)
        table.put_item(Item=item)

    def query(self, table_name, key, value):
        table = self.resource.Table(table_name)
        response = table.query(
            KeyConditionExpression=Key(key).eq(value)
        )
        return response.get('Items') 

    def put_items(self, table_name, items):
        table = dynamodb.Table(table_name)
        with table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=item)

    def get_item(self, table_name, key):
        table = self.resource.Table(table_name)
        response = table.get_item(Key=key)
        return response.get('Item')

    def edit_item(self, table_name, key, update_expression, expression_attribute_values):
        table = dynamodb.Table(table_name)
        table.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

    def create_table(self, table_name, key_schema, provisioned_throughput):
        
        current_tables = dynamodb.list_tables()['TableNames']

        if table_name not in current_tables:
            print('Creating table: {}'.format(table_name))
            table = dynamodb.create_table(
                TableName=[table_name],
                KeySchema=[key_schema],
                ProvisionedThroughput=[provisioned_throughput]
            )
        else:
            print('Table already exists: {}'.format(table_name)),
            table = dynamodb.Table(table_name)
            return None
        return table

    def delete_table(self, table_name):
        table = dynamodb.Table(table_name)
        table.delete()

    def get_table(self, table_name):
        table = dynamodb.Table(table_name)
        return table
        
    def check_for_table(self, table_name):
        current_tables = dynamodb.list_tables()['TableNames']
        if table_name in current_tables:
            return True
        else:
            return False
    
    def check_for_item(self, table_name, key):
        table = dynamodb.Table(table_name)
        response = table.get_item(Key=key)
        if response.get('Item') is None:
            return False
        else:
            return True
        
    def delete_item(self, table_name, key):
        table = self.resource.Table(table_name)
        table.delete_item(Key=key)