import anthropic
import os 
from dotenv import load_dotenv
import streamlit as st
from tools import TOOLS,TOOL_FUCTIONS

#######################################################
load_dotenv()
claudeKEy = os.getenv("claudeKey")

#######################################################
client = anthropic.Anthropic(api_key=claudeKEy)

#######################################################
def generateResponse(prmpt):

    response = client.beta.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        tools=TOOLS,
        messages=[{"role":"user","content":prmpt}]
        
    )
    return response

########################################################
st.header("Agent Reaharsal")
st.divider()

prmpt = st.text_input("So..?")
btnSend = st.button("Send")

if btnSend:
    respond = generateResponse(prmpt)

    for block in respond.content:
        if block.type == "text":
            st.markdown(block.text)
        elif block.type=="tool_use":
            st.warning(f"tool name: {block.name}\n\ntool input: {block.input}\n\ntool id: {block.id}")


    st.warning(f"stop reason:{respond.stop_reason}")
    st.success(f"🟢 Input Token:{respond.usage.input_tokens} Ouput Token:{respond.usage.output_tokens}")
    
