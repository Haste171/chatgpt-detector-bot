from gptzero import GPTZeroAPI

api_key = 'b2102ef5c89d46c8bfc2b16b99cf2c87' # Your API Key from https://gptzero.me
gptzero_api = GPTZeroAPI(api_key)

document = 'Hello world!'
response = gptzero_api.text_predict(document)
print(response)