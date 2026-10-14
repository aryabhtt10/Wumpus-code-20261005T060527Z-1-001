import random
import html
import pygame
import os
import json
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Massive high-quality local fallback trivia database (45 unique questions)
TRIVIA_DB = [
    # Hunt the Wumpus Trivia
    {"q": "Who created the original 'Hunt the Wumpus' text game in 1973?", "opts": ["Gregory Yob", "Will Crowther", "Don Daglow", "Ken Thompson"], "ans": 0},
    {"q": "In the classic 'Hunt the Wumpus' game, what mathematical shape is the cave network modeled after?", "opts": ["Octahedron", "Icosahedron", "Dodecahedron", "Tetrahedron"], "ans": 2},
    {"q": "In the classic Wumpus game, how many custom arrows does the player start with?", "opts": ["3", "5", "10", "1"], "ans": 1},
    {"q": "What animal helper in Wumpus games grabs you and flies you to a random cave?", "opts": ["Super Bat", "Vampire Bat", "Giant Owl", "Cave Eagle"], "ans": 0},
    {"q": "In Hunt the Wumpus, what dangerous hazards are pitch black and cause instant portal malfunction?", "opts": ["Bottomless Pits", "Acid Pools", "Lava Streams", "Quicksand"], "ans": 0},
    
    # Computer Science & Technology
    {"q": "What does CPU stand for?", "opts": ["Computer Processing Unit", "Central Processing Unit", "Central Peripheral Unit", "Core Power Unit"], "ans": 1},
    {"q": "What does RAM stand for?", "opts": ["Read Access Memory", "Rapid Action Module", "Random Access Memory", "Realtime Active Memory"], "ans": 2},
    {"q": "In programming, which data type holds only a 'True' or 'False' value?", "opts": ["Integer", "String", "Float", "Boolean"], "ans": 3},
    {"q": "What is the time complexity of a standard Binary Search algorithm?", "opts": ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "ans": 1},
    {"q": "Which programming language was developed by James Gosling at Sun Microsystems and released in 1995?", "opts": ["Python", "C++", "Java", "Ruby"], "ans": 2},
    {"q": "What does HTTP stand for in web browser URLs?", "opts": ["Hypertext Transfer Protocol", "High Tech Terminal Page", "Hyperlink Text Transmission Path", "Home Tab Transfer Process"], "ans": 0},
    {"q": "What is the primary language used for styling modern web application pages?", "opts": ["HTML", "SQL", "CSS", "TypeScript"], "ans": 2},
    {"q": "Which data structure operates on a 'Last In, First Out' (LIFO) access pattern?", "opts": ["Queue", "Stack", "Linked List", "Binary Tree"], "ans": 1},
    {"q": "Who is widely considered the world's first computer programmer for her work on Babbage's Analytical Engine?", "opts": ["Ada Lovelace", "Grace Hopper", "Katherine Johnson", "Margaret Hamilton"], "ans": 0},
    {"q": "What is the binary representation of the decimal number 10?", "opts": ["1001", "1010", "1100", "0111"], "ans": 1},

    # Mathematics & Science
    {"q": "What is the square root of 144?", "opts": ["10", "11", "12", "14"], "ans": 2},
    {"q": "What is the closest planet to our Sun in the solar system?", "opts": ["Venus", "Mars", "Mercury", "Earth"], "ans": 2},
    {"q": "What is the chemical symbol for the precious metal Gold?", "opts": ["Ag", "Au", "Gd", "Fe"], "ans": 1},
    {"q": "Approximately how long does it take for light from the Sun to reach the Earth?", "opts": ["8 seconds", "8 minutes", "8 hours", "8 days"], "ans": 1},
    {"q": "Which scientist developed the theory of General Relativity?", "opts": ["Isaac Newton", "Albert Einstein", "Nikola Tesla", "Marie Curie"], "ans": 1},
    {"q": "What is the only mammal capable of true, sustained flight?", "opts": ["Flying Squirrel", "Bat", "Sugar Glider", "Flying Lemur"], "ans": 1},
    {"q": "What gas do plants absorb from the atmosphere during photosynthesis?", "opts": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"], "ans": 2},
    {"q": "How many bones are in a typical adult human skeleton?", "opts": ["156", "206", "256", "306"], "ans": 1},
    {"q": "What is the boiling point of pure water at sea level in degrees Celsius?", "opts": ["50 C", "80 C", "100 C", "120 C"], "ans": 2},
    {"q": "What is the most abundant gas found in Earth's atmosphere?", "opts": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Argon"], "ans": 1},

    # Gaming & Pop Culture
    {"q": "Which sandbox video game is the best-selling video game of all time?", "opts": ["Minecraft", "Tetris", "Grand Theft Auto V", "Wii Sports"], "ans": 0},
    {"q": "Who is the main green-clad protagonist of Nintendo's 'The Legend of Zelda' series?", "opts": ["Zelda", "Link", "Ganon", "Luigi"], "ans": 1},
    {"q": "In the classic arcade game 'Pac-Man', what is the name of the red ghost?", "opts": ["Blinky", "Pinky", "Inky", "Clyde"], "ans": 0},
    {"q": "Which game developer created the popular franchise 'Dark Souls' and 'Elden Ring'?", "opts": ["Bethesda", "FromSoftware", "CD Projekt Red", "BioWare"], "ans": 1},
    {"q": "What was the name of the first commercially successful video game console, released in 1977?", "opts": ["Nintendo Entertainment System", "Atari 2600", "Sega Genesis", "Commodore 64"], "ans": 1},

    # Geography & History
    {"q": "Which ocean is the largest and deepest ocean on Earth?", "opts": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"], "ans": 3},
    {"q": "What is the capital city of Japan?", "opts": ["Kyoto", "Osaka", "Tokyo", "Hiroshima"], "ans": 2},
    {"q": "In which year did the famous passenger ship Titanic strike an iceberg and sink?", "opts": ["1905", "1912", "1923", "1939"], "ans": 1},
    {"q": "Who painted the famous Renaissance masterpiece 'Mona Lisa'?", "opts": ["Michelangelo", "Raphael", "Vincent van Gogh", "Leonardo da Vinci"], "ans": 3},
    {"q": "Which country is the natural habitat and home to the Kangaroo?", "opts": ["New Zealand", "South Africa", "Australia", "Brazil"], "ans": 2},
    {"q": "What is the longest river in the world?", "opts": ["Amazon River", "Nile River", "Yangtze River", "Mississippi River"], "ans": 1},
    {"q": "Which ancient civilization constructed the Great Pyramids of Giza?", "opts": ["Romans", "Aztecs", "Egyptians", "Greeks"], "ans": 2},
    {"q": "What is the capital city of France?", "opts": ["London", "Berlin", "Paris", "Rome"], "ans": 2},
    {"q": "Who was the first President of the United States?", "opts": ["Thomas Jefferson", "Abraham Lincoln", "John Adams", "George Washington"], "ans": 3},
    {"q": "Which country gifted the famous Statue of Liberty to the United States?", "opts": ["France", "Great Britain", "Spain", "Germany"], "ans": 0},
    {"q": "What is the smallest country in the world by land area?", "opts": ["Monaco", "Liechtenstein", "Vatican City", "San Marino"], "ans": 2},
    {"q": "Which mountain is the highest mountain peak above sea level in the world?", "opts": ["K2", "Mount Kilimanjaro", "Mount Everest", "Mount Fuji"], "ans": 2},
    {"q": "What was the name of the ancient trade route that connected China to the Mediterranean?", "opts": ["The Spice Road", "The Silk Road", "The Amber Path", "The Incense Route"], "ans": 1},
    {"q": "Which European country was ruled by the famous leader Napoleon Bonaparte?", "opts": ["France", "Spain", "Italy", "Austria"], "ans": 0},
    {"q": "What is the capital city of Australia?", "opts": ["Sydney", "Melbourne", "Canberra", "Brisbane"], "ans": 2}
]

# Path to workspace-level trivia.json (one level up from game/)
TRIVIA_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'trivia.json'))


def _ensure_trivia_file():
    # If trivia.json exists and contains valid data, load it.
    if os.path.exists(TRIVIA_JSON_PATH):
        try:
            with open(TRIVIA_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass

    # Otherwise, write the internal TRIVIA_DB into trivia.json adding simple hints.
    out = []
    for item in TRIVIA_DB:
        # compute correct answer text when possible
        try:
            correct = item['opts'][item['ans']]
        except Exception:
            correct = None
        hint = f"Starts with '{correct[0]}'" if correct else ""
        new_item = {
            'q': item.get('q'),
            'opts': item.get('opts'),
            'ans': item.get('ans'),
            'hint': hint
        }
        out.append(new_item)

    try:
        with open(TRIVIA_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return out


# Load trivia DB from trivia.json (or create it from built-in DB)
TRY_TRIVIA_DB = _ensure_trivia_file()

# Fetch random trivia, ensuring we prevent repeats using asked_questions tracking
def random_question(difficulty="easy", asked_questions=None):
    if asked_questions is None:
        asked_questions = set()

    # Try fetching from OpenTDB API first
    if HAS_REQUESTS:
        import urllib3
        # Disable SSL warnings for InsecureRequestWarning when using verify=False
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Try fetching up to 5 times if the random API pulls a repeat
        for _ in range(5):
            try:
                url = f"https://opentdb.com/api.php?amount=1&type=multiple&difficulty={difficulty.lower()}"
                # Use verify=False to bypass certificate errors on macOS/Python environments
                response = requests.get(url, timeout=2, verify=False)
                response.raise_for_status()
                
                data = response.json()
                if data.get('results'):
                    item = data['results'][0]
                    q = html.unescape(item['question'])
                    
                    if q in asked_questions:
                        continue  # Question is a repeat, fetch a fresh one
                        
                    correct = html.unescape(item['correct_answer'])
                    incorrect = [html.unescape(ans) for ans in item['incorrect_answers']]
                    
                    # OpenTDB multiple choice has 4 options (1 correct + 3 incorrect)
                    opts = incorrect + [correct]
                    random.shuffle(opts)
                    
                    # Double-check correct answer is present
                    if correct not in opts:
                        opts[0] = correct
                        random.shuffle(opts)
                        
                    ans_idx = opts.index(correct)
                    asked_questions.add(q)
                    return {"q": q, "opts": opts, "ans": ans_idx}
            except Exception:
                break  # If network fails or SSL fails, immediately fall back to local DB
                
    # Fallback to local high-quality trivia loaded from trivia.json
    available = [item for item in TRY_TRIVIA_DB if item.get("q") not in asked_questions]
    if not available:
        # If all questions have been asked, reset history so game never crashes/freezes!
        for item in TRIVIA_DB:
            if item["q"] in asked_questions:
                asked_questions.remove(item["q"])
        available = TRIVIA_DB
        
    choice = random.choice(available)
    # Ensure hint exists on returned choice
    if 'hint' not in choice:
        try:
            correct = choice['opts'][choice['ans']]
            choice['hint'] = f"Starts with '{correct[0]}'"
        except Exception:
            choice['hint'] = ""
    asked_questions.add(choice["q"])
    return choice


def handle_input(event, engine):
    if event.type != pygame.KEYDOWN:
        return

    if event.key == pygame.K_ESCAPE and engine.state == "TRIVIA":
        engine.sound_manager.play("menu select")
        engine.state = "SHOP"
        return

    # Buy a hint for 1 gold
    if event.key == pygame.K_h and engine.state == "TRIVIA":
        engine.sound_manager.play("menu select")
        if getattr(engine, 'coins', 0) >= 1:
            engine.coins -= 1
            # Prefer explicit hint from data; if missing or invalid, compute a fallback.
            raw_hint = engine.current_q.get('hint') if engine.current_q else None
            if not raw_hint or str(raw_hint).lower() in ('none', 'null'):
                # build a simple hint from the correct option's first character
                try:
                    correct = None
                    if engine.current_q and 'opts' in engine.current_q and 'ans' in engine.current_q:
                        opts = engine.current_q.get('opts', [])
                        ans = engine.current_q.get('ans', 0)
                        if 0 <= ans < len(opts):
                            correct = opts[ans]
                    if correct:
                            engine.current_hint = f"Starts with '{str(correct)[0]}'"
                    else:
                        engine.current_hint = ''
                except Exception:
                    engine.current_hint = ''
            else:
                engine.current_hint = raw_hint
            engine.hint_reveal_index = 0
            engine.hint_reveal_tick = 0
            engine.log("Hint purchased for 1 Gold.")
            # Debug: print final hint and remaining coins
            try:
                print(f"[DEBUG] Hint purchased: '{engine.current_hint}' | coins={engine.coins}")
            except Exception:
                print("[DEBUG] Hint purchased, but failed to read hint or coins")
        else:
            engine.log("Not enough gold to buy a hint!")
            print(f"[DEBUG] Hint purchase attempted, not enough gold: coins={getattr(engine,'coins',0)}")
        return

    ans_idx = -1
    if event.key in [pygame.K_1, pygame.K_KP1]:
        ans_idx = 0
    elif event.key in [pygame.K_2, pygame.K_KP2]:
        ans_idx = 1
    elif event.key in [pygame.K_3, pygame.K_KP3]:
        ans_idx = 2
    elif event.key in [pygame.K_4, pygame.K_KP4]:
        ans_idx = 3

    if ans_idx != -1 and ans_idx < len(engine.current_q['opts']):
        engine.sound_manager.play("menu select")
        is_correct = (ans_idx == engine.current_q['ans'])
        engine.resolve_trivia_answer(is_correct)
