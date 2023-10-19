import config, openai, platform, subprocess, os, pydoc, webbrowser

class SharedUtil:

    @staticmethod
    def getSingleResponse(userInput, temperature=None):
        try:
            completion = openai.ChatCompletion.create(
                model=config.chatGPTApiModel,
                messages=[{"role": "user", "content" : userInput}],
                n=1,
                temperature=temperature if temperature is not None else config.chatGPTApiTemperature,
                max_tokens=config.chatGPTApiMaxTokens,
            )
            return completion.choices[0].message.content
        except:
            return ""

    @staticmethod
    def isPackageInstalled(package):
        whichCommand = "where.exe" if platform.system() == "Windows" else "which"
        try:
            isInstalled, *_ = subprocess.Popen("{0} {1}".format(whichCommand, package), shell=True, stdout=subprocess.PIPE).communicate()
            return True if isInstalled else False
        except:
            return False

    @staticmethod
    def getCliOutput(cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    @staticmethod
    def textTool(tool="", content=""):
        if tool and SharedUtil.isPackageInstalled(tool):
            pydoc.pipepager(content, cmd=tool)
            if SharedUtil.isPackageInstalled("pkill"):
                tool = tool.strip().split(" ")[0]
                os.system(f"pkill {tool}")
        return ""

    @staticmethod
    def runSystemCommand(command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout  # Captured standard output
        error = result.stderr  # Captured standard error
        response = ""
        response += f"# Output:\n{output}"
        if error.strip():
            response += f"\n# Error:\n{error}"
        return response

    @staticmethod
    def openURL(url):
        config.stopSpinning()
        if config.terminalEnableTermuxAPI:
            command = f'''termux-open-url "{url}"'''
            SharedUtil.runSystemCommand(command)
        else:
            webbrowser.open(url)