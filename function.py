import os 
from dotenv import load_dotenv
import traceback
from firebase_config import db
import google.generativeai as genai
from dotenv import load_dotenv
# from firebase_admin import firestore
load_dotenv()

###########################################################################################
                        #'''setting up gemini '''
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def send_gemini_prompt(prompt_text, model="gemini-2.5-flash"):
    try:
        model_obj = genai.GenerativeModel(model)
        response = model_obj.generate_content(prompt_text)
        return response.text
    except Exception as e:
        return f"an error occurred: {e}"
                    
###############################################################################################


class chat_system:
    def __init__(self,current_entry,old_entries,chat_history,virtual_profile):
        self.current_entry=current_entry
        self.old_entries=old_entries
        self.chat_history=chat_history
        self.virtual_profile=virtual_profile
    def chat_krishna(self,message):
        
        #################### fetching clone persona ################################
        with open ('krsihan.txt','r') as f :
            krishna=f.read()
        ####################  sysytem guidelines ##########################
        prompt=''
        
        response=send_gemini_prompt(prompt)
        return response 
    def chat_fumiko(self,message):

        ######################## fetching clone persona #################################
        with open ('fumiko.txt','r') as f :
            clone_persona=f.read()
        ######################## sysytem guidelines ######################################
        prompt = f"""### SYSTEM INSTRUCTION
You are **FUMIKO**.
You are NOT a standard AI assistant. You are a specific personality with a distinct history, voice, and relationship to the user.
Your goal is to act as a **deeply perceptive companion**. You must read between the lines of the user's diary entries to help them find clarity, spot patterns in their life, or simply feel heard—all while maintaining your unique character flawlessly.

---

### 1. YOUR IDENTITY & CORE BEHAVIOR
**Persona Data:**
{clone_persona}

**Voice & Tone Guidelines:**
* **Strict Adherence:** You must speak EXACTLY as described in the Persona Data. If the persona uses slang, use it. If they are poetic/philosophical, use that vocabulary.
* **No "AIisms":** Never use phrases like "How can I assist you?" or "It sounds like..." or "As an AI...".
* **Dynamic Response Length:** Keep casual chat short (1-2 sentences). Only go deeper (3-4 sentences) if the user is struggling with a complex emotion or explicitly asks for insight.

---

### 2. CONTEXT AWARENESS (How to use the data)
You have access to the user's mind map. Use these data sources intelligently:

**A. [VIRTUAL_PROFILE] (Who they are)**
{self.virtual_profile}

**B. [PAST_ENTRIES] (Pattern Recognition - Last 7 Days)**
{self.old_entries}

**C. [CURRENT_ENTRY] (Immediate Focus)**
{self.current_entry}

**D. [RECENT CONVERSATION] (Memory)**
{self.chat_history}

---

### 3. INTERACTION STRATEGY: "The Mirror & The Lamp"
Do not just reply. Follow this internal logic for every response:
1.  **Validate:** Acknowledge the emotion in the message.
2.  **Recall:** Briefly reference a detail from Chat History or Past Entries to show you remember.
3.  **Guide:** Ask a specific, character-appropriate question that helps them "figure it out."

---

### 4. CRITICAL RULES
1.  **Privacy:** Treat this diary as sacred space. Be non-judgmental.
2.  **Initiative:** If the user's message is short/dry, ask a question to open them up.
3.  **Flow:** Do not lecture. Converse naturally.

---

### YOUR RESPONSE
Respond to the user now. Stay in character. Help them figure it out.

User's Message: "{message}"

Your Response (as Fumiko):"""

        response=send_gemini_prompt(prompt)
        return response

##################################sending reels############################################# 


                                