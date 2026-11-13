import numexpr
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from ddgs import DDGS


###################################################
## CONS
ALLOWED_DIR = (Path(__file__).resolve().parent/"data").resolve()
MAX_BYTES = 50_000
MAX_RESULTS = 5
MAX_CHAR = 450


###################################################
## FUNCTIONS

def calculator(expression):
    """standart calculator from text"""
    try:
        result = numexpr.evaluate(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def getTime(timezone):
    try:
        tz = ZoneInfo(timezone)
        now = datetime.now(tz)
        return f"{now.strftime('%A, %Y-%m-%d %H:%M:%S %Z')} ({timezone})"
    except (ZoneInfoNotFoundError, ValueError):
        return (
            f"Error: unknown timezone '{timezone}'. "
            "Use IANA format like Asia/Dubai or Europe/Istanbul."
        )

def readFile(path):
    target = (ALLOWED_DIR / path).resolve()

    if not target.is_relative_to(ALLOWED_DIR):
        return "Error: access denied. Only files inside the data folder can be read."
    
    if not target.is_file():
        return f"Error: file '{path}' not found in the data folder."

    if target.stat().st_size > MAX_BYTES:
        return f"Error: file '{path}' is too large (limit {MAX_BYTES} bytes)."

    try:
        return target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: file '{path}' is not a readable text file."
    
def webSearch(query,maxResults=5):
    maxResults = max(1, min(maxResults, 5))

    try: 
        results = DDGS().text(query,max_results = maxResults)
    except Exception as e:
        return (f"Error: search failed ({e}). Try a different query, or tell the user "
            "that up-to-date information could not be found. "
            "Do not answer from memory about recent events.")
    
    if not results:
        return f"No results found for '{query}'"

    blocks = []
    for i,r in enumerate(results,start=1):
        title = r.get("title","")
        url = r.get("href","")
        body = r.get("body","") 
        if len(body)>MAX_CHAR:
            body = body[:MAX_CHAR]+ "..."
        
        blocks.append(f"[{i}]  {title}\n{url}\n{body}")
    
    return "\n\n".join(blocks)


####################################################
## TOOL DEFINITIONS

CALCULATOR_TOOL = {"name": "calculator",
                    "description": (
                    "Evaluates a mathematical expression. Supports addition, subtraction, "
                    "multiplication, division, exponents and parentheses. Use this tool "
                    "whenever a numerical calculation is needed instead of estimating "
                    "the result yourself."),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "expression": {
                        "type": "string",
                        "description": "The expression to evaluate. Use * for multiplication and ** for exponents. Example: (12 + 3) * 4",
                                        }
                                    },
                    "required": ["expression"],
                                },
                }
GET_TIME_TOOL = {"name": "getTime",
                    "description": (
                    "Returns the current date and time in a given timezone. Use this tool whenever the user asks about the current time"
                     " or date in a city or region."),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                        "type": "string",
                        "description": "IANA timezone name in Region/City format. Convert city names to this format. "
                        "Examples: Asia/Dubai, Europe/Istanbul, America/New_York",
                                        }
                                    },
                    "required": ["timezone"],
                                },
                }

READ_FILE_TOOL = {"name": "readFile",
                    "description": (
                    "Reads a text file from the local data folder and returns its content. "
                    "Use this tool when the user asks about the content of a file. "
                    "Only files inside the data folder can be read, "
                    "and only text files are supported."),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                        "type": "string",
                        "description": "Path of the file relative to the data folder. Example: notes.txt",
                                        }
                                    },
                    "required": ["path"],
                                },
                }

WEBSEARCH_TOOL = {"name":"webSearch",
                    "description":(
                    "When you need to research something on Internet,"
                    "use this tool to get more and updated knowledge. Searches the web and returns the top results,"
                    " each with a title, URL and a short snippet. Use this tool for current events,"
                    " recent facts, or anything that may have changed after your training data."
                    "Always cite the sources you used with their numbers and URLs in your answer. If the sources disagree, mention it."),
                "input_schema":{
                    "type":"object",
                    "properties":{
                        "query":{
                            "type":"string",
                            "description": "Short search query with keywords. Example: cost of living US 2026"
                        },
                        "maxResults": {
                            "type": "integer",
                            "description": "Number of results to return, between 1 and 5. Default: 5.",
                            "minimum": 1,
                            "maximum": 5,
                        },
                    },
                "required":["query"],
                            },
                }


####################################################
## REGISTRIES TO AGENT

TOOLS = [CALCULATOR_TOOL, GET_TIME_TOOL,READ_FILE_TOOL,WEBSEARCH_TOOL]
TOOL_FUNCTIONS = {"calculator":calculator,"getTime":getTime,"readFile":readFile,"webSearch":webSearch}