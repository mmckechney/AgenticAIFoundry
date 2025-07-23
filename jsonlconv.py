import json

# Input and output file paths
#input_path = 'finetunedata/train.jsonl'
#output_path = 'finetunedata/converted_train.jsonl'

input_path = 'finetunedata/val.jsonl'
output_path = 'finetunedata/converted_val.jsonl'

# System message to use for all entries
system_message = {"role": "system", "content": "I am AI assistant to help with your queries."}

with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
    for line in infile:
        try:
            data = json.loads(line)
            prompt = data.get('prompt', '').strip()
            response = data.get('response', '').strip()

            converted = {
                "messages": [
                    system_message,
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response}
                ]
            }

            # Write each converted object as a new line in output file
            outfile.write(json.dumps(converted, ensure_ascii=False) + '\n')
        except json.JSONDecodeError as e:
            print(f"Skipping invalid JSON line: {e}")
