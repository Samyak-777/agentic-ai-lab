import datetime
import re

def parse_input(user_input):
    """Input Handler & Decision Logic"""
    user_input = user_input.lower()
    
    if "calculate" in user_input:
        return "calculator", user_input
    elif "date" in user_input or "time" in user_input:
        return "datetime", None
    elif "hello" in user_input or "hi" in user_input:
        return "greeting", None
    else:
        return "unknown", None

def execute_action(intent, data):
    """Action Execution"""
    if intent == "calculator":
        # Extract math expression using regex
        match = re.search(r'calculate\s+(.*)', data)
        if match:
            expression = match.group(1)
            try:
                # WARNING: eval() is unsafe in production, but fine for a local lab
                result = eval(expression)
                return f"The result is: {result}"
            except:
                return "Sorry, I couldn't calculate that."
    elif intent == "datetime":
        return f"Current date and time: {datetime.datetime.now()}"
    elif intent == "greeting":
        return "Hello! I am your simple rule-based agent. How can I help?"
    else:
        return "I am a simple agent. I only understand greetings, dates, and basic math (e.g., 'calculate 2+2')."

def run_agent():
    print("🤖 Rule-Based Agent Started. Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            break
        
        intent, data = parse_input(user_input)
        response = execute_action(intent, data)
        print(f"Agent: {response}")

if __name__ == "__main__":
    run_agent()