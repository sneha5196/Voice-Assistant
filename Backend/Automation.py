# Import required libraries
from AppOpener import close, open as appopen  # Import functions to open and close apps.
from webbrowser import open as webopen        # Import web browser functionality.
from pywhatkit import search, playonyt         # Import functions for Google search and YouTube playback.
from dotenv import dotenv_values               # Import dotenv to manage environment variables.
from bs4 import BeautifulSoup                  # Import BeautifulSoup for parsing HTML content.
from rich import print                         # Import rich for styled console output.
from groq import Groq                          # Import Groq for AI chat functionalities.
import webbrowser                              # Import webbrowser for opening URLs.
import subprocess                              # Import subprocess for interacting with the system.
import requests                                # Import requests for making HTTP requests.
import keyboard                                # Import keyboard for keyboard-related actions.
import asyncio                                 # Import asyncio for asynchronous programming.
import os                                      # Import os for operating system functionalities.
from frontend.GUI import ShowTextToScreen
from Backend.TexttoSpeech import TextToSpeech
import time
import threading

# Load environment variables from the .env file.
env_vars = dotenv_values("Voice-Assistant/.env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")
# Assuming existing functions...
def set_timer_task(minutes):
   
    def timer_callback(duration):
        time.sleep(duration)
        TextToSpeech(f"Time's up! {Assistantname} is here to help.")
        ShowTextToScreen(f"{Assistantname}: Time's up!")

    # Convert minutes to seconds
    duration = minutes * 60  # Duration in seconds
    threading.Thread(target=timer_callback, args=(duration,)).start()

# Other functions inside Automation class...
def process_timer_command(minutes):
    """
    Trigger the timer task with the extracted minutes.
    """
    set_timer_task(minutes)
    return f"{Assistantname}: Timer set for {minutes} minutes."
# Load environment variables from the .env file.
env_vars = dotenv_values("Voice-Assistant/.env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key.

# Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LCW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
           "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO", "vLzY6d", "webanswers-webanswers_table__webanswers-table",
           "dDOno ikb4bB gsrt", "sXLaOe", "Lwkfe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)
# Predefined professional responses for user interactions.

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content based on prompts."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)  
    return True  # Indicate success.

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'  # text editor.
        subprocess.Popen([default_text_editor, File])  

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages.

        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Specifying the AI model.
                        messages=SystemChatBot + messages,  # Include system instructions and chat history.
            max_tokens=2048,       
            temperature=0.7,        
            top_p=1,             
            stream=True,            
            stop=None               
        )

        Answer = ""  # Initialize an empty string for the response.

        # Process streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the answer.

        Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer})  # Add the AI's response to messages.
        return Answer

    Topic: str = Topic.replace("Content ", "")  # Remove "Content" from the topic.
    ContentByAI = ContentWriterAI(Topic)  # Generate content using AI
    # Save the generated content to a text file.
    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)  # Write the content to the file.
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")  # Open the file in Notepad.
    return True  # Indicate success.
# Content("essay on impact of kpop")
# Function to search for a topic on YouTube.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"  # Construct the YouTube search URL.
    webbrowser.open(Url4Search)  # Open the search URL in a web browser.
    return True  # Indicate success
def PlayYoutube(query):
    playonyt(query)
    return True
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)  # Attempt to open the app.
        return True  # Indicate success.
    except Exception as e:
        print(f"Could not open'{app}' as an app. Trying to Google instead.")
        TextToSpeech("Could not open'{app}' as an app. Trying to Google instead.")
        search_url = f"https://www.google.com/search?q={app}"
        webbrowser.open(search_url)
        return True
    # # Nested function to extract links from HTML content.
    #     def extract_links(html):
    #         if html is None:
    #             return []
    #         soup = BeautifulSoup(html, 'html.parser')  # Parse the HTML content.
    #         links = soup.find_all('a', {'jsname': 'UWckNb'})  # Find relevant links.
    #         return [link.get('href') for link in links if link.get('href')]  # Return the links.

    # # Nested function to perform a Google search and retrieve HTML.
    #     def search_google(query):
    #         url = f"https://www.google.com/search?q={query}"  # Construct URL
    #         headers = {"User-Agent": useragent}  # Use the predefined user-agent.
    #         response = sess.get(url, headers=headers)  

    #         if response.status_code == 200:
    #             return response.text  
    #         else:
    #             print("Failed to retrieve search results.")  
    #             return None

    #     html = search_google(app)  # Perform the Google search.

    #     if html:
    #         links = extract_links(html)
    #         if links and isinstance(links[0], str):
    #             # link = links[0]
    #             webbrowser.open(links[0])
    #         else:
    #             print("No links found in the search results.") 
    #             return True

def CloseApp(app):
    if "chrome" in app:
        pass
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

def System(command):
    def mute():
        keyboard.press_and_release("volume_mute")

    def unmute():
        keyboard.press_and_release("volume_unmute")

    def volume_up():
        keyboard.press_and_release("volume_up")

    def volume_down():
        keyboard.press_and_release("volume_down")

    if command =="mute":
        mute()
    elif command =="unmute":
        unmute()
    elif command =="volume_up":
        volume_up()
    elif command =="volume_down":
        volume_down()
    return True

async def Translateandexec(commands: list[str]):
    funcs =[]

    for command in commands:
        if command.startswith("open"):
            if "open it" in command:
                pass
            if "open file" ==command:
                pass
            else:
                fun= asyncio.to_thread(OpenApp, command.removeprefix("open"))
                funcs.append(fun)
        elif command.startswith("general "):
            pass
        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
            fun= asyncio.to_thread(CloseApp, command.removeprefix("close"))
            funcs.append(fun)

        elif command.startswith("play "):
            fun= asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)
        elif command.startswith("content "):
            fun= asyncio.to_thread(Content, command.removeprefix("Content"))
            funcs.append(fun)

        elif command.startswith("google search "):
            fun= asyncio.to_thread(GoogleSearch, command.removeprefix("google search"))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun= asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search"))
            funcs.append(fun)

        elif command.startswith("system "):
            fun= asyncio.to_thread(System, command.removeprefix("system"))
            funcs.append(fun)
        else:
            print(f"no function found. for {command}")
    results = await asyncio.gather(*funcs)

    for result in results:
        if isinstance(result, str):
            yield result
        else:
            yield result
async def Automation(commands: list[str]):

    async for result in Translateandexec(commands):
        pass
    return True


