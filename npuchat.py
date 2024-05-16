import configparser
import os
import re
import requests
import threading
import time
from flask import Flask, render_template, request, jsonify
from requests.exceptions import Timeout

APPNAME = 'NPU Chat'
VERSION = '0.26'


def contains_chinese(text: str) -> bool:
    """
    Detect if a string contains Chinese characters.

    Args:
        text (str): The input string to check.

    Returns:
        bool: True if the string contains Chinese characters, False otherwise.
    """
    pattern = r'[\u4e00-\u9fff]+'
    if re.search(pattern, text):
        return True
    else:
        return False

def feed_the_llama(query: str) -> str:
    """
    Send the user's query to the NPU server and modify it if context is being
    used.

    If you're using chat context, the Qwen model appears to differentiate
    between codeblocks (3 backticks in markdown) and plain text outside of
    these blocks. Let's take this exchange for example:
        user: how many crayons?
        llm: there are three crayons

    On the next query, the user's query to the LLM
    ('which colors are they?') would become:
        ```
        there are three crayons
        ```
        which colors are they?

    The model appears to 'know' that the text outside the codeblock is
    referencing what's inside of it.

    To see this in action, uncomment the print statement below and perform
    a query. In my tests this method seems be sufficient to maintain context.
    If you have a better idea please open an issue or make a PR.

    Args:
        query (str): The user's input string.

    Returns:
        str: Answer from the LLM.
    """

    if USE_CHAT_CONTEXT:
        if CONTEXT: # if context history isn't empty
            # compile the history into individual codeblocks
            llm_output_history = ""
            for llm_reply in CONTEXT: # format into markdown codeblocks
                llm_output_history = (
                    f"{llm_output_history}"
                    f"```\n"
                    f"{llm_reply}"
                    f"\n```\n"
                )
            query = llm_output_history + query # append user's query
            #print(f"\ncontext:\n\n{query}\n\n")

    # prompt template:
    prefix = (
        "<|im_start|>system You are a helpful assistant. <|im_end|> "
        "<|im_start|>user "
    )

    postfix = (
        "<|im_end|><|im_start|>assistant "
    )

    # create the request object
    json_data = {
        'PROMPT_TEXT_PREFIX': prefix,
        'input_str': str(query) + ' ',
        'PROMPT_TEXT_POSTFIX': postfix,
    }

    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(
            f"http://{NPU_ADDRESS}:{NPU_PORT}",
            headers=headers,
            json=json_data,
            timeout=CONNECTION_TIMEOUT
        )

        response.raise_for_status() # throw exception on non 2xx HTTP statuses

        response = response.json() # get JSON from response

        answer = response['content'] # text of the LLM's response

        return answer # return text to client

    # handle errors for better user-friendliness
    except Timeout:
        return "Request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        error_msg = (
            f"An error occurred: {str(e)}"
            f" ---- is the server online?"
        )
        return error_msg

def web_server() -> None:
    """
    Sets up the Flask server and handles web requests.
    """

    # print the server details to the console
    print(
        f"Starting server at: "
        f"http://{BINDING_ADDRESS}:{BINDING_PORT}"
    )
    app = Flask(__name__)
    app.name = f"{APPNAME} v{VERSION}"

    # serve the UI to the user
    @app.route('/', methods=['GET', 'POST'])
    def index():
        response = app.make_response(render_template('index.html'))
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = (
            'no-cache, no-store, must-revalidate'
        )
        return response

    # endpoint (http://your-ip/search)
    @app.route('/search', methods=['POST'])
    def web_request():
        response = app.make_response(jsonify(web_request_logic()))
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = (
            'no-cache, no-store, must-revalidate'
        )
        return response

    def web_request_logic():

        global USE_CHAT_CONTEXT
        global CONTEXT

        # start recording response time
        start_time = time.time()

        # get web input
        question = request.form['input_text']

        # commands for manipulating context state
        if question.lower() == 'clear': # erase context
            CONTEXT = [] # initialize the context list
            return {'content': "context cleared."}
        if question.lower() == 'off': # turn it off
            CONTEXT = [] # initialize the context list
            USE_CHAT_CONTEXT = False
            return {'content': "context off."}
        if question.lower() == 'on': # turn it on
            USE_CHAT_CONTEXT = True
            return {'content': "context on."}

        print(f"━━━━━━━━┫ Received request: {question}")

        # if lock is acquired then this app is currently in use.
        # we can currently only handle one request at a time.
        if lock.locked():
            error_msg = "Sorry, I can only handle one request "\
                        "at a time and I'm currently busy."
            return {
                    'result': error_msg
            }

        # if this app is free to process a request
        with lock:
            answer = feed_the_llama(question) # send to npu server

        # update chat context
        if USE_CHAT_CONTEXT:

            ignore_chinese_chars = False

            # check if user wants to ignore Chinese characters
            if IGNORE_CHINESE:
                ignore_chinese_chars = contains_chinese(answer)

            # update context history
            if not ignore_chinese_chars:
                CONTEXT.append(answer)

                # trim context to desired depth by removing oldest element
                if len(CONTEXT) > CONTEXT_DEPTH:
                    CONTEXT.pop(0)

        # modify the answer for markdown HTML tag to make it pretty
        answer = (
            f"<md class='markdown-style'>"
            f"{answer}"
            f"</md>"
        )

        # print completed time
        end_time = time.time()
        print(f"Completed in {end_time - start_time:.2f} seconds.")

        # return answer to client
        answer_markdown = {'content': answer}
        return answer_markdown

    # setup Flask
    app.run(
        host=BINDING_ADDRESS,
        port=BINDING_PORT
    )

def load_config(script_dir: str) -> None:
    """
    Loads user settings from settings.ini into globals

    Args:
        script_dir (str): The working directory of this script.

    Returns:
        None
    """

    # if script path doesn't have trailing slash
    if script_dir[-1] != '/':
        script_dir = script_dir + "/" # add it

    # get current working directory of this script to find settings.ini
    config_path = f"{script_dir}settings.ini"

    # parse settings.ini
    parser = configparser.ConfigParser()
    parser.read(config_path)

    # globals for settings
    global BINDING_ADDRESS
    global BINDING_PORT
    global NPU_ADDRESS
    global NPU_PORT
    global CONNECTION_TIMEOUT
    global USE_CHAT_CONTEXT
    global CONTEXT_DEPTH
    global IGNORE_CHINESE

    # assign settings. str unless noted otherwise
    BINDING_ADDRESS = parser.get('chat_ui', 'BINDING_ADDRESS')
    BINDING_PORT = parser.get('chat_ui','BINDING_PORT')
    NPU_ADDRESS = parser.get('npu','NPU_ADDRESS')
    NPU_PORT = parser.get('npu','NPU_PORT')
    CONNECTION_TIMEOUT = int(
        parser.get('timeout','TIMEOUT')
    ) # int

    USE_CHAT_CONTEXT = parser.get('context','USE_CONTEXT') # bool
    CONTEXT_DEPTH = int(
        parser.get('context','DEPTH')
    ) # int
    IGNORE_CHINESE = parser.get('context','IGNORE_CHINESE') # bool

if __name__ == "__main__":

    # get cwd of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # load user settings
    load_config(script_dir)

    # control access since currently only one instance can run at a time
    lock = threading.Lock()

    # context / chat history
    CONTEXT = []

    # start Flask
    web_server()
