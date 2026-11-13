import anthropic
import os 
from dotenv import load_dotenv
import streamlit as st
from tools import TOOLS,TOOL_FUNCTIONS
from datetime import datetime


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
        messages=messages,
        system = build_system_prompt()
    )
    return response

def build_system_prompt():
    today = datetime.now().strftime("%A, %Y-%m-%d")
    return (
        f"Today's date is {today}. "
        "Your own knowledge may be outdated. For current events or recent facts, "
        "rely on webSearch results. If the search fails or returns nothing useful, "
        "tell the user you could not find up-to-date information instead of "
        "answering from memory."
    )

def toolUsage(usrPrompt,respond,N=10, onTool=None):
    """agent helper to use tools agents have"""

    messages = []
    endTurn = False
    messages.append({"role":"user","content":usrPrompt})

    while N>0 and not endTurn:
        N = N-1
        toolResults = []

        messages.append({"role":"assistant","content":respond.content})

        ### scans blocks which have to use tools..
        for block in respond.content:
            if block.type != "tool_use":
                continue
            func = TOOL_FUNCTIONS.get(block.name)
            if func is not None:
                ## call the function from tool pool.
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
            
            ## visualize to call a tool on streamlit
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
## Streamlit 

def show_tool(name, tool_input, result):
    """visualize using a tool"""
    st.code(f"tool: {name}\ninput: {tool_input}\nresult: {result}")

st.header("Agent Reaharsal")
st.divider()

prmpt = st.text_input("So..?")
btnSend = st.button("Send")

if btnSend:
    ## first contact with agent 
    respond = generateResponse([{"role":"user","content":prmpt}])

    ## take a look to blocks which have tool usage info 
    for block in respond.content:
        if block.type=="tool_use":
            with st.status("Agent is working...", expanded=True) as status:
                ## go and use your tool dude..
                respond = toolUsage(prmpt, respond, onTool=show_tool)
                status.update(label="🟢 The job is completed by The Agent :) 🟢", state="complete")

    st.warning(f"stop reason:{respond.stop_reason}")

    ## Final message is writed
    finalMessage = next(block for block in respond.content if block.type == "text")
    st.markdown(finalMessage.text)

    st.success(f"Input Token:{respond.usage.input_tokens} Ouput Token:{respond.usage.output_tokens}")
    with st.expander("Raw JSON response"):
        st.json(respond)