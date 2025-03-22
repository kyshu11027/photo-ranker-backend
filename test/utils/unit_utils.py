import json
import requests

class UnitTestUtils():
    
    def load_sample_event_from_file(self, test_event_file_name: str) ->  dict:
        """
        Loads and validate test events from the file system
        """
        event_file_name = f"test/events/{test_event_file_name}.json"
        with open(event_file_name, "r", encoding='UTF-8') as file_handle:
            event = json.load(file_handle)
            return event

    def get_test_jwt(self, auth0_domain, client_id, client_secret, api_audience):
        try:
            tokenResponse = requests.post(f'{auth0_domain}/oauth/token', data={
                'client_id': client_id,
                'client_secret': client_secret,
                'audience': api_audience,
                'grant_type': 'client_credentials'  # Missing grant type added
            })
            print("Response Status:", tokenResponse.status_code)
            print("Response Body:", tokenResponse.text)
            
            tokenResponse.raise_for_status()  # Ensure request was successful
            access_token = tokenResponse.json().get('access_token')

            if not access_token:
                raise Exception('Token response did not contain an access token')
            
            return access_token
        except requests.RequestException as e:
            raise