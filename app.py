import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

app = Flask(__name__)
CORS(app)  # <-- this is what fixes the CORS/OPTIONS issue

# ---------------------------------------------------------
# STEP 2 — Gemini client
# ---------------------------------------------------------
client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

# ---------------------------------------------------------
# STEP 3 — Model + system instruction
# ---------------------------------------------------------
model = "gemini-3.5-flash-lite"

agent_system_instruction = """
You are a professional AI customer support agent for TechStore.

Your job is to help customers with products, pricing, shipping, returns, and support.

Use company information when relevant.
Use the calculator tool whenever a mathematical calculation is required.
Use the search_web tool only when external information is needed.

Never invent information.
If information is unavailable, clearly say that you do not have that information.

Keep responses concise, clear, friendly, and professional.
Do not add unnecessary information or repeated offers of help.
"""

# ---------------------------------------------------------
# STEP 6 — Company knowledge
# ---------------------------------------------------------
company_info = """
Company: TechStore

Products:
- Laptops
- Smartphones
- Headphones
- Smart Watches

Shipping:
- Standard delivery takes 3-5 business days.
- Express delivery takes 1-2 business days.

Returns:
- Products can be returned within 14 days of delivery.
- The product must be unused and in its original packaging.

Support:
- Customer support is available Monday to Friday, 9 AM to 6 PM.
"""

# ---------------------------------------------------------
# STEP 10 — Memory
# ---------------------------------------------------------
conversation_history = []

# ---------------------------------------------------------
# Tools
# ---------------------------------------------------------
def calculator(expression):
    try:
        return eval(expression)
    except Exception:
        return "Unable to calculate the expression."


def search_web(query):
    # Placeholder — replace with a real search API later
    return f"Search requested for: {query}"


calculator_declaration = types.FunctionDeclaration(
    name="calculator",
    description="Calculate a mathematical expression.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "expression": {
                "type": "STRING",
                "description": "The mathematical expression to calculate."
            }
        },
        "required": ["expression"]
    }
)

search_declaration = types.FunctionDeclaration(
    name="search_web",
    description="Search the web for information.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The search query."
            }
        },
        "required": ["query"]
    }
)

tools = types.Tool(
    function_declarations=[
        calculator_declaration,
        search_declaration
    ]
)

agent_config = types.GenerateContentConfig(
    tools=[tools],
    system_instruction=agent_system_instruction
)


def execute_tool(function_call):
    if function_call.name == "calculator":
        return calculator(function_call.args["expression"])
    elif function_call.name == "search_web":
        return search_web(function_call.args["query"])
    return "Unknown tool."


# ---------------------------------------------------------
# STEP 56/57 — run_agent (your exact working logic)
# ---------------------------------------------------------
def run_agent(user_query):
    conversation_history.append({
        "role": "user",
        "content": user_query
    })

    prompt = f"""
    Conversation History:
    {conversation_history}

    Company Information:
    {company_info}

    Customer Question:
    {user_query}

    Use the conversation history when it is relevant.
    Use company information when relevant.
    Use calculator for mathematical calculations.
    Use search_web when external information is needed.
    Never invent information.

    Keep responses concise, clear, friendly, and professional.
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=agent_config
    )

    part = response.candidates[0].content.parts[0]

    if not part.function_call:
        conversation_history.append({
            "role": "assistant",
            "content": response.text
        })
        return response.text

    function_call = part.function_call
    result = execute_tool(function_call)

    tool_response = types.Part(
        function_response=types.FunctionResponse(
            name=function_call.name,
            response={"result": result}
        )
    )

    contents = [
        prompt,
        response.candidates[0].content,
        types.Content(
            role="user",
            parts=[tool_response]
        )
    ]

    final_response = client.models.generate_content(
        model=model,
        contents=contents,
        config=agent_config
    )

    conversation_history.append({
        "role": "assistant",
        "content": final_response.text
    })

    return final_response.text


# ---------------------------------------------------------
# Flask routes
# ---------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"reply": "Please type a message."}), 400

    try:
        reply = run_agent(user_message)
    except Exception as e:
        print("ERROR in run_agent:", e)
        return jsonify({"reply": "Sorry, something went wrong on the server."}), 500

    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
