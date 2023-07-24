# Replace "your_openai_api_key" in the ".env" file to your actual OpenAI API key.

# To run the program: python debug.py <file_path>

import subprocess
import sys
import openai
import time
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")


def log_attempt(attempt_num, code, error_output, suggested_fix):
    with open("debug_log.txt", "a") as log_file:
        log_file.write(f"Attempt {attempt_num}\n")
        log_file.write("Original Code:\n")
        log_file.write(code)
        log_file.write("\nError Output:\n")
        log_file.write(error_output.decode("utf-8"))
        log_file.write("\nSuggested Fix:\n")
        log_file.write(suggested_fix)
        log_file.write("\n-----------------------------------\n")


def user_accepts_fix():
    user_response = input("Do you want to apply the suggested fix? (yes/no): ")
    return user_response.lower().strip() == "yes"


def run_python_script(file_path):
    try:
        output = subprocess.check_output(["python3", file_path])
        return True, output
    except subprocess.CalledProcessError as e:
        return False, e.output


def fix_code(code, error_output):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an exceptional Python programmer, and your purpose is to assist in resolving issues in Python code."
            },
            {
                "role": "user",
                "content": f"Python code and the error message that appeared in the Terminal:\n\n{code}\n\n{error_output}\n\nYou'll offer the corrected Python code without any additional text. Just share the code to avoid any interference with the debugging process."
            }
        ]
    )
    return response['choices'][0]['message']['content']


def auto_debug_python_script(target_file, max_attempts=5, retry_delay=2):
    for attempt in range(1, max_attempts + 1):
        success, output = run_python_script(target_file)
        if success:
            print("✅ Python script ran successfully!")
            break
        else:
            print(f"❌ Attempt {attempt}: Error encountered")
            print(output.decode("utf-8"))

            with open(target_file, "r") as f:
                original_code = f.read()

            fixed_code = fix_code(original_code, output.decode("utf-8"))
            print(f"💡 Suggested Fix:\n{fixed_code}\n")

            log_attempt(attempt, original_code, output, fixed_code)

            print("❗️ Error Highlighting:")
            lexer = PythonLexer()
            formatter = TerminalFormatter()
            highlighted_code = highlight(original_code, lexer, formatter)
            print(highlighted_code)

            if user_accepts_fix():
                with open(target_file, "w") as f:
                    f.write(fixed_code)
                print("🔧 Applied the suggested fix.")
                break
            else:
                print("⚙️ Proceeding to the next attempt...")
                time.sleep(retry_delay)

    if not success:
        print("⚠️ Run this script again.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Use: python debug.py <file_path>")
        sys.exit(1)

    target_file = sys.argv[1]
    if not os.path.isfile(target_file):
        print("File does not exist.")
        sys.exit(1)

    print("🔍 Auto-debugging the Python script...")
    auto_debug_python_script(target_file)