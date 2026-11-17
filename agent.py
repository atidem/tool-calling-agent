import streamlit as st
from core import runAgent, MODEL
from logger import saveLog,calcCost

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
    with st.status("Agent is working...", expanded=True) as status:
        answerText, turns = runAgent(prmpt, onTool=show_tool)
        status.update(label="🟢 The job is completed by The Agent :) 🟢", state="complete")

    st.warning(f"stop reason:{turns[-1]['stop_reason']}")
    st.markdown(answerText)

    saveLog(prmpt, answerText, turns, MODEL)
    totalIn = sum(t["input_tokens"] for t in turns)
    totalOut = sum(t["output_tokens"] for t in turns)
    costUsd = calcCost(MODEL, totalIn, totalOut)
    st.success(f".:Input Token:{totalIn}:.     .:Ouput Token:{totalOut}:.     .:Cost: ${costUsd}:.")

    with st.expander("Turn details"):
        st.dataframe(turns)
        
        st.caption(f"{len(turns)} turns · input {totalIn} · output {totalOut} tokens · ${costUsd}")
