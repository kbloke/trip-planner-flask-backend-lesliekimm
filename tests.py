import server
import unittest
import json
from pymongo import MongoClient


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()
        # Run app in testing mode to retrieve exceptions and stack traces
        server.app.config['TESTING'] = True

        # Inject test database into application
        mongo = MongoClient('localhost', 27017)
        db = mongo.test_database
        server.app.db = db

        # Drop collection (significantly faster than dropping entire db)
        db.drop_collection('myobjects')

    # Trip tests
    def test_post(self):
        response = self.app.post('/trip/', data=json.dumps(dict(
            name='San Fran', waypoints=[])),
            content_type='application/json')

        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'application/json' in response.content_type
        assert 'San Fran' in responseJSON['name']
        self.assertEqual(0, len(responseJSON['waypoints']))

    def test_get(self):
        response = self.app.post('/trip/', data=json.dumps(dict(
            name='Cross country', waypoints=[])),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON['_id']

        response = self.app.get('/trip/'+postedObjectID)
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'Cross country' in responseJSON['name']
        self.assertEqual(0, len(responseJSON['waypoints']))

    def test_get_nonexistent_trip(self):
        response = self.app.get('/trip/55f0cbb4236f44b7f0e3cb23')
        self.assertEqual(response.status_code, 404)

    def test_get_no_id(self):
        response = self.app.get('/trip/')
        self.assertEqual(response.status_code, 404)

    def test_put(self):
        response = self.app.post('/trip/', data=json.dumps(dict(
            name='San Fran', waypoints=[])),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON['_id']

        response = self.app.put('/trip/'+postedObjectID, data=json.dumps(
            dict(name='BOING',
                 waypoints=['mission', 'soma', 'nob hill'])),
                 content_type='application/json')
        responseJSON = json.loads(response.data.decode())

        self.assertEqual(response.status_code, 200)
        assert 'BOING' in responseJSON['name']
        self.assertEqual(3, len(responseJSON['waypoints']))

    def test_delete(self):
        response = self.app.post('/trip/', data=json.dumps(dict(
            name='San Fran',
            waypoints=['russian hill', 'pac heights', 'sunset'])),
            content_type='application/json')

        postResponseJSON = json.loads(response.data.decode())
        postedObjectID = postResponseJSON['_id']

        del_response = self.app.delete('/trip/'+postedObjectID)

        self.assertEqual(del_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
