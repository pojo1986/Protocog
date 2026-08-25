#playwright and ollama, along with python MUST be installed... I think
#this python script should automatically train coglet.
# this likely won't work yet since the ollama Ai agent has no way of reading coglet messages
import asyncio
from playwright.async_api import async_playwright
import ollama
#model can be changed. make sure its actually installed though
MODEL_NAME = "llama3"

async def get_ollama_reply(coglet_message):
    """Feeds the coglet's chaotic message to Ollama to get a response."""
    prompt = (
        f"You are talking to a simple text-based AI 'coglet' that speaks in broken, chaotic phrases. At the start, it will know no words. Feed it useful words with simple meaning like hello, or phrases like how are you? "
        f"The coglet just said: '{coglet_message}' "
        f"Reply to it directly using simple words, correct grammar, and clear phrasing to help train it. "
        f"Do not include any narrator notes, quotes, or meta-commentary. Output ONLY your direct reply."
        f"Keep the responses 1-2 sentences, being very short ones."
        f"Coversations will help it response appropriately when actual conversations are being had, the goal."
    )
    try:
        response = ollama.generate(model=MODEL_NAME, prompt=prompt)
        return response['response'].strip().strip('"')
    except Exception as e:
        print(f"Ollama Error: {e}")
        return "That is interesting. Let us keep talking."

async def run_interactive_training():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Opening ProtoCog...")
        await page.goto("https://r74n.com/mini/protocog")
        await page.wait_for_timeout(3000) 
        
        
        last_seen_message = ""
        
        print("Listening to the coglet... Press Ctrl+C to exit.")
        
        while True:
            try:
                
                # Note: If R74n updates the class names, adjust '.message' to match the DOM container
                messages = await page.query_selector_all(".message, .chat-line, p")
                
                if messages:
                    
                    latest_msg_element = messages[-1]
                    latest_text = (await latest_msg_element.inner_text()).strip()
                    
                    
                  
                    if latest_text != last_seen_message and "coglet" in latest_text.lower():
                        last_seen_message = latest_text
                        print(f"👶 Coglet muttered: {latest_text}")
                        
                        
                        ollama_reply = await get_ollama_reply(latest_text)
                        print(f"🤖 Ollama replies: {ollama_reply}")
                        
                        
                        input_box = await page.query_selector("input[type='text'], #input")
                        if input_box:
                            await input_box.fill(ollama_reply)
                            await input_box.press("Enter")
                        else:
                            
                            await page.keyboard.type(ollama_reply)
                            await page.keyboard.press("Enter")
                            
            except Exception as e:
                print(f"Error reading or writing to browser: {e}")
                
            await asyncio.sleep(2) 

if __name__ == "__main__":
    asyncio.run(run_interactive_training())
