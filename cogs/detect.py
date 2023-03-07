import interactions
from interactions import (
    Client,
    CommandContext,
    ComponentContext,
    Modal,
    TextInput,
    TextStyleType,
    Button,
)
from dotenv import load_dotenv
from gptzero import GPTZeroAPI
import sys
import os
import requests

sys.path.append('../')
load_dotenv()



class Detect(interactions.Extension):
    def __init__(self, client):
        self.client: Client = client

    @interactions.extension_command()
    async def detect(self, ctx: CommandContext): # Make sure the type of variable is the same 
        """Attempt to detect whether or not given text was written by an AI or not""" # Command description that shows on Discord when using the command

        modal = Modal(
            custom_id="modal1",
            title="AI Detect",
            components=[
                TextInput(
                    style=TextStyleType.PARAGRAPH,
                    custom_id="text-input-2",
                    label="Paste text below",
                    min_length=250,
                ),
            ],
        )
        await ctx.popup(modal)

    @interactions.extension_modal("modal1")
    async def modal2(self, ctx: CommandContext, res: str):
        await ctx.defer()

        # GPTZERO
        api_key = os.environ.get('GPTZERO_API_KEY') # Your API Key from https://gptzero.me
        gptzero_api = GPTZeroAPI(api_key)

        def predict(document):
            return gptzero_api.text_predict(document)
        gz_detector = predict(res)
        documents = gz_detector['documents']
        document = documents[0]  # assume there is only one document in the list
        completely_generated_prob = document['completely_generated_prob']
        overall_burstiness = document['overall_burstiness']

        # HuggingFace
        class HF:
            def __init__(self, text):
                self.text = text
                self.url = "https://openai-openai-detector.hf.space/"
                self.headers = {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive",
                    "Cookie": "session-space-cookie=54b58a19a8ae5fd3d91291c9b157b6c9",
                    "DNT": "1",
                    "Host": "openai-openai-detector.hf.space",
                    "Referer": "https://openai-openai-detector.hf.space/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-GPC": "1",
                    "TE": "trailers",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"
                }

            def get_prediction(self):
                query_string = f"?{self.text}"
                response = requests.get(self.url + query_string, headers=self.headers)
                return response.json()

        hf_detector = HF(res)
        hf_response = hf_detector.get_prediction()
        real_prob = hf_response["real_probability"] * 100
        fake_prob = hf_response["fake_probability"] * 100

        tokens = hf_response["used_tokens"]
        embed = interactions.Embed(title='Detector',description=f'📌 [Invite This Bot](https://discord.com/api/oauth2/authorize?client_id=1082531996850462720&permissions=8&scope=bot) | [Support Server](https://discord.gg/Ysbks3eMHA)\n📌 Just because one detector does not find something to be AI written does not mean another is incorrect! *Combine all the information together...*')

        if completely_generated_prob > 0.5:
            print('1')
            embed.add_field(name='GPTZero Result', value=f':bangbang: The entire content was most likely generated by an AI model.\nOverall Burstiness: {overall_burstiness}', inline=True)
        if completely_generated_prob < 0.5:
            if completely_generated_prob >= 0.21:
                embed.add_field(name='GPTZero Result', value=f':warning: The content may have been partially based on input or other sources.\nOverall Burstiness: {overall_burstiness}', inline=True)
                print('2')
        if completely_generated_prob < 0.2:
            embed.add_field(name='GPTZero Result', value=f':white_check_mark: The entire content was likely written by a Human.\nOverall Burstiness: {overall_burstiness}', inline=True)
            print('3')
        embed.add_field(name='HuggingFace Result', value=f':thumbsup: Real probability: {real_prob:.2f}%\n:thumbsdown: Fake probability: {fake_prob:.2f}%', inline=True)

        embed.set_footer(text="ChatGPT Detector 1.0", icon_url='https://cdn.discordapp.com/attachments/908374960454631454/1082557878667321394/detector-logo.png')
        await ctx.send(embeds=embed)


def setup(client):
    Detect(client)
