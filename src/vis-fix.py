# ___________________________________________
# RUN AS -> python vis-fix.py --<photofile>
# Include file extension!
# ___________________________________________

from PIL import Image
import io, base64, os, sys
from openai import OpenAI, RateLimitError, pydantic_function_tool

from dotenv import load_dotenv, find_dotenv
from tavily import TavilyClient

from pydantic import BaseModel, Field


load_dotenv(find_dotenv())
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=TAVILY_API_KEY)

script_dir = os.path.dirname(os.path.abspath(__file__))

sys.stderr = open(os.path.join(script_dir, "debug.txt"), "w", encoding="utf-8")

instructions_path = os.path.join(script_dir, "INSTRUCTIONS.md")
with open(instructions_path, "r", encoding="utf-8") as f:
    instructions = f.read().strip()


def process_image(path):
    with Image.open(path) as img:
        print(f"Before processing image: size={img.size}", file=sys.stderr)
        img = img.convert("RGB") # Remove alpha channel, no transparency pixels.
        img.thumbnail((1024, 1024)) # Proportional resize
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        print(f"After processing image: size={img.size}", file=sys.stderr)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")  # Base64 produces an ASCII encoded string, safer processing than raw binary.
    

class web_search(BaseModel):
    """Tool used to search in the web for technical documentation, coding errors, and other details to help with debugging"""
    query: str = Field(description="The search query to use based on the screenshot")
    


def format_web_search(raw_response: dict) -> str:
    """Convert search results into LLM-friendly context."""
    web_results = [f"Web search for query: {raw_response['query']}\n"]

    # If answer attribute is not null in dictionary param
    if raw_response.get("answer"):
        web_results.append(f"Summary: {raw_response['answer']}\n")

    web_results.append("Sources:")
    for i, result in enumerate(raw_response["results"], 1):
        web_results.append(
            f"\n{i}. {result['title']}\n"
            f"   URL: {result['url']}\n"
            f"   Content: {result['content']}\n"
            f"   Relevance score: {result['score']:.2f}"
        )

    return "\n".join(web_results)


def main():
    try:
        openai = OpenAI(
          base_url="https://openrouter.ai/api/v1",
          api_key=OPENROUTER_API_KEY
        )

        image_dir = os.path.abspath(os.path.join(script_dir, "..", "image_tests"))

        # Flag with image
        image = sys.argv[1].strip()

        if not image.startswith('--'):
            raise ValueError('Missing image flag. Usage: --[namefile]. Include extension.')

        image = image.removeprefix('--')

        print("🔎🤔 Analyzing your image's bugs... stand by.")

        image_bs64 = process_image(os.path.join(image_dir, image))
        print(f"Size of the Base64 string: {len(image_bs64)}", file=sys.stderr)
        image_content = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_bs64}"}
        }
        messagesPack = [
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Here is the picture you need to analyze."},
                    image_content
                ]
            }
        ]
        
        i = 0 
        while i < 5:
            i += 1
            print(f"ITERATION #{i}", file=sys.stderr)
            
            kimik = openai.chat.completions.parse(
                model="moonshotai/kimi-k2.5",
                messages=messagesPack,
                tools=[pydantic_function_tool(web_search)],
                tool_choice="auto"
            )
            message = kimik.choices[0].message

            # Update conversation with LLM
            messagesPack.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": message.tool_calls
            })
            
            # Used in case that tool calls fail repeteadly
            wrongAttempts = 0
            if message.tool_calls:
                print(f"LLM CALL #{i}", file=sys.stderr)
                for tool_call in message.tool_calls:
                    if tool_call.type == 'function' and tool_call.function.name == 'web_search':
                        print(f"Model required to use the tool: {tool_call.function.name}\n", file=sys.stderr)

                        # Arguments that the model suggests for the tool
                        args = tool_call.function.parsed_arguments

                        print(f"Query suggested by model: {args.query}\n", file=sys.stderr)

                        # Web search with model's query
                        raw_response = tavily.search(
                            query=args.query,
                            search_depth="advanced",
                            max_results=8,
                            include_answer=True,
                            include_raw_content=False,
                            include_images=False
                        )

                        # LLM friendly content, only with necessary data
                        web_context = format_web_search(raw_response)

                        # Append tool output
                        messagesPack.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": web_context
                        })
                    else:
                        # A wrong tool was requested, go to next tool call 
                        print(f"Model required to use something unexpected: {tool_call.type}\n", file=sys.stderr)
                        wrongAttempts += 1

                        # Go to next iteration if too many bad calls 
                        if wrongAttempts > 2: break

                        # Append the wrong tool call for the record of the LLM
                        messagesPack.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Unsupported tool requested: {tool_call.type}. Available tool: web_search(query)"
                        })

            # No more tool calls from LLM
            else:
                break

        # Ensure valid state for output, not empty
        final_output = message.content or "😕 No valid answers from Kimi K."
        print(f"\n🤖 Analyzer says:\n\n{final_output}\n")
                  
    except RateLimitError:
        print("Rate limit exceeded. Please wait and try again later.", file=sys.stderr)
        sys.exit(1)

    except Exception as err:
        print(f"🔴 An error occurred: {err}")
        sys.exit(1)

main()