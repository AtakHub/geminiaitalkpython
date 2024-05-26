import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Path to your service account key JSON file
service_account_key_path = 'config/empathy-d0ae8-firebase-adminsdk-j6x9z-ca3a444671.json'

# Initialize the Firebase Admin SDK
try:
    cred = credentials.Certificate(service_account_key_path)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    raise

# Get a reference to the Firestore database
db = firestore.client()

# Reference to the collection and document you want to get data from
collection_name = 'answers'
document_name = 'user1'

doc_ref = db.collection(collection_name).document(document_name)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure the generative AI
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.0-pro")
chat = model.start_chat(history=[])

# Initial length of the array
previous_length = 0

# Main loop
while True:
    try:
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data_array = list(data.values())
            current_length = len(data_array)
            if current_length > previous_length:
                message = data_array[-1]  # Accessing the last element using negative indexing
                response = chat.send_message(message)
                print(f'You: {data_array[-1]}')

                print("\n")
                print(f"bot: {response.text}")
                print("\n")
                response_data = {
                    'message': message,
                    'response': response.text
                }
                db.collection('responses').add(response_data)
                previous_length = current_length

                previous_length = current_length
        else:
            print('No such document!')
    except Exception as e:
        print(f'Error getting document: {e}')
    time.sleep(1)  # Wait for 1 second before checking again
