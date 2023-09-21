null = None
events = [
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": null,
        "function_call": {
          "name": "integrate_google_searches",
          "arguments": ""
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "{\n"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": " "
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": " \""
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "keywords"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "\":"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": " \""
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "El"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "iran"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": " Wong"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "\"\n"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "}"
        }
      },
      "finish_reason": null
    }
  ]
},
{
  "id": "chatcmpl-80uNudhwznSPoOflCoKaKQZVGA531",
  "object": "chat.completion.chunk",
  "created": 1695227434,
  "model": "gpt-3.5-turbo-16k-0613",
  "choices": [
    {
      "index": 0,
      "delta": {},
      "finish_reason": "function_call"
    }
  ]
},
]

func_name = ""
func_args = ""
for event in events:
    delta = event["choices"][0]["delta"]
    if not func_name and delta and delta.get("function_call") and delta["function_call"].get("name"):
        func_name += delta["function_call"]["name"]
    if delta and delta.get("function_call"):
        func_args += delta["function_call"]["arguments"]

print(func_name)
print(func_args)