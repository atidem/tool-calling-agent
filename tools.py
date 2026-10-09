import numexpr

###################################################
## FUNCTIONS

def calculator(expr):
    """standart calculator from text"""
    try:
        result = numexpr.evaluate(expr)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


####################################################
## TOOL DEFINITIONS

CACULATOR_TOOL = {"name": "calculator",
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

####################################################
## REGISTRIES TO AGENT

TOOLS = [CACULATOR_TOOL]
TOOL_FUCTIONS = {"calculator":calculator}