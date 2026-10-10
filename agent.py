import anthropic
import os 
from dotenv import load_dotenv
import streamlit as st
from tools import TOOLS,TOOL_FUNCTIONS

#######################################################
load_dotenv()
claudeKEy = os.getenv("claudeKey")

#######################################################
client = anthropic.Anthropic(api_key=claudeKEy)

#######################################################
def generateResponse(messages):
    """ contact with agent """

    response = client.beta.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        tools=TOOLS,
        messages=messages
    )
    return response

def toolUsage(usrPrompt,respond,N=10, onTool=None):
    """agent helper to use tools agents have"""

    messages = []
    endTurn = False
    messages.append({"role":"user","content":usrPrompt})

    while N>0 and not endTurn:
        N = N-1
        toolResults = []

        messages.append({"role":"assistant","content":respond.content})

        for block in respond.content:
            if block.type != "tool_use":
                continue
            func = TOOL_FUNCTIONS.get(block.name)
            if func is not None:
                res = func(**block.input)
                isErr = res.startswith("Error")
            else:
                res,isErr = f"Err: ! Tool: {block.name}",True
            toolResults.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": res,
                "is_error": isErr,
            })

            if onTool:
                 onTool(block.name, block.input, res)

        messages.append({"role": "user", "content": toolResults})
        respond = generateResponse(messages)

        ## stop mechanism
        if respond.stop_reason == "end_turn":
            endTurn = True
        else :
            if respond.stop_reason == "max_tokens":
                return "!!! Max Token...."
            if N == 0:
                return "!!! MAX ITR 10 is completed.."
        
    return respond
########################################################

def show_tool(name, tool_input, result):
    st.code(f"tool: {name}\ninput: {tool_input}\nresult: {result}")

st.header("Agent Reaharsal")
st.divider()

prmpt = st.text_input("So..?")
btnSend = st.button("Send")

if btnSend:
    respond = generateResponse([{"role":"user","content":prmpt}])

    for block in respond.content:
        if block.type=="tool_use":
            with st.status("Agent is working...", expanded=True) as status:
                respond = toolUsage(prmpt, respond, onTool=show_tool)
                status.update(label="🟢 The job is completed by The Agent :) 🟢", state="complete")

    st.warning(f"stop reason:{respond.stop_reason}")

    finalMessage = next(block for block in respond.content if block.type == "text")
    st.markdown(finalMessage.text)

    st.success(f"Input Token:{respond.usage.input_tokens} Ouput Token:{respond.usage.output_tokens}")
    with st.expander("Raw JSON response"):
        st.json(respond)