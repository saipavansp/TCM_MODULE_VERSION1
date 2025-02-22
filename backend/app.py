from flask import Flask, request, jsonify
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time
import random

from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("Groq_API")
HF_TOKEN = os.getenv("HF_TOKEN")
os.environ['HF_TOKEN'] = HF_TOKEN if HF_TOKEN else ""


def initialize_llm(api_key, retries=3):
    """Initialize Groq LLM with fallback to OpenAI."""
    for attempt in range(retries):
        try:
            return ChatGroq(groq_api_key=api_key, model="llama-3.3-70b-versatile")
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to initialize Groq after {retries} attempts. Error: {str(e)}")
                openai_key = input("Enter OpenAI API key for fallback: ")
                if openai_key:
                    try:
                        return ChatOpenAI(api_key=openai_key)
                    except Exception as openai_error:
                        print(f"Failed to initialize OpenAI fallback. Error: {str(openai_error)}")
                        return None
    return None


# Initialize the LLM
llm = initialize_llm(GROQ_API_KEY)
if llm is None:
    raise Exception("Failed to initialize any language model")

# Load prompts and behaviors from CSV
prompts_file = "prompts.csv"
behavior_file = "Behavior.csv"
df_prompts = pd.read_csv(prompts_file)
df_behaviors = pd.read_csv(behavior_file)


def get_behavior_by_call_number(call_number):
    """Get behavior based on call number (first 5 polite, next 5 rude)."""
    behavior_type = "Polite Customer" if call_number < 5 else "Rude Customer"
    behavior_row = df_behaviors[df_behaviors['Type'] == behavior_type]
    if not behavior_row.empty:
        return {
            'type': behavior_type,
            'behavior': behavior_row.iloc[0]['Behavior']
        }
    return None


def get_random_scenario(used_scenarios=None):
    """Get a random scenario title from the prompts CSV, excluding used ones."""
    if used_scenarios is None:
        used_scenarios = []

    all_scenarios = df_prompts['Title'].tolist()
    available_scenarios = [s for s in all_scenarios if s not in used_scenarios]

    if not available_scenarios:
        return None
    return random.choice(available_scenarios)


def get_prompt_by_scenario(scenario_input: str):
    """Retrieve prompt details based on the provided scenario."""
    try:
        if not scenario_input:
            scenario_input = get_random_scenario()

        result = df_prompts[df_prompts['Title'].str.contains(scenario_input, case=False, na=False)]
        if not result.empty:
            row = result.iloc[0]
            return {
                'Title': row['Title'],
                'Scenario': row['Scenario'],
                'Example Conversation': row['Example Conversation'],
                'Keywords': row['Keywords']
            }
    except Exception as e:
        print(f"Error getting prompt: {str(e)}")
    return None


app = Flask(__name__)


@app.route('/api/get_total_scenarios', methods=['GET'])
def get_total_scenarios():
    """Return total number of available scenarios."""
    try:
        total = len(df_prompts)
        return jsonify({"total": total})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/start_call', methods=['POST'])
def start_call():
    data = request.get_json()
    used_scenarios = data.get('usedScenarios', [])
    call_number = len(used_scenarios)  # Use this to determine behavior

    # Get behavior based on call number
    behavior_data = get_behavior_by_call_number(call_number)
    if behavior_data is None:
        return jsonify({"error": "Failed to get behavior pattern"}), 500

    scenario_input = get_random_scenario(used_scenarios)
    if scenario_input is None:
        return jsonify({"error": "No more unused scenarios available"}), 400

    prompt_details = get_prompt_by_scenario(scenario_input)
    if prompt_details is None:
        return jsonify({"error": "Failed to get scenario prompt"}), 500

    context = (
        f"Title: {prompt_details['Title']}\n"
        f"Scenario: {prompt_details['Scenario']}\n"
        f"Example Conversation: {prompt_details['Example Conversation']}\n"
        f"Keywords: {prompt_details['Keywords']}"
    ).strip()

    return jsonify({
        "context": context,
        "customerGreeting": "Hello",
        "selectedScenario": prompt_details['Title'],
        "behavior": behavior_data['behavior'],
        "behaviorType": behavior_data['type']
    })


@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    user_message = data.get('message', '')
    context = data.get('context', '')
    chat_history = data.get('chatHistory', '')
    behavior = data.get('behavior', '')

    system_prompt_template = """
You are an AI simulating a customer in a telecalling scenario.

SCENARIO CONTEXT:
{context}

BEHAVIOR PATTERN:
{behavior}

INSTRUCTIONS:
1. Follow the scenario context to understand the situation and background
2. Adopt the specified behavior pattern in your responses
3. Maintain consistency with both the scenario and behavior throughout the conversation
4. Keep responses natural and realistic while exhibiting the assigned traits
5. Pay attention to the conversation history for context

CONVERSATION HISTORY:
{chat_history}

CURRENT MESSAGE FROM AGENT:
{input}

Respond as the customer, ensuring your response aligns with both the scenario context and behavior pattern.
    """.strip()

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_template)
    ])

    conversation_chain = chat_prompt | llm
    try:
        response_obj = conversation_chain.invoke({
            "input": user_message,
            "context": context,
            "chat_history": chat_history,
            "behavior": behavior
        })
        response = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
        return jsonify({"response": response.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)