from tools import calculator_tool, weather_tool, summarizer_tool
import re

def agent_logic(user_input):
    user_input = user_input.lower()
    
    if "weather" in user_input:
        # Extract location (simple heuristic)
        location = user_input.split("in ")[-1].strip() if "in" in user_input else "london"
        print("[Log] Selected Tool: Weather")
        return weather_tool(location)
        
    elif "calculate" in user_input:
        expression = user_input.replace("calculate", "").strip()
        print("[Log] Selected Tool: Calculator")
        return calculator_tool(expression)
        
    elif "summarize" in user_input:
        text = user_input.replace("summarize", "").strip()
        print("[Log] Selected Tool: Summarizer")
        return summarizer_tool(text)
        
    else:
        return "I don't have a tool for that."

if __name__ == "__main__":
    print("🤖 Tool-Using Agent Started.")
    while True:
        query = input("\nYou: ")
        if query.lower() == 'exit': break
        print(f"Agent: {agent_logic(query)}")