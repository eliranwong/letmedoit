from myhand import config
import traceback
from myhand.utils.install import *
from myhand.utils.shared_utils import SharedUtil

"""
My Hand Bot Plugin - auto heal python code

functionalities:
* install missing packages
* fixed broken codes

User can define the maximum number of auto-healing attempts by editing "max_consecutive_auto_heal" in config.py.
The default value of config.max_consecutive_auto_heal is 3.

[FUNCTION_CALL]
"""

def heal_python(function_args):
    # get the sql query statement
    fix = function_args.get("fix") # required
    missing = function_args.get("missing") # required
    if isinstance(missing, str):
        missing = eval(missing)

    try:
        if missing:
            for i in missing:
                installmodule(f"--upgrade {i}")
        exec(SharedUtil.fineTunePythonCode(fix), globals())
        return "EXECUTED"
    except:
        return traceback.format_exc()

functionSignature = {
    "name": "heal_python",
    "description": "Fix python code if both original code and traceback error are provided",
    "parameters": {
        "type": "object",
        "properties": {
            "fix": {
                "type": "string",
                "description": "Improved version of python code that resolved the traceback error. Return the original code instead only if traceback shows an import error.",
            },
            "missing": {
                "type": "string",
                "description": """List of missing packages identified from import errors, e.g. "['datetime', 'requests']". Return "[]" if there is no import error in the traceback.""",
            },
        },
        "required": ["fix", "missing"],
    },
}

# configs particular to this plugin
# persistent
persistentConfigs = (
    ("max_consecutive_auto_heal", 3),
)
config.setConfig(persistentConfigs)

config.pluginsWithFunctionCall.append("heal_python")
config.heal_python_signature = [functionSignature]
config.chatGPTApiFunctionSignatures.append(functionSignature)
config.chatGPTApiAvailableFunctions["heal_python"] = heal_python