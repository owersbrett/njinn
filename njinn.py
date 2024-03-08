
import os
import requests
import sys
import datetime
import logging


user_input = ""
context_messages = []
today = datetime.date.today()
date_dir = str(today.year) + "/" + str(today.month) + "/" + str(today.day) + "/"

logging.basicConfig()
log = logging.getLogger("ai_terminal_helper")
log.setLevel(logging.INFO)
base_url = "https://api.openai.com/v1/chat/completions"
openai_apikey = os.getenv('OPENAI_API_KEY')
base_log_file_path = os.getenv('AI_LOG_PATH')

class API:
    def headers(self):
        return {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_apikey}"
                }
    def post(self, messages):
        data = {
                    "model": "gpt-4",
                    "messages": messages,
                    "temperature": 0.7
                }

        return requests.post(
                base_url, 
                headers=self.headers(),
                data=data
            )
        
        
def print_morning_message():
    log.info('Time is ' + str(today.ctime()) + "\n")


# Ensure OPENAI_API_KEY is set in your environment variables


# Conversation log file path
file_name = "conversation.log"

def get_file_path():
    date_dir = str(datetime.date.today().year) + "/" + str(datetime.date.today().month) + "/" + str(datetime.date.today().day) + "/"
    return base_log_file_path + date_dir + file_name

def get_last_messages(newest_message):
    n = 10
    log.debug("reading path: " + get_file_path())
    messages = []
    try:
        with open(get_file_path(), "r") as log_file:
            lines = log_file.readlines()
            # Ensuring we're getting the last N pairs of lines (system-user)
            mes = lines[-n*2:]
            if (len(mes) > 1 != 0):
                messages.append({"content": mes[0], "role": "user"})
                messages.append({"content": mes[1], "role": "system"})
    except FileNotFoundError:
        print_morning_message()
    log.debug("messages: " + str(messages) + "\n")
    dict = {"content": newest_message, "role": "user"}
    messages.append(dict)
    log.debug("messages with prompt: \n" + str(messages) + "\n")
    return messages


def append_to_log(user_input, ai_response):
    """Append the structured messages to the conversation log."""
    try:
        os.makedirs(os.path.dirname(get_file_path()), exist_ok=True)
        with open(get_file_path(), "a") as log_file:
            # Write system response (odd lines) and user input (even lines)
            log_file.write(f"{user_input}\n")    # User (odd)
            log_file.write(f"{ai_response}\n")  # System (even)
    except Exception as e:
        log.error(f"Failed to append to log: {e}")


def generate_prompt():
    """Generate the prompt with preloaded conversation context and user input."""
    user_input = " ".join(sys.argv[1:])
    return user_input

def convert_logs_to_dict(lines):
    """Convert every two lines in the log to a dict with roles based on line number parity."""
    logs_dict = []

    for i in range(0, len(lines), 2):
        user_lines = lines[i].strip()  # System (odd)
        try:
            user_line = lines[i+1].strip()  # User (even)
        except IndexError:
            user_line = ""  # In case of an odd number of lines, assume no user line

        entry = {
            "system": system_line,
            "user": user_line
        }
        logs_dict.append(entry)

    return logs_dict

def ask_openai(messages):
    log.debug(context_messages)
    api = API()
    log.debug("Response")
    res = api.post(context_messages)
    log.debug(res)
    # return choice.message.content

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

    else:
        log.debug("delete flag is not set")   
        custom_prompt = " ".join(sys.argv[1:])
        log.info(custom_prompt)
        messages = get_last_messages(custom_prompt)
        response = ask_openai(messages)
        log.info(str(response))
        respone_content = response["choices"][0]["message"]["content"]
        log.info(str(respone_content))
        # append_to_log(custom_prompt, respone_content)
        log.info(str(messages[-1]["content"]))
        log.info(str(messages[-2]["content"]))

    # for context_message in context_messages:
    #     user_message = context_messages[0]
    #     system_message = context_messages[1]
    # print(context_messages)

    # ai_response = ask_openai(custom_prompt, context_messages)
    # print(json.dumps({"role": "system", "content": ai_response}))
    # append_to_log(custom_prompt, ai_response)

if __name__ == "__main__":
    main()

# curl https://api.openai.com/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -d '{
#      "model": "gpt-3.5-turbo",
#      "messages": [{"role": "user", "content": "Say this is a test!"}],
#      "temperature": 0.7
#    }'
