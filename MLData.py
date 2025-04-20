import requests
import json
import re
import time
import os

def split_blocks(text):
    return [block.strip() for block in text.strip().split("\n\n") if block.strip()]
def extract_from_block(block):
    lines=[line.strip() for line in block.strip().splitlines() if line.strip()]
    if not lines:
        return None
    last_line=lines[-1].capitalize()

    # Case 1: Answer: Yes/No
    for line in lines:
        if line.lower().startswith("answer:"):
            ans_match=re.match(r'answer:\s*(yes|no)',line,re.IGNORECASE)
            if ans_match:
                answer=ans_match.group(1).capitalize()
                question_lines=[l for l in lines if not l.lower().startswith("answer:")]
                question=" ".join(question_lines).strip('"“” ')
                return (question, answer)

    # Case 2: - Yes - No No
    for line in lines:
        if line.startswith("-"):
            parts=re.findall(r'(Yes|No)', line, re.IGNORECASE)
            if len(parts)>=2:
                return (" ".join(lines), parts[-1].capitalize()) 

    # Case 3: Yes or No?
    for i, line in enumerate(lines):
        if "Yes or No?" in line:
            parts=line.split("Yes or No?")
            question=parts[0].strip('"“” ') + '?'
            trailing=parts[1].strip() if len(parts)>1 else ""
            if trailing in ['Yes','No']:
                return (question, trailing)
            elif last_line in ['Yes','No']:
                return (question,last_line)
            else:
                return (question, "")

    # Case 4: "?"+answer same line or next
    for i, line in enumerate(lines):
        if "?" in line:
            q, *maybe_ans=line.split("?", 1)
            question=q.strip('"“” ') + '?'
            if maybe_ans:
                after=maybe_ans[0].strip().capitalize()
                if after in ['Yes','No']:
                    return (question,after)
            elif i+1<len(lines):
                next_line=lines[i+1].capitalize()
                if next_line in ['Yes','No']:
                    return (question, next_line)
            return (question, "")  

    # Case 5: two lines — one question, one answer
    if len(lines)==2 and last_line in ['Yes','No']:
        return (lines[0].strip('"“” '), last_line)

    return None


def main():
    start=time.perf_counter()
    url = ("https://huggingface.co/datasets/AdaptLLM/finance-tasks/""resolve/main/Headline/test.json")
    resp=requests.get(url)
    resp.raise_for_status()
    data=resp.json()
    results=[]

    for idx, item in enumerate(data):
        input_text=item.get("input", "")
        cid=item.get("class_id")
        gid=item.get("gold_index")

        blocks=split_blocks(input_text)
        for qid, block in enumerate(blocks,start=1):
            pair=extract_from_block(block)
            if pair:
                question,answer=pair
                results.append({
                    "id": f"{idx}_{qid}",
                    "Question": question,
                    "Answer": answer,
                    "class_id": cid,
                    "gold_index": gid
                })
    with open("headline_qa_pairs.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    elapsed = time.perf_counter() - start
    print(f" {len(results):,} pairs, taking {elapsed:.2f} seconds")

if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    os.chdir(current_dir)
    main()
