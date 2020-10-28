from geoprofielen.objects.dbconnector import DBConnector

# note that the test result will depend on the database
# if the entry changes it will result in an error eventhough
# the code might be ok.. 
def test_dijktrajecten():
    dbc = DBConnector()
    dbc.get_dijktrajecten()