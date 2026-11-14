import anthropic
import os 
from dotenv import load_dotenv
import streamlit as st
from tools import TOOLS,TOOL_FUNCTIONS
from datetime import datetime
from time import perf_counter
from logger import saveLog,calcCost

#######################################################
MODEL = "claude-haiku-4-5"
load_dotenv()
claudeKEy = os.getenv("claudeKey")

#######################################################
client = anthropic.Anthropic(api_key=claudeKEy)

#######################################################
def generateResponse(messages,turns):
    """ contact with agent """
    start = perf_counter()
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=512,
        tools=TOOLS,
        messages=messages,
        system = build_system_prompt()
    )
    end = perf_counter()

    ## logging each steps 
    toolNames = [b.name for b in response.content if b.type == "tool_use"]
    log = {
        "step": len(turns) + 1,
        "stop_reason": response.stop_reason,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "duration_sec": round(end - start, 2),
        "tools": toolNames,
    }
    
    turns.append(log)

    return response

def build_system_prompt():
    today = datetime.now().strftime("%A, %Y-%m-%d")
    return (
        f"Today's date is {today}.\n\n"
        "Knowledge:\n"
        "- Your training data is reliable only up to early 2025.\n"
        "- For anything that may have changed after that, use webSearch.\n\n"
        "Searching:\n"
        "- If a search fails or is not useful, try a different query, up to 3 searches in total.\n"
        "- If you still have no result, you may answer from your own knowledge only if you are confident, "
        "and you must say that the answer comes from your training data and may be outdated.\n"
        "- Never present a guess as a fact.\n\n"
        "Answering:\n"
        "- When you use search results, cite them with their numbers, e.g. [1], "
        "and list the URLs you used at the end.\n"
        "- If sources disagree, say so.\n"
        "- Keep answers concise."
    )

def toolUsage(usrPrompt,respond,turns,N=10, onTool=None):
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
        respond = generateResponse(messages,turns)

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
    turns = []
    ## first contact with agent 
    respond = generateResponse([{"role":"user","content":prmpt}],turns)

    ## take a look to blocks which have tool usage info 
    for block in respond.content:
        if block.type=="tool_use":
            with st.status("Agent is working...", expanded=True) as status:
                ## go and use your tool dude..
                respond = toolUsage(prmpt, respond, turns, onTool=show_tool)
                status.update(label="🟢 The job is completed by The Agent :) 🟢", state="complete")

    st.warning(f"stop reason:{respond.stop_reason}")

    ## Final message is writed
    finalMessage = next(block for block in respond.content if block.type == "text")
    st.markdown(finalMessage.text)

    
    saveLog(prmpt, finalMessage.text, turns, MODEL)
    totalIn = sum(t["input_tokens"] for t in turns)
    totalOut = sum(t["output_tokens"] for t in turns)
    costUsd = calcCost(MODEL, totalIn, totalOut)
    st.success(f".:Input Token:{totalIn}:.     .:Ouput Token:{totalOut}:.     .:Cost: ${costUsd}:.")

    with st.expander("Raw JSON response"):
        st.json(respond)

    with st.expander("Turn details"):
        st.dataframe(turns)
        
        st.caption(f"{len(turns)} turns · input {totalIn} · output {totalOut} tokens · ${costUsd}")
