import config, json, openai, os
from base64 import b64decode

def generate_image(function_args):
    prompt = function_args.get("prompt") # required
    try:
        # get responses
        #https://platform.openai.com/docs/guides/images/introduction
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )
        # open image
        #imageUrl = response['data'][0]['url']
        jsonFile = os.path.join("temp", "openai_image.json")
        with open(jsonFile, mode="w", encoding="utf-8") as fileObj:
            json.dump(response, fileObj)
        imageFile = os.path.join("temp", "openai_image.png")
        with open(jsonFile, mode="r", encoding="utf-8") as fileObj:
            jsonContent = json.load(fileObj)
            image_data = b64decode(jsonContent["data"][0]["b64_json"])
            with open(imageFile, mode="wb") as pngObj:
                pngObj.write(image_data)
        if config.terminalEnableTermuxAPI:
            config.mainWindow.getCliOutput(f"termux-share {imageFile}")
        else:
            os.system(f"{config.open} {imageFile}")

    except openai.error.APIError as e:
        print("Error: Issue on OpenAI side.")
        print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
    except openai.error.Timeout as e:
        print("Error: Request timed out.")
        print("Solution: Retry your request after a brief wait and contact us if the issue persists.")
    except openai.error.RateLimitError as e:
        print("Error: You have hit your assigned rate limit.")
        print("Solution: Pace your requests. Read more in OpenAI [Rate limit guide](https://platform.openai.com/docs/guides/rate-limits).")
    except openai.error.APIConnectionError as e:
        print("Error: Issue connecting to our services.")
        print("Solution: Check your network settings, proxy configuration, SSL certificates, or firewall rules.")
    except openai.error.InvalidRequestError as e:
        print("Error: Your request was malformed or missing some required parameters, such as a token or an input.")
        print("Solution: The error message should advise you on the specific error made. Check the [documentation](https://platform.openai.com/docs/api-reference/) for the specific API method you are calling and make sure you are sending valid and complete parameters. You may also need to check the encoding, format, or size of your request data.")
    except openai.error.AuthenticationError as e:
        print("Error: Your API key or token was invalid, expired, or revoked.")
        print("Solution: Check your API key or token and make sure it is correct and active. You may need to generate a new one from your account dashboard.")
    except openai.error.ServiceUnavailableError as e:
        print("Error: Issue on OpenAI servers. ")
        print("Solution: Retry your request after a brief wait and contact us if the issue persists. Check the [status page](https://status.openai.com).")
    except:
        config.showErrors()


functionSignature = {
    "name": "generate_image",
    "description": "create an image",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "description about the image",
            },
        },
        "required": ["prompt"],
    },
}

config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["generate_image"] = generate_image