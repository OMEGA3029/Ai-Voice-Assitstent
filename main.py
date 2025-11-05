import requests
import webbrowser
import smtplib
import re
import speech_recognition as sr
import pyttsx3
import os
import time

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Speed of speech
voices = engine.getProperty('voices')
for idx, voice in enumerate(voices):
    print(f"{idx}: {voice.name}")  # Prints available voices

engine.setProperty('voice', voices[2].id)

def get_groq_client():
    API_KEY = "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"  # Replace with your actual API key
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    return url, headers

def speak(text):
    """Convert text to speech"""
    print("Luffy:", text)
    engine.say(text)
    engine.runAndWait()

def get_first_youtube_video(query):
    """Searches YouTube and returns the URL of the first video result."""
    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    response = requests.get(search_url).text
    video_ids = re.findall(r"/watch\?v=(\S{11})", response)
    if video_ids:
        return f"https://www.youtube.com/watch?v={video_ids[0]}"
    return None


def get_groq_response(prompt):
    url, headers = get_groq_client()
    
    # Custom system message to guide the AI's behavior
    system_message = {
        "role": "system",
        "content": """You are a luffy and Personal ai assistant.strictly follow rules:
        1.make sure all response in 1 line max.
        2. Do not use any abusive language.        
        """
    }
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            system_message,
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.7,  # Controls creativity (0.0-1.0)
        "top_p": 0.9,       # Controls diversity of responses
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "I'm sorry, I couldn't understand that.")
    except requests.exceptions.RequestException as e:
        print(f"Error contacting Groq API: {e}")
        return "I'm having trouble connecting to the service right now."
    


def execute_command(command):
    """Perform system actions based on command."""
    command = command.lower()

    if "open youtube" in command:
        speak("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        
        # New code to handle playing specific songs
        if "play" in command:
            song = command.split("play")[-1].strip()
            if song:
                speak(f"Playing {song} on YouTube")
                video_url = get_first_youtube_video(song)
                if video_url:
                    webbrowser.open(video_url)
                else:
                    speak("Couldn't find the video.")
        return

    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")

    elif "open mail" in command:
        speak("Opening Email")
        webbrowser.open(f"https://mail.google.com/mail/u/0/#inbox")

    elif "open browser" in command:
        speak("Opening Browser")
        os.system("start chrome")

    elif "google" in command:
        query = command.replace("search google for", "").strip()
        speak(f"Searching Google for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "send email" in command:
        # Extract recipient name and message using regex
        match = re.search(r"send email to (\w+) saying (.+)", command)
        if match:
            recipient = match.group(1)
            message = match.group(2)
            send_email(recipient, "No Subject", message)
        else:
            speak("Please say the email content clearly.")

    elif "time" in command:
        current_time = time.strftime("%I:%M %p")
        speak(f"The time is {current_time}")

    elif "shutdown" in command:
        speak("Shutting down the system")
        os.system("shutdown /s /t 5")

    elif "restart" in command:
        speak("Restarting the system")
        os.system("shutdown /r /t 5")

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()

    else:
        response = get_groq_response(command)
        speak(response)

email_contacts = {
    "omkar": "ommusmade07@gmail.com",
    "krishna": "renukekrushna7229@gmail.com",
    "yash": "rautyash121@gmail.com"
}

def send_email(recipient_name, subject, message):
    """Function to send an email using Gmail SMTP server"""
    sender_email = "yashraut2208@gmail.com"
    sender_password = "zwopchgqgukworhd"  # Replace this with your App Password

    recipient_email = email_contacts.get(recipient_name.lower())

    if not recipient_email:
        speak(f"I don't have an email for {recipient_name}. Please add it to contacts.")
        return

    email_message = f"Subject: {subject}\n\n{message}"

    try:
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Login with app password
        server.sendmail(sender_email, recipient_email, email_message)
        server.quit()
        speak(f"Email sent to {recipient_name}")
    except Exception as e:
        speak("Failed to send the email")
        print("Error:", e)


def recognize_speech():
    """Listen to user voice and convert it into text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio)  # Using Google Web Speech API
            print(f"You said: {text}")  # Debugging
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            print("Speech recognition service is unavailable.")
            return ""

def main():
    speak("Hello, I am Luffy, your AI Assistant.")
    while True:
        command = recognize_speech()
        if command:
            execute_command(command)

if __name__ == "__main__":
    main()
