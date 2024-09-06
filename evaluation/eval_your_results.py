import json
import os
import re
import argparse
from tqdm import tqdm 
parser = argparse.ArgumentParser()
parser.add_argument("--results_file", type=str, default='./result.jsonl')
args = parser.parse_args()

TASKS = [
    "Reasoning",
    "Perception",
]

SUBTASKS = [
    "Monitoring",
    "OCR with Complex Context",
    "Diagram and Table",
    'Autonomous_Driving',
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
        "Best answer:",
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
data = [json.loads(q) for q in open(os.path.expanduser(args.results_file), "r")]
cnt = 0

results = {}
for task in TASKS:
    results[f'{task}'] = {}
    for subtask in SUBTASKS:
        results[f'{task}'][f'{subtask}'] = {}
        

for question in tqdm(data):
    Task = question['Task']
    Subtask = question['Subtask']
    Category = question['Category']
    question_id = question["Question_id"]
    ground_truth = question["Ground truth"]
    text = question["Output"]
    
    text = extract_characters_regex(text, question['Answer choices'])
    
    cnt = ground_truth == text
    
    if Category not in results[Task][Subtask].keys():
        results[Task][Subtask][f'{Category}'] = {'true': cnt, 'false': 1-cnt}
    else:
        results[Task][Subtask][f'{Category}']['true'] += cnt
        results[Task][Subtask][f'{Category}']['false'] += 1 - cnt


for task, tasks_values in results.items():
    print(f'*'*32 + f'{task} (Task Start)')
    cnt_task, sum_task = 0, 0
    for substask, subtask_value in tasks_values.items():
        print(f'+'*16 + f'{substask} (Subtask Start)')
        cnt_subtask, sum_subtask = 0, 0
        for category, category_dict in subtask_value.items():
            cnt_subtask += category_dict['true']
            sum_subtask += category_dict['false'] + category_dict['true']
            acc = category_dict['true'] / (category_dict['false'] + category_dict['true'])
            print(f'-'*4 + f'\t' + 'Acc ' + '{:.4f}'.format(acc) + f'\t{category.capitalize()}')
        
        if sum_subtask == 0:
            acc_subtasks = 0
        else:
            acc_subtasks = cnt_subtask / sum_subtask
        print(f'+'*16 + f'\t Acc ' + '{:.4f}'.format(acc_subtasks) + f'\t{substask}')
        cnt_task += cnt_subtask
        sum_task += sum_subtask
    
    if sum_task == 0:
        acc_task = 0
    else:
        acc_task = cnt_task / sum_task
    print(f'*'*32 + f'Acc' + '{:.4f}\n'.format(acc_task) + f'\t{task}')
