from frontend.GUI import(
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetAssistantStatus,
    GetMicrophoneStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Automation import set_timer_task 
from Backend.Automation import process_timer_command
from Backend.SpeechtoText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TexttoSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep 
import subprocess
import threading
import json
import os


env_vars=  dotenv_values("Voice-Assistant/.env")
Username= env_vars.get("Username")
Assistantname= env_vars.get("Assistantname")
DefaultMessage=f'''{Username}: Hello, How are you?
{Assistantname}: Welcome{Username}, I am doing well. How may i help you'''
subprocess=[]
Function=["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    File=open(r'Voice-Assistant\Data\Chatlog.json',"r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'),'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'),'w',encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
        with open(r'Voice-Assistant\Data\ChatLog.json','r', encoding='utf-8') as file:
            chatBot_data=json.load(file)
        return chatBot_data
def ChatLogIntegration():
    json_data=ReadChatLogJson()
    formatted_chatlog=""
    for entry in json_data:
            if entry["role"]=="user":
                formatted_chatlog +=f"User:{entry['content']}\n"
            elif entry["role"]=="assistant":
                formatted_chatlog+=f"Assistant:{entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User",Username+ " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
         file.write(AnswerModifier(formatted_chatlog))

def ShowChatOnGUI():
     File = open(TempDirectoryPath('Database.data'),"r", encoding='utf-8')
     Data = File.read()
     if len(str(Data))>0:
          lines = Data.split('\n')
          result = '\n'.join(lines)
          File.close()
          File= open(TempDirectoryPath('Responses.data'),"w", encoding='utf-8')
          File.write(result)
          File.close()
def IntialExecution():
     SetMicrophoneStatus("False")
     ShowTextToScreen("")
     ShowDefaultChatIfNoChats()
     ChatLogIntegration()
     ShowChatOnGUI()

IntialExecution()

def MainExecution():
    TaskExecution=False
    #  ImageExecution=False

    SetAssistantStatus("Listening...")
    Query= SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision =FirstLayerDMM(Query)

    print("")
    print(f"Decision :{Decision}")
    print("")

    G= any([i for i in Decision if i.startswith("general")])
    R= any([i for i in Decision if i.startswith("realtime")])

    Mearged_query=" and ".join(
         [" ".join(i.split()[1:])for i in Decision if  i.startswith("general") or i.startswith("realtime")]
    )
    # for queries in Decision:
    #      if "generate" in queries:
    #      ImageGenerationQuery= srt(queries)
    #      ImageExecution = True
    if any("timer" in query for query in Decision):
       minutes = extract_time_from_query(Query)  # Extract minutes for the timer
       if minutes > 0:
           # Call Automation's process_timer_command to set the timer
           timer_response = process_timer_command(minutes)
           ShowTextToScreen(timer_response)
           SetAssistantStatus("Timer set.")
           TextToSpeech(timer_response)
           return True
    for queries in Decision:
         if TaskExecution == False:
              if any(queries.startswith(func) for func in Function):
                   run(Automation(list(Decision)))
                   TaskExecution = True
    if R:  # If there is a realtime query, process it
          SetAssistantStatus("Searching...")
          Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
          ShowTextToScreen(f"{Assistantname}: {Answer}")
          SetAssistantStatus("Answering...")
          TextToSpeech(Answer)
          return True
    if G or R:
         SetAssistantStatus("Searching...")
         Answer =ChatBot(QueryModifier(Mearged_query))
         ShowTextToScreen(f"{Assistantname}:{Answer}")
         SetAssistantStatus("Answering...")
         TextToSpeech(Answer)
         return True
    else:
         for Queries in Decision:
              if "general" in Queries:
                   SetAssistantStatus("Searching...")
                   QueryFinal= Queries.replace("realtime","")
                   Answer=RealtimeSearchEngine(QueryModifier(QueryFinal))
                   ShowTextToScreen(f"{Assistantname}:{Answer}")
                   SetAssistantStatus("Answering...")
                   TextToSpeech(Answer)
                   return True
              elif "exit" in Queries:
                   QueryFinal="Okayy, byee!"
                   Answer=ChatBot(QueryModifier(QueryFinal))
                   ShowTextToScreen(f"{Assistantname}:{Answer}")
                   SetAssistantStatus("Answering...")
                   TextToSpeech(Answer)
                   SetAssistantStatus("Answering...")
                   os._exit(1)
def extract_time_from_query(query):
    words = query.split()
    for word in words:
        if word.isdigit():
            return int(word)  # Return the number found
    return 0 
def FirstThread():
     while True:
          CurrentStatus = GetMicrophoneStatus()

          if CurrentStatus =="True":
               MainExecution()
          else:
               AIStatus = GetAssistantStatus()

               if "Available..." in AIStatus:
                    sleep(0.1)
               else:
                    SetAssistantStatus("Available...")
def SecondThread():
     GraphicalUserInterface()

if __name__ == "__main__":
     thread2= threading.Thread(target=FirstThread, daemon=True)
     thread2.start()
     SecondThread()

     