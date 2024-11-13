from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_community.llms import OpenAI
import logging
import os
import requests
import json
from bson import json_util
from bs4 import BeautifulSoup
import openai
import re
from datetime import datetime
from marshmallow import Schema, fields, ValidationError
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Define the Registration Schema
class RegistrationSchema(Schema):

    fullname = fields.Str(required=True)
    phone_no = fields.Str(required=True)
    company_name = fields.Str(required=True)
    email = fields.Email(required=True)

app = Flask(__name__)
CORS(app)

# MongoDB credentials
username = "dev"
password = "walliea"  

# URL-encode username and password
encoded_username = quote_plus(username)
encoded_password = quote_plus(password)

# MongoDB connection string
mongodb_uri = f"mongodb+srv://{encoded_username}:{encoded_password}@wallmark.tmreg.mongodb.net/?retryWrites=true&w=majority&appName=WallMark"

try:
    client = MongoClient(mongodb_uri)
    db = client.get_database('WallMark')
    app.config['db'] = db
    register_collection = db.get_collection('registerSchema')
    logging.info("Connected to MongoDB")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {str(e)}")

os.environ["OPENAI_API_KEY"] = "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"
openai.api_key = os.getenv("OPENAI_API_KEY")

website_urls = [
    "https://wallmarkply.com/",
    "https://wallmarkply.com/about/",
    "https://wallmarkply.com/blog/",
    "https://wallmarkply.com/plywoods/",
    "https://wallmarkply.com/wallmark-ply-wins-prestigious-times-business-award-for-trusted-preferred-brand/",
    "https://wallmarkply.com/author/techlead/",
    "https://wallmarkply.com/pvc-board/",
    "https://wallmarkply.com/doors/",
    "https://wallmarkply.com/products/",
    "https://wallmarkply.com/particle-board/",
    "https://wallmarkply.com/veneers/",
    "https://wallmarkply.com/contact/",
    "https://wallmarkply.com/mdf/",
    "https://wallmarkply.com/index.php/blog/",
    "https://wallmarkply.com/index.php/contact/",
    "https://wallmarkply.com/index.php/about/",
    "https://wallmarkply.com/booking/",
    "https://wallmarkply.com/2024/08/",
    "https://wallmarkply.com/category/blog/",
    "https://wallmarkply.com/index.php/pvc-board/",
    "https://wallmarkply.com/index.php/doors/",
    "https://wallmarkply.com/index.php/veneers/",
    "https://wallmarkply.com/index.php/particle-board/",
    "https://wallmarkply.com/index.php/plywoods/",
    "https://wallmarkply.com/index.php/mdf/",
    "https://wallmarkply.com/comments/feed/",
    "https://wallmarkply.com/feed/",
    "https://wallmarkply.com/wp-login.php",
    "https://wallmarkply.com/wp-login.php?action=lostpassword"
]

# Hardcoded contact details
CONTACT_DETAILS = """
Wallmark Ply Pvt Ltd.
Address: Odakkaly, Perumbavoor, 
         Asamannoor P.O, Ernakulam Dist., kerala, India
Phone: +91 97 4491 2617 
       +91 75 9494 1057 
       +91 81 2962 724
Email: info@wallmarkply.com
"""

def scrape_data():
    raw_text = ''
    for url in website_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for paragraph in soup.find_all(['p', 'h1', 'h2', 'h3']):
                raw_text += paragraph.get_text() + "\n"
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve {url}: {str(e)}")
    return raw_text

# Scrape data from websites
raw_text = scrape_data()

# Split the text to avoid token size issues
text_splitter = CharacterTextSplitter(separator="\n", chunk_size=800, chunk_overlap=200, length_function=len)
texts = text_splitter.split_text(raw_text)

# Download embeddings from OpenAI
embeddings = OpenAIEmbeddings()
document_search = FAISS.from_texts(texts, embeddings)
chain = load_qa_chain(OpenAI(), chain_type="stuff")

def get_openai_response(prompt, context=None):
    try:
        messages = [{"role": "system", "content": context}] if context else []
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200
        )
        return response.choices[0].message['content'].strip()
    except openai.error.OpenAIError as e:
        return f"OpenAI Error: {str(e)}"

def is_calculation_question(question):
    math_keywords = ['calculate', 'sum', 'add', 'subtract', 'multiply', 'divide', 'total', 'average', 'mean', 'difference']
    math_symbols = re.search(r'[0-9\+\-\*/]', question)
    
    if any(keyword in question.lower() for keyword in math_keywords) or math_symbols:
        return True
    return False

def is_contact_or_location_question(question):
    contact_keywords = ['contact', 'phone', 'email', 'address', 'location', 'where', 'reach']
    if any(keyword in question.lower() for keyword in contact_keywords):
        return True
    return False

# Store chats with timestamps
chat_history = []
conversation_context = ""

@app.route('/chat', methods=['POST'])
def chat():
    global conversation_context
    user_input = request.json['message']
    bot_response = ""

    if user_input.lower() in ["hi", "hii", "hello", "hey", "good morning", "good afternoon", "good evening", "greetings", "howdy", "what's up", "hey there", "hi there"]:
        bot_response = "Hello! Welcome to Walliea, How can I assist you today?"
    elif user_input.lower() in ["wallmark", "wall mark"]:
        bot_response = "Wallmark Ply is a trusted and preferred brand of high-quality plywood that has won the prestigious Times Business Award. Powered by Cygnotech Labs, it is known for its passion for producing top-notch plywood products."
    elif user_input.lower() in ["bye", "thank you", "thanks", "goodbye", "see you", "later", "talk to you later"]:
        bot_response = "Goodbye, and have a great day ahead!"
    elif is_contact_or_location_question(user_input):
        bot_response = CONTACT_DETAILS
    else:
        question = user_input.strip()
        if len(question) < 4:
            bot_response = "Please enter a valid question!"
        else:
            if is_calculation_question(question):
                bot_response = get_openai_response(user_input, context=conversation_context)
            else:
                if "earlier" in user_input.lower() or "previous" in user_input.lower():
                    relevant_history = ""
                    for entry in chat_history:
                        if any(word in entry['user'].lower() for word in ["wallmark", "plywood", "veneers"]):
                            relevant_history += f"{entry['user']} - {entry['bot']}\n"
                    if relevant_history:
                        bot_response = f"Here's what we discussed earlier:\n{relevant_history}"
                    else:
                        bot_response = "Sorry, I couldn't find anything relevant from earlier conversations."
                else:
                    docs = document_search.similarity_search(user_input)
                    if docs:
                        kb_response = chain.run(input_documents=docs, question=question)
                        kb_response = kb_response.replace("Based on the provided context, ", "").strip()
                        kb_response = kb_response.replace("According to the information, ", "").strip()
                        bot_response = kb_response
                    else:
                        bot_response = "Sorry, I couldn't find relevant information from our database."
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history.append({"user": user_input, "bot": bot_response, "timestamp": timestamp})
    conversation_context += f"User: {user_input}\nWallya: {bot_response}\n"

    return jsonify({"response": bot_response})

@app.route('/new_chat', methods=['POST'])
def new_chat():
    global chat_history, conversation_context
    chat_history = []
    conversation_context = ""
    return jsonify({"message": "New chat started"})

@app.route('/register', methods=['POST'])
def register():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        
        # Validate the input data using the schema
        schema = RegistrationSchema()
        validated_data = schema.load(data)
        
        # Insert into MongoDB
        result = register_collection.insert_one(validated_data)
        
        # Return success response
        return jsonify({
            "message": "Registration successful",
            "user_id": str(result.inserted_id),
            "data": schema.dump(validated_data)
        }), 201
        
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.messages}), 400
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500
    
@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        users = register_collection.find({}, {
        })
        
        # Convert users to list and parse ObjectId
        users_list = json.loads(json_util.dumps(list(users)))
        
        return jsonify(users_list), 200
        
    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)