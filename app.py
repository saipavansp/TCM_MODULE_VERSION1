import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time

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

# --- Load Prompt Data from CSV ---
csv_file = "prompts.csv"  # Update with your CSV file path
df_prompts = pd.read_csv(csv_file)

def get_prompt_by_scenario(scenario_input: str):
    """
    Retrieve prompt details based on the provided scenario (or title fragment).
    Searches the 'Title' column for a case-insensitive match.
    """
    result = df_prompts[df_prompts['Title'].str.contains(scenario_input, case=False, na=False)]
    if not result.empty:
        row = result.iloc[0]
        return {
            'Title': row['Title'],
            'Scenario': row['Scenario'],
            'Example Conversation': row['Example Conversation'],
            'Keywords': row['Keywords']
        }
    else:
        return None

def main():
    session_id = "default"
    scenario_input = input("Enter scenario (e.g., busy_customer): ").strip() or "busy_customer"
    
    # Fetch prompt details once based on user input.
    prompt_details = get_prompt_by_scenario(scenario_input)
    if prompt_details is None:
        print(f"No prompt found for scenario '{scenario_input}'. Exiting.")
        return

    # Create a static context from the CSV prompt details.
    context = (
        f"Title: {prompt_details['Title']}\n"
        f"Scenario: {prompt_details['Scenario']}\n"
        f"Example Conversation: {prompt_details['Example Conversation']}\n"
        f"Keywords: {prompt_details['Keywords']}"
    ).strip()
    
    # Build the system prompt template with placeholders.
    # Note: In this simulation, the human (agent) inputs messages and the LLM responds as the customer.
    system_prompt_template = """
You are an AI simulating a customer in a telecalling scenario.
Below is the prompt context for the scenario:
{context}
Conversation so far:
{chat_history}
Agent: {input}
Respond as the customer, maintaining consistency with the previous conversation and the scenario prompt.
Keep responses natural, concise, and realistic.
    """.strip()
    
    # Create the chat prompt template. It expects three input variables: "context", "chat_history", and "input".
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_template)
    ])
    
    # Compose the chain using the new pipe operator.
    conversation_chain = chat_prompt | llm

    # Initialize a conversation history string.
    chat_history = ""
    
    # Simulate phone ringing.
    print("Phone is ringing...")
    time.sleep(2)
    
    # Simulate customer picking up the call and greeting.
    print("Call session started. You (the agent) can now start chatting. Type 'exit' to end the call.")
    customer_greeting = "Hello"
    print("Customer:", customer_greeting)
    chat_history += f"Customer: {customer_greeting}\n"
    
    
    
    # Conversation loop: the agent's input is sent to the chain,
    # and the LLM responds as the customer.
    while True:
        user_message = input("Agent: ").strip()
        if user_message.lower() in ['exit', 'quit']:
            break
        try:
            response_obj = conversation_chain.invoke({
                "input": user_message,
                "context": context,
                "chat_history": chat_history
            })
            response = response_obj.content if hasattr(response_obj, "content") else str(response_obj)
            print("Customer:", response.strip())
            chat_history += f"Agent: {user_message}\nCustomer: {response}\n"
        except Exception as e:
            print(f"Error during chat: {str(e)}")
    
    # Save conversation transcript.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcript_{session_id}_{timestamp}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(chat_history)
    print(f"Call ended and transcript saved to {filename}")

if __name__ == "__main__":
    main()
