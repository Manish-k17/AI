import json
import platform
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import pyautogui
import time
from typing import Optional, List

# --- Configuration ---
GROQ_API_KEY = "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"

# --- Helper Functions (used by GroqAutomation methods) ---

def _google_search_web(topic: str) -> bool:
    try:
        search(topic)
        print(f"Performed Google search for: {topic}")
        return True
    except Exception as e:
        print(f"Error performing Google search: {e}")
        return False

def _Youtube_web(topic: str) -> bool:
    try:
        url = f"https://www.youtube.com/results?search_query={topic}"
        webbrowser.open(url)
        print(f"Performed Youtube for: {topic}")
        return True
    except Exception as e:
        print(f"Error performing Youtube: {e}")
        return False

def _play_youtube_video(query: str) -> bool:
    try:
        playonyt(query)
        print(f"Playing YouTube video: {query}")
        return True
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return False

def _open_notepad_with_file(filepath: str) -> bool:
    try:
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, filepath])
        print(f"Opened {filepath} in Notepad.")
        return True
    except Exception as e:
        print(f"Error opening notepad: {e}")
        return False

def _system_command_execute(command: str) -> bool:
    try:
        if command == "mute" or command == "unmute":
            pyautogui.press("volume mute")
        elif command == "volume up":
            pyautogui.press("volumeup")
        elif command == "volume down":
            pyautogui.press("volumedown")
        else:
            print(f"Unknown system command: {command}")
            return False
        print(f"Executed system command: {command}")
        return True
    except Exception as e:
        print(f"Error executing system command {command}: {e}")
        return False

# --- Groq Automation Class ---

class GroqAutomation:
    def __init__(self):
        self.groq_client = None
        if GROQ_API_KEY:
            self.groq_client = Groq(api_key=GROQ_API_KEY)
        else:
            print("Warning: GROQ_API_KEY not found. Groq functions will not work.")

        pyautogui.FAILSAFE = True
        self.screen_width, self.screen_height = pyautogui.size()
        self.messages = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}, a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems, etc."}]


    def _query_groq(self, prompt: str) -> Optional[str]:
        if not self.groq_client:
            return "Error: Groq client not initialized (API key missing)."

        current_conversation_messages = self.messages + [{"role": "user", "content": prompt}]

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=current_conversation_messages,
                max_tokens=2048,
                temperature=0.7,
                top_p=1,
                stream=False,
                stop=None
            )
            response_content = completion.choices[0].message.content
            self.messages.append({"role": "assistant", "content": response_content})
            return response_content
        except Exception as e:
            print(f"Error querying Groq API: {e}")
            return f"Error: Unable to get response from Groq - {str(e)}"

    def _search_and_open_web_app(self, app_name: str) -> bool:
        sess = requests.session()
        headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}

        def extract_links(html_content: str) -> List[str]:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a', href=True)
            return [link.get('href') for link in links]

        def search_microsoft_store(query: str) -> Optional[str]:
            url = f"https://www.microsoft.com/en-us/search?q={query}"
            try:
                response = sess.get(url, headers=headers)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Failed to retrieve search results from Microsoft Store: {e}")
                return None

        def open_in_chrome_beta(url: str) -> bool:
            system = platform.system()
            try:
                if system == "Windows":
                    chrome_beta_paths = [
                        r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome Beta\Application\chrome.exe")
                    ]
                    for path in chrome_beta_paths:
                        if os.path.exists(path):
                            subprocess.Popen([path, url])
                            print(f"Opened {url} in Chrome Beta.")
                            return True
                    chrome_stable_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                    ]
                    for path in chrome_stable_paths:
                        if os.path.exists(path):
                            subprocess.Popen([path, url])
                            print(f"Chrome Beta not found, opened {url} in stable Chrome.")
                            return True
                elif system == "Darwin":
                    try:
                        subprocess.run(["open", "-a", "Google Chrome Beta", url], check=True)
                        print(f"Opened {url} in Chrome Beta.")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        subprocess.run(["open", "-a", "Google Chrome", url], check=True)
                        print(f"Chrome Beta not found, opened {url} in stable Chrome.")
                        return True
                elif system == "Linux":
                    try:
                        subprocess.run(["google-chrome-beta", url], check=True)
                        print(f"Opened {url} in Chrome Beta.")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        subprocess.run(["google-chrome", url], check=True)
                        print(f"Chrome Beta not found, opened {url} in stable Chrome.")
                        return True

                webbrowser.open(url)
                print(f"Chrome not found, opened {url} in default browser.")
                return True
            except Exception as e:
                print(f"Error opening browser: {e}")
                webbrowser.open(url)
                return True

        html = search_microsoft_store(app_name)
        if html:
            links = extract_links(html)
            if links:
                filtered_links = [link for link in links if "microsoft.com" in link or "store.steampowered.com" in link or "play.google.com/store" in link]
                if filtered_links:
                    link_to_open = filtered_links[0]
                    return open_in_chrome_beta(link_to_open)
                else:
                    print(f"No relevant links found for {app_name} in search results.")
                    return False
            else:
                print(f"No links extracted from search for {app_name}.")
                return False
        return False

    def open_app(self, app_name: str) -> bool:
        print(f"Attempting to open application: {app_name}")
        try:
            appopen(app_name, match_closest=True, output=True, throw_error=True)
            print(f"Successfully opened system app: {app_name}")
            return True
        except Exception as e:
            print(f"Could not open system app '{app_name}' using AppOpener: {e}. Attempting web search...")
            return self._search_and_open_web_app(app_name)

    def close_app(self, app_name: str) -> bool:
        print(f"Attempting to close application: {app_name}")
        if "chrome" in app_name.lower():
            try:
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], check=True)
                print(f"Closed Chrome using taskkill.")
                return True
            except Exception as e:
                print(f"Could not close Chrome with taskkill: {e}. Trying AppOpener...")
        
        try:
            close(app_name, match_closest=True, output=True, throw_error=True)
            print(f"Closed {app_name} using AppOpener.")
            return True
        except Exception as e:
            print(f"Error closing {app_name}: {e}")
            return False

    def send_whatsapp_message(self, contact: str, message: str) -> bool:
        print(f"Attempting to send WhatsApp message to {contact}...")
        if not self.open_app('whatsapp'):
            print("Failed to open WhatsApp.")
            return False
        
        try:
            time.sleep(7)

            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            
            pyautogui.write(contact)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(2)
            pyautogui.press('down')
            pyautogui.press('enter')
            time.sleep(1)          
            
            pyautogui.write(message)
            time.sleep(5)
            pyautogui.press('enter')
            print(f"Successfully sent WhatsApp message to {message}.")
            return True
        except pyautogui.FailSafeException:
            print("PyAutoGUI FailSafe triggered. Mouse moved to a corner. Aborting WhatsApp message.")
            return False
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def adjust_system_setting(self, setting: str, value: int) -> bool:
        print(f"Attempting to adjust system setting: {setting} by {value}")
        setting = setting.lower()
        try:
            if setting == 'volume':
                abs_value = abs(value)
                for _ in range(abs_value):
                    if value > 0:
                        pyautogui.press('volumeup')
                    else:
                        pyautogui.press('volumedown')
                    time.sleep(0.1)
                print(f"Adjusted volume by {value} steps.")
                return True
            
            elif setting == 'brightness':
                if platform.system() == 'Windows':
                    print("Attempting to adjust brightness on Windows via GUI. This is less reliable.")
                    self.open_app('settings')
                    time.sleep(2)
                    pyautogui.write('display settings')
                    time.sleep(1)
                    pyautogui.press('enter')
                    time.sleep(2)

                    for _ in range(abs(value)):
                        if value > 0:
                            pyautogui.press('right')
                        else:
                            pyautogui.press('left')
                        time.sleep(0.1)
                    print(f"Attempted to adjust brightness by {value} steps.")
                    return True
                else:
                    print(f"Brightness adjustment is not supported for {platform.system()} via this method.")
                    print("Consider using platform-specific commands (e.g., 'xrandr' on Linux, 'osascript' on macOS).")
                    return False
            else:
                print(f"Unsupported system setting: {setting}")
                return False
        except pyautogui.FailSafeException:
            print("PyAutoGUI FailSafe triggered. Mouse moved to a corner. Aborting system setting adjustment.")
            return False
        except Exception as e:
            print(f"Error adjusting system setting {setting}: {e}")
            return False

    def generate_content(self, topic: str) -> bool:
        print(f"Generating content for: {topic}")
        prompt = f"Write content about: {topic}"
        content_by_ai = self._query_groq(prompt)

        if "Error" in content_by_ai:
            print(f"Content generation failed: {content_by_ai}")
            return False

        data_dir = "Data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Created directory: {data_dir}")

        filename_topic = "".join(c for c in topic if c.isalnum() or c in [' ', '_']).replace(' ', '_').lower()
        filepath = os.path.join(data_dir, f"{filename_topic}.txt")
        
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content_by_ai)
            print(f"Content written to: {filepath}")
            
            return _open_notepad_with_file(filepath)
        except Exception as e:
            print(f"Error writing content to file: {e}")
            return False

    def google_search(self, query: str) -> bool:
        return _google_search_web(query)


    def Youtube(self, query: str) -> bool:
        return _Youtube_web(query)

    def play_youtube(self, query: str) -> bool:
        return _play_youtube_video(query)

    def system_command(self, command: str) -> bool:
        return _system_command_execute(command)

    async def _execute_single_command(self, action: str, value: str) -> bool:
        print(f"Executing: Action='{action}', Value='{value}'")
        if action == "open_app":
            return self.open_app(value)
        elif action == "close_app":
            return self.close_app(value)
        elif action == "play_youtube":
            return self.play_youtube(value)
        elif action == "Google Search":
            return self.google_search(value)
        elif action == "Youtube":
            return self.Youtube(value)
        elif action == "generate_content":
            return self.generate_content(value)
        elif action == "system_command":
            return self.system_command(value)
        elif action == "send_whatsapp_message":
            parts = value.split(':', 1)
            if len(parts) == 2:
                return self.send_whatsapp_message(parts[0].strip(), parts[1].strip())
            else:
                print(f"Invalid format for send_whatsapp_message: {value}. Expected 'contact:message'.")
                return False
        elif action == "adjust_system_setting":
            parts = value.split(':', 1)
            if len(parts) == 2:
                try:
                    setting = parts[0].strip()
                    val = int(parts[1].strip())
                    return self.adjust_system_setting(setting, val)
                except ValueError:
                    print(f"Invalid value for adjust_system_setting: {parts[1]}. Expected integer.")
                    return False
            else:
                print(f"Invalid format for adjust_system_setting: {value}. Expected 'setting:value_int'.")
                return False
        else:
            print(f"Unknown action: {action}")
            return False

    async def process_natural_language_command(self, nl_command: str) -> List[bool]:
        print(f"\nProcessing natural language command: '{nl_command}'")
        groq_prompt = (
            f"Based on the following user request, identify the primary action(s) and their "
            f"arguments. Respond ONLY with a JSON array of objects. Each object should have 'action' (string) "
            f"and 'value' (string) keys. If multiple actions, list them in order. "
            f"Possible actions: 'open_app', 'close_app', 'play_youtube', 'Google Search', "
            f"'Youtube', 'generate_content', 'system_command', 'send_whatsapp_message', "
            f"'adjust_system_setting'.\n"
            f"For 'send_whatsapp_message', the value should be 'ContactName:MessageContent'.\n"
            f"For 'adjust_system_setting', the value should be 'setting_name:integer_value' (e.g., 'volume:5' or 'brightness:-10').\n"
            f"User request: '{nl_command}'\n\n"
            f"Example for 'open notepad and search for cats':\n"
            f"[\n  {{\"action\": \"open_app\", \"value\": \"notepad\"}},\n  {{\"action\": \"Google Search\", \"value\": \"cats\"}}\n]\n"
            f"Example for 'send a whatsapp message to Mom saying hi':\n"
            f"[\n  {{\"action\": \"send_whatsapp_message\", \"value\": \"Mom:hi\"}}\n]\n"
            f"Example for 'increase volume by 5':\n"
            f"[\n  {{\"action\": \"adjust_system_setting\", \"value\": \"volume:5\"}}\n]\n"
            f"Your JSON response:"
        )

        original_messages_backup = list(self.messages)
        self.messages = [{"role": "system", "content": "You are a helpful assistant that extracts structured commands from user requests."}]
     
        groq_response = self._query_groq(groq_prompt)
        
        self.messages = original_messages_backup

        if "Error" in groq_response:
            print(f"Groq parsing failed: {groq_response}")
            return [False]

        try:
            commands_to_execute = json.loads(groq_response)
            if not isinstance(commands_to_execute, list):
                raise ValueError("Groq response was not a JSON array.")
            
            results = []
            for cmd in commands_to_execute:
                if "action" in cmd and "value" in cmd:
                    result = await self._execute_single_command(cmd["action"], cmd["value"])
                    results.append(result)
                else:
                    print(f"Malformed command from Groq: {cmd}. Skipping.")
                    results.append(False)
            return results
        except json.JSONDecodeError as e:
            print(f"Failed to parse Groq's JSON response: {e}\nResponse: {groq_response}")
            return [False]
        except ValueError as e:
            print(f"Error in Groq response structure: {e}\nResponse: {groq_response}")
            return [False]
        except Exception as e:
            print(f"An unexpected error occurred during command processing: {e}")
            return [False]

# --- Main Execution Block ---
async def main(statement: Optional[str] = None):
    automator = GroqAutomation()
    print("--- Starting Automation Tests ---")
    if statement:
        await automator.process_natural_language_command(statement)
    else:
        print("No statement provided for automation.")
    time.sleep(2)
    print("\n--- Automation Tests Complete ---")

async def Automation(commands: list[str]):
    print(f"Starting automation with commands: {commands}")
    results = []
    automator_instance = GroqAutomation()
    for cmd_str in commands:
        individual_results = await automator_instance.process_natural_language_command(cmd_str)
        results.extend(individual_results)

    print(f"Automation completed. Results: {results}")
    return True


if __name__ == "__main__":
    while True:
        Task = input("Enter a natural language command for automation: ")
        asyncio.run(main(Task))