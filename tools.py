import numexpr
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

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

ALLOWED_DIR = (Path(__file__).resolve().parent/"data").resolve()
MAX_BYTES = 50_000
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

####################################################
## REGISTRIES TO AGENT

TOOLS = [CALCULATOR_TOOL, GET_TIME_TOOL,READ_FILE_TOOL]
TOOL_FUNCTIONS = {"calculator":calculator,"getTime":getTime,"readFile":readFile}