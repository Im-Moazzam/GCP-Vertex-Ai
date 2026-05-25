import re
import json
from pathlib import Path
def process_description_dataset():
    raw_data_path = Path("raw_data/LAS 4_V8_links_data with Descriptions.txt")
    output_dir = Path("normalized_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file_path = Path(output_dir) / "description_dataset.json"
    
    if not raw_data_path.exists():
        print(f"❌ Error: Could not find raw file at '{raw_data_path}'")
        return
    with open(raw_data_path, "r", encoding="utf-8") as f:
        file_text = f.read()
        print("Extracting Natural Language Prompt & Layout Schema Pairs...")
        page_blocks = re.split(r'(?={"pageIndex":\d+)', file_text)

        training_context_library = []

        for block in page_blocks:
            if not block.strip():
                continue
            # 1. Parse out the structured page JSON dictionary inside this block
            json_match = re.search(
                r'({"pageIndex":\d+,"assets":\[.*?\]})', block, re.DOTALL)

            # 2. Extract the natural language description narrative attached to it
            description_match = re.search(
                r'Description:\s*(.*)', block, re.IGNORECASE)

            if json_match and description_match:
                try:
                    page_data = json.loads(json_match.group(1))
                    page_index = page_data["pageIndex"]

                    # Clean up loose line breaks or extra spaces from the text
                    intent_text = description_match.group(1).strip()

                    # Pair the natural language prompt context with the correct output schema
                    pair = {
                        "pageIndex": page_index,
                        "natural_language_intent": intent_text,
                        "expected_layout_json": page_data
                    }
                    training_context_library.append(pair)
                    print(
                        f"✅ Paired Page Index [{page_index}] with descriptive intent.")

                except json.JSONDecodeError:
                    # Safe pass for top-level structural settings configurations
                    continue

        # Save our clean, structured few-shot context files to our normalized path
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            json.dump(training_context_library, out_f, indent=2)

        print(f"\n🎉 Success! Library generated at: '{output_file_path}'")
        print(
            f"📦 Total validated learning pairs ready: {len(training_context_library)}")


if __name__ == "__main__":
    process_description_dataset()
