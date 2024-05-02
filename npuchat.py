import configparser
import logging
import markdown
import os
import requests
import threading
import time
from flask import Flask, render_template, request, jsonify

APPNAME = 'NPU Chat'
VERSION = '0.1'


def feed_the_llama(query: str) -> str:

    headers = {
        'Content-Type': 'application/json',
    }

    prefix = (
        "<|im_start|>system You are a helpful assistant. <|im_end|> "
        "<|im_start|>user "
    )

    postfix = (
        "<|im_end|><|im_start|>assistant "
    )

    json_data = {
        'PROMPT_TEXT_PREFIX': prefix,
        'input_str': str(query) + ' ',
        'PROMPT_TEXT_POSTFIX': postfix,
    }

    response = requests.post(
        f"http://{NPU_ADDRESS}:{NPU_PORT}",
        headers=headers,
        json=json_data
    )

    response = response.json()

    answer = response['content']

    answer = (
        f"<md class='markdown-style'>"
        f"{answer}"
        f"</md>"
    )

    return answer

def web_server() -> None:

    print(
        f"Starting server at: "
        f"http://{BINDING_ADDRESS}:{BINDING_PORT}"
    )

    app = Flask(__name__)
    app.name = f"{APPNAME} v{VERSION}"

    @app.route('/', methods=['GET', 'POST'])
    def index():
        response = app.make_response(render_template('index.html'))
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    @app.route('/search', methods=['POST'])
    def web_search():
        response = app.make_response(jsonify(web_search_logic()))
        response.headers['Pragma'] = 'no-cache'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response

    def web_search_logic():
        start_time = time.time()

        question = request.form['input_text']
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
            answer = feed_the_llama(question) # send to npu

        end_time = time.time()
        print(f"Completed in {end_time - start_time:.2f} seconds.")

        answer_markdown = {'content': answer}
        return answer_markdown

    app.run(
        host=BINDING_ADDRESS,
        port=BINDING_PORT
    )

def load_config(script_dir: str) -> None:

    # if script path doesn't have trailing slash
    if script_dir[-1] != '/':
        script_dir = script_dir + "/" # add it

    config_path = f"{script_dir}settings.ini"

    parser = configparser.ConfigParser()
    parser.read(config_path)

    global BINDING_ADDRESS
    global BINDING_PORT
    global NPU_ADDRESS
    global NPU_PORT

    BINDING_ADDRESS = parser.get('chat_ui', 'BINDING_ADDRESS')
    BINDING_PORT = parser.get('chat_ui','BINDING_PORT')
    NPU_ADDRESS = parser.get('npu','NPU_ADDRESS')
    NPU_PORT = parser.get('npu','NPU_PORT')

if __name__ == "__main__":

    # get cwd of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # load user settings
    load_config(script_dir)

    # control access since currently only one instance can run at a time
    lock = threading.Lock()

    # start Flask
    web_server()
