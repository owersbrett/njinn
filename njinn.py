
import json
import os
import http.client
import sys
import datetime
import logging

directive = { 
    "content": """
    I communicate in three sentences max. 
    I don't use new line characters. 
    I am an expert solutions architect, how may I serve you?""", "role": "system"}
user_input = ""
today = datetime.date.today()
date_dir = str(today.year) + "/" + str(today.month) + "/" + str(today.day) + "/"

logging.basicConfig()
log = logging.getLogger("ai_terminal_helper")
# log.setLevel(logging.INFO)
# log.setLevel(logging.DEBUG)
base_url = "https://api.openai.com/v1/chat/completions"
openai_apikey = os.getenv('OPENAI_API_KEY')
base_log_file_path = os.getenv('AI_LOG_PATH')

class API:
    base_url = "api.openai.com"
    def headers(self):
        return {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_apikey}"
                }
    def post(self, messages):
        data = {
                    "model": "gpt-3.5-turbo-0125",
                    "messages": messages,
                    "temperature": 0.7
                }
        data = json.dumps(data).encode("utf-8")
        conn = http.client.HTTPSConnection(self.base_url)

        conn.request("POST", "/v1/chat/completions", data, self.headers())
        res = conn.getresponse()
        data = res.read()
        log.info(data)
        decoded_data = data.decode("utf-8")
        json_data = json.loads(decoded_data)
        if "error" in json_data:
            raise Exception(json_data["error"])
        return json_data

# Ensure OPENAI_API_KEY is set in your environment variables


# Conversation log file path
base_log_file_path = "/Users/bowers/scripts/mount/logs/"
file_name = "conversation.jsonl"

def get_file_path():
    date_dir = str(datetime.date.today().year) + "/" + str(datetime.date.today().month) + "/" + str(datetime.date.today().day) + "/"
    return base_log_file_path + date_dir + file_name

def get_last_messages(newest_message):
    n = 10  # or any other number representing the conversation context size you want
    messages = []
    try:
        with open(get_file_path(), "r") as log_file:
            for line in reversed(list(log_file)):
                if len(messages) >= n:
                    break
                message = json.loads(line.strip())
                messages.append(message)
    except FileNotFoundError:
        log.info("File not found. Creating it.")

    messages = list(reversed(messages))  # Reverse again to maintain chronological order
    messages.insert(0, directive)  # Prepend directive message if needed
    messages.append({"content": newest_message, "role": "user"})  # Append the new user message

    log.debug(f"messages with prompt: \n{messages}\n")
    return messages




def append_to_log(user_input, ai_response):
    """Append the structured messages to the conversation log in JSONL format."""
    path = os.path.dirname(get_file_path())
    try:
        os.makedirs(path, exist_ok=True)
        with open(get_file_path(), "a") as log_file:
            # Write user input and system response as JSON objects
            user_message = json.dumps({"content": user_input, "role": "user"})
            ai_message = json.dumps({"content": ai_response, "role": "system"})
            log_file.write(f"{user_message}\n")  # User
            log_file.write(f"{ai_message}\n")    # System
    except Exception as e:
        log.error(f"Failed to append to log: {e}")



def generate_prompt():
    """Generate the prompt with preloaded conversation context and user input."""
    user_input = " ".join(sys.argv[1:])
    return user_input


def ask_openai(messages):
    log.debug(messages)
    api = API()
    log.debug("Response")
    res = api.post(messages=messages)
    log.debug(res)
    response_content = res["choices"][0]["message"]["content"]

    return response_content
    # return choice.message.content

def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            print(line)

def delete_last_two_lines(file_path):
    log.info("""Delete the last two lines from the specified file.""")
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Check if the file has at least two lines to delete
    if len(lines) >= 2:
        # Remove the last two lines
        log.info("Deleting last two lines")
        log.info(lines[-2:])
        lines = lines[:-2]
    else:
        # If the file has fewer than two lines, clear it
        lines = []
    
    # Write the remaining lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)    

def main():
    if '-d' in sys.argv:
        log.info("delete")
        delete_last_two_lines(get_file_path())
    elif '-l' in sys.argv:
        log.info("logs")
        read_file(get_file_path())
    elif '-i' in sys.argv or len(sys.argv) == 1:
        log.info("interactive")
        while True:
            custom_prompt = input("Enter your prompt: ")
            if custom_prompt == "exit":
                break
            messages = get_last_messages(custom_prompt)
            response = ask_openai(messages)
            log.info(str(response))
            append_to_log(custom_prompt, response)
            print(response)
    else:
        log.debug("delete flag is not set")   
        custom_prompt = " ".join(sys.argv[1:])
        print(custom_prompt)
        log.info(custom_prompt)
        messages = get_last_messages(custom_prompt)
        response = ask_openai(messages)
        log.info(str(response))
        append_to_log(custom_prompt, response)
        print(response)

if __name__ == "__main__":
    main()
