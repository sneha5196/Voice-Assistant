from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables from the .env file.
env_vars = dotenv_values("Voice-Assistant/.env")

# Get the input language setting from the environment variables.
InputLanguage = env_vars.get("InputLanguage")

# Define the HTML code for the speech recognition page
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                console.log("recongnition ended");
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Inject the selected language into the HTML
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
os.makedirs("Data", exist_ok=True)
with open(r"Voice-Assistant/Data/Voice.html", "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Get the current working directory.
current_dir = os.getcwd()

# Generate the file path for the HTML file.
Link = f"{current_dir}/Voice-Assistant/Data/Voice.html"

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "wh"]

    # Check if the query is a question and add a question mark if necessary.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

# Translate any non-English text to English
def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Main speech recognition logic
def SpeechRecognition():
    driver.get("file:///" + Link)
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            Text = driver.find_element(by=By.ID, value="output").text
            if Text:
                driver.find_element(by=By.ID, value="end").click()

                input_lang = InputLanguage.lower()
                if input_lang == "en" or "en" in input_lang:
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating....")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            print(f"Error during speech recognition: {e}")

# Main entry point
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print(Text)