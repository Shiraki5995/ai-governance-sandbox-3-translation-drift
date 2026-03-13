import json
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------------------------
# Base directory
# -------------------------------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------
# Load API key from .env
# -------------------------------------------------
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)

# -------------------------------------------------
# Read text file
# -------------------------------------------------
def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# -------------------------------------------------
# Load multilingual policy texts
# -------------------------------------------------
def load_inputs() -> dict:
    input_dir = os.path.join(base_dir, "inputs")

    inputs = {
        "english_original": load_text(os.path.join(input_dir, "original_policy.txt")),
        "french": load_text(os.path.join(input_dir, "french_translation.txt")),
        "german": load_text(os.path.join(input_dir, "german_translation.txt")),
        "italian": load_text(os.path.join(input_dir, "italian_translation.txt")),
        "spanish": load_text(os.path.join(input_dir, "spanish_translation.txt"))
    }

    return inputs

# -------------------------------------------------
# Analyze translation drift with OpenAI
# -------------------------------------------------
def analyze_translation_drift(inputs: dict) -> dict:
    prompt = f"""
You are a governance analysis assistant.

Analyze the following multilingual policy texts.

Tasks:
1. Detect translation drift between the English original and the other languages.
2. Identify key differences in interpretation or emphasis.
3. Extract the shared META CONCEPT behind all versions.
4. Explain the governance implication.

Return JSON only in this format:

{{
  "translation_drift": {{
    "French": "...",
    "German": "...",
    "Italian": "...",
    "Spanish": "..."
  }},
  "meta_concept": "...",
  "governance_implication": "..."
}}

Texts:
{json.dumps(inputs, indent=2, ensure_ascii=False)}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "system",
                "content": "You analyze multilingual governance texts and return structured JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content
    return json.loads(content)

# -------------------------------------------------
# Create CBP Node
# -------------------------------------------------
def create_cbp_node(ai_result: dict) -> dict:
    cbp_node = {
        "concept": "market oversight",
        "intent": "protect market stability",
        "boundary": "monitor high-risk suppliers",
        "rationale": ai_result["governance_implication"],
        "meta_concept": ai_result["meta_concept"],
        "translation_drift": ai_result["translation_drift"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return cbp_node

# -------------------------------------------------
# Save CBP Node to file
# -------------------------------------------------
def save_cbp_node(node: dict) -> str:
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "translation_drift_node.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(node, f, indent=2, ensure_ascii=False)

    return output_path

# -------------------------------------------------
# Main
# -------------------------------------------------
def main() -> None:
    inputs = load_inputs()

    print("Loaded multilingual policy texts:")
    print(json.dumps(inputs, indent=2, ensure_ascii=False))
    print()

    ai_result = analyze_translation_drift(inputs)

    print("AI Analysis:")
    print(json.dumps(ai_result, indent=2, ensure_ascii=False))
    print()

    cbp_node = create_cbp_node(ai_result)

    print("CBP Node created:")
    print(json.dumps(cbp_node, indent=2, ensure_ascii=False))
    print()

    saved_path = save_cbp_node(cbp_node)
    print(f"CBP Node saved to: {saved_path}")

# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    main()