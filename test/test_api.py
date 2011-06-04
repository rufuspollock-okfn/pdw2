from flask import json, url_for
from pdw2.web import app

class TestApi:
    def setup(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/api')
        assert 'API' in response.data

    def _make_query(self, jurisdiction, work):
        return '/api/pd?jurisdiction=%s&work=%s' % (jurisdiction,
                json.dumps(work))

    def test_pd(self):
        params = {
            'jurisdiction': 'uk'
        }
        params_json = json.dumps(params)
        url = self._make_query('fr', {
            'type': 'literary',
            'title': 'A Christmas Carol',
            'date': '1953'
            })
        response = self.app.get(url)
        out = json.loads(response.data)
        print response.data
        assert out['fr']['pd'] == False, response.data

    def test_pd_with_other_dates(self):
        work = {
            "date": "19030101", 
            "when": "19230101", 
            "persons": [
                {
                    "birth_date": "17490101", 
                    "country": "uk", 
                    "death_date": "None", 
                    "type": "person", 
                    "name": "Boyle, James"
                }
            ], 
            "type": "literary", 
            "title": "Collected Papers on the Public Domain (ed)"
        }
        url = self._make_query('uk', work)
        response = self.app.get(url)
        out = json.loads(response.data)
        # TODO: null does not seem right
        assert out['uk']['pd'] == None, response.data

