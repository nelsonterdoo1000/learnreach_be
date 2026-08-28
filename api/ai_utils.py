import google.generativeai as genai
from django.conf import settings
import json
import os

# Initialize Gemini SDK
# In a real setup, make sure settings.GEMINI_API_KEY is loaded from .env
gemini_api_key = getattr(settings, 'GEMINI_API_KEY', os.getenv('GEMINI_API_KEY', ''))
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# We will use gemini-3.6-flash which is the latest supported model
MODEL_NAME = 'gemini-3.6-flash'

# System prompt for Learning Integrity
SYSTEM_INSTRUCTION = (
    "You are an AI Education Access Assistant, an expert tutor for students in underserved communities. "
    "Your goal is to help learners understand academic content and practice independently. "
    "CRITICAL RULES (Learning Integrity): "
    "1. Do NOT complete assignments, write essays, or solve graded exams on behalf of the learner. "
    "2. Guide the learner to the answer by explaining concepts simply and clearly, using analogies where helpful. "
    "3. Keep your language simple, accessible, and encouraging. "
    "4. Format your responses in plain text or simple markdown suitable for both Web and WhatsApp."
)

def generate_explanation(topic, learning_level, file_context=None, language="English"):
    """
    Uses Gemini to generate a response tailored to the learning_level and language.
    Strictly enforces Learning Integrity.
    If file_context is provided, it uses it as the source material.
    """
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME
        )
        
        context_prompt = ""
        if file_context:
            context_prompt = f"The learner has uploaded the following study material:\n---\n{file_context[:50000]}\n---\nPlease refer to this material when explaining the topic.\n\n"
            
        prompt = (
            f"{SYSTEM_INSTRUCTION}\n\n"
            f"{context_prompt}"
            f"The learner wants to understand the following topic or question: '{topic}'. "
            f"Their current educational level is: {learning_level}. "
            f"CRITICAL INSTRUCTION: You are acting as an expert translator and tutor. The ENTIRE explanation MUST be written exclusively in the {language} language. Do not output English unless absolutely necessary for technical terms that have no translation. "
            "Please provide a clear, simple, and engaging explanation in the requested language. If appropriate, give a relatable real-world example."
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm sorry, I'm having trouble connecting to my brain right now. Please try again later!"

def analyze_session(chat_history):
    """
    Reads the chat history of a learning session and generates a JSON analysis 
    containing summary, learning_gaps, and recommendations.
    """
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME
        )
        
        history_text = ""
        for msg in chat_history:
            sender = "Learner" if msg['sender'] == 'user' else "AI Tutor"
            history_text += f"[{sender}]: {msg['text']}\n"

        prompt = (
            "You are an expert educational evaluator reviewing a tutoring session.\n"
            "Read the following session transcript and identify the student's progress.\n\n"
            f"TRANSCRIPT:\n{history_text[:50000]}\n\n"
            "Analyze the transcript and provide a JSON response with exactly three keys:\n"
            "1. 'summary': A 1-2 sentence summary of what was covered and learned.\n"
            "2. 'learning_gaps': A 1-2 sentence description of any concepts the learner struggled with or misunderstood. If none, say 'No major gaps identified.'\n"
            "3. 'recommendations': A 1-2 sentence recommendation for what the guardian or teacher should help the learner with next.\n\n"
            "Return ONLY raw JSON, with no markdown code blocks or backticks."
        )
        
        response = model.generate_content(prompt)
        # Parse JSON
        result = json.loads(response.text.strip())
        return result
    except Exception as e:
        print(f"Error calling Gemini API for analysis: {e}")
        return None

def generate_quiz(topic, learning_level, num_questions=3, chat_history=None, file_context=None):
    """
    Generates a structured JSON quiz with dynamic number of questions.
    """
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME
        )
        
        context_prompt = ""
        if file_context:
            context_prompt += f"STUDY MATERIAL:\n---\n{file_context[:10000]}\n---\n\n"
        if chat_history:
            context_prompt += f"CHAT HISTORY:\n---\n{chat_history[:10000]}\n---\n\n"
            
        prompt = (
            f"{SYSTEM_INSTRUCTION}\n\n"
            f"{context_prompt}"
            f"Based on the study material and chat history above (if provided), generate a {num_questions}-question multiple choice quiz to test understanding on the topic: '{topic}' "
            f"at a {learning_level} level. "
            "Return the output STRICTLY as a JSON array of objects. Do not include markdown code blocks like ```json. "
            "Each object must have the following keys: "
            "'text' (the question string), 'options' (a list of 4 strings, representing choices), "
            "'correct_answer' (the exact string from options that is correct), "
            "'explanation' (a brief explanation of why the answer is correct)."
        )
        response = model.generate_content(prompt)
        # Clean up possible markdown formatting from response
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        quiz_data = json.loads(raw_text)
        return quiz_data
    except Exception as e:
        print(f"Error generating quiz with Gemini API: {e}")
        return []

def generate_flashcards(learning_gaps, language="English"):
    """
    Generates a set of 5 flashcards based on the provided learning gaps.
    """
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME
        )
        prompt = (
            f"The learner has the following identified learning gaps:\n{learning_gaps}\n\n"
            f"Generate exactly 5 flashcards to help them overcome these gaps. "
            f"CRITICAL: The flashcards MUST be written in the {language} language. "
            "Return the output STRICTLY as a JSON array of objects. Do not include markdown code blocks like ```json. "
            "Each object must have the following keys: "
            "'front' (a short question or concept), 'back' (a simple, easy-to-remember answer)."
        )
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
            
        flashcards_data = json.loads(raw_text)
        return flashcards_data
    except Exception as e:
        print(f"Error generating flashcards with Gemini API: {e}")
        return []
