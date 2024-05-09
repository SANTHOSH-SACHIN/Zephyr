import streamlit as st
from groq import Groq, InternalServerError

# Groq API Key
API_KEY = st.secrets["GROQ_API_TOKEN"]

# Initialize the Groq API
client = Groq(api_key=API_KEY)

# App title
st.set_page_config(page_title="Llama 2 Chatbot")

# Sidebar
with st.sidebar:
    st.title('Zephyr AI')
    model_options = ["mixtral-8x7b-32768", "llama3-70b-8192", "llama3-8b-8192", "gemma-7b-it"]
    llm = st.selectbox("Select a model", model_options, index=1)

# Model parameters (based on OpenAI's GPT-4 or Anthropic's Claude/Gemini)
temperature = 0.7  # OpenAI's GPT-4 temperature

# Store LLM generated responses
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

def generate_groq_response(prompt_input, llm):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"{string_dialogue} {prompt_input} Assistant:"}
            ],
            model=llm,
            temperature=temperature
        )
        return response.choices[0].message.content
    except InternalServerError as e:
        st.error(f"An error occurred: {e}")

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_groq_response(prompt, llm)
                if response:
                    message = {"role": "assistant", "content": response}
                    st.session_state.messages.append(message)
                    st.write(response)