import vertexai, os
from vertexai.preview.generative_models import GenerativeModel
from letmedoit import config
from letmedoit.health_check import HealthCheck
if not hasattr(config, "openaiApiKey") or not config.openaiApiKey:
    HealthCheck.setBasicConfig()
    HealthCheck.changeAPIkey()
    HealthCheck.saveConfig()
    print("Updated!")
HealthCheck.checkCompletion()
HealthCheck.setPrint()

# Install google-cloud-aiplatform FIRST!
#!pip install --upgrade google-cloud-aiplatform

# Keep for reference; unnecessary for api key authentication with json file
# (developer): Update and un-comment below lines
#project_id = "letmedoitai"
#location = "us-central1"
#vertexai.init(project=project_id, location=location)


class GeminiPro:

    def __init__(self):
        # authentication
        authpath1 = os.path.join(HealthCheck.getFiles(), "credentials_googleaistudio.json")
        if os.path.isfile(authpath1):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = authpath1
            self.runnable = True
        else:
            print(f"API key json file '{authpath1}' not found!")
            print("Read https://github.com/eliranwong/letmedoit/wiki/Google-API-Setup for setting up Google API.")
            self.runnable = False
        # initiation
        vertexai.init()

    def run(self, prompt=""):
        if not self.runnable:
            print("Gemini Pro is not running due to missing configurations!")
            return None
        model = GenerativeModel("gemini-pro")
        chat = model.start_chat()
        print("\nGemini Pro launched!")
        print("(To start a new chat, enter '.new')")
        print("(To quit, enter '.quit')")

        while True:
            print("------------------------------\n")
            print("Enter your prompt below:")
            if not prompt:
                prompt = input(">>> ")
                if prompt and not prompt in (".new", ".quit"):
                    config.currentMessages.append({"content": prompt, "role": "user"})
            else:
                print(f">>> {prompt}")
            print("")
            if prompt == ".quit":
                break
            elif prompt == ".new":
                chat = model.start_chat()
                print("New chat started!")
            elif prompt := prompt.strip():
                response = chat.send_message(prompt).text
                print(response)
                if hasattr(config, "currentMessages"):
                    config.currentMessages.append({"content": response, "role": "assistant"})
            prompt = ""
            print("")
        print("------------------------------")
        print("Gemini Pro closed!")

def main():
    GeminiPro().run()

if __name__ == '__main__':
    main()