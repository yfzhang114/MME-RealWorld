import json
import os
import re
import argparse
from tqdm import tqdm 
parser = argparse.ArgumentParser()
parser.add_argument("--results_file", type=str, default='')
args = parser.parse_args()

TASKS = [
    "Reasoning",
    "Perception",
]

SUBTASKS = [
    "Monitoring",
    "OCR with Complex Context",
    "Diagram and Table",
    "Autonomous_Driving",
    'Remote Sensing'
]

def extract_characters_regex(s, choices):
    s = s.strip()
    answer_prefixes = [
        "The best answer is",
        "The correct answer is",
        "The answer is",
        "The answer",
        "The best option is"
        "The correct option is",
        "Best answer:"
        "Best option:",
    ]
    for answer_prefix in answer_prefixes:
        s = s.replace(answer_prefix, "")

    if len(s.split()) > 10 and not re.search("[ABCDE]", s):
        return ""
    matches = re.search(r'[ABCDE]', s)
    if matches is None:
        for choice in choices:
            if s.lower() in choice.lower():
                return choice[1]
        return ""
    return matches[0]

print(args.results_file)
file_path = os.path.expanduser(args.results_file)

# Check the file extension and process accordingly
if file_path.endswith(".jsonl"):
    # For JSONL files (line-delimited JSON)
    data = [json.loads(line) for line in open(file_path, "r")]
elif file_path.endswith(".json"):
    # For standard JSON files
    with open(file_path, "r") as f:
        data = json.load(f)  # Load the entire JSON file as a single object
else:
    raise ValueError(f"Unsupported file format: {file_path}")

cnt = 0

results = {}
for task in TASKS:
    results[f'{task}'] = {}
    for subtask in SUBTASKS:
        results[f'{task}'][f'{subtask}'] = {}
        
for question in tqdm(data):
    Task = question['Task']
    Subtask = question['Subtask']
    Category = question['Category'].lower()
    question_id = question["Question_id"]
    ground_truth = question["Ground truth"]
    text = question["Output"]
    
    if 'attribute' in Category.lower():
        Category = Category.split('/')[0] + '/attribute'
    
    text = extract_characters_regex(text, question['Answer choices'])
    # 检查 Ground Truth 和 text 是否相同
    cnt = ground_truth == text
    
    if Category not in results[Task][Subtask].keys():
        results[Task][Subtask][f'{Category}'] = {'true': cnt, 'false': 1 - cnt, 'is_E': text == 'E'}
    else:
        results[Task][Subtask][f'{Category}']['true'] += cnt
        results[Task][Subtask][f'{Category}']['false'] += 1 - cnt
        results[Task][Subtask][f'{Category}']['is_E'] += text == 'E'



sum_all, succ_all = 0, 0
for task, tasks_values in results.items():
    print(f'*'*32 + f'{task} (Task Start)')
    cnt_task, cnt_E, sum_task = 0, 0, 0
    for substask, subtask_value in tasks_values.items():
        print(f'+'*16 + f'{substask} (Subtask Start)')
        cnt_subtask, sum_subtask, e_subtask = 0, 0, 0
        for category, category_dict in subtask_value.items():
            cnt_subtask += category_dict['true']
            sum_subtask += category_dict['false'] + category_dict['true']
            e_subtask += category_dict['is_E']
            acc = category_dict['true'] / (category_dict['false'] + category_dict['true'])
            print(f'-'*4 + f'\t' + 'Acc ' + '{:.4f}'.format(acc) + f"\t{category.capitalize()} ({category_dict['false'] + category_dict['true']} items)")
        
        if sum_subtask == 0:
            acc_subtasks = 0
            e_subtask = 0
        else:
            acc_subtasks = cnt_subtask / sum_subtask
        print(f'+'*16 + f'\t Acc ' + '{:.4f}'.format(acc_subtasks) + f'\t E choice {e_subtask} \t{substask} ({sum_subtask} items)')
        cnt_task += cnt_subtask
        sum_task += sum_subtask
        cnt_E += e_subtask
    
    if sum_task == 0:
        acc_task = 0
    else:
        acc_task = cnt_task / sum_task
    succ_all += cnt_task
    sum_all += sum_task
    print(f'*'*32 + f'Acc ' + '{:.4f}'.format(acc_task) + f'\t E choice {cnt_E} \t{task} ({sum_task} items)\n')
    
print(f'*'*32 + f'Overall Acc ' + '{:.4f}'.format(succ_all / sum_all))