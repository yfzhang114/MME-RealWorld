import os
import torch.nn as nn
import pandas as pd
from tqdm import tqdm
import json
import os.path as osp
import hashlib
import pickle
from huggingface_hub import scan_cache_dir

def toliststr(s):
    if isinstance(s, str) and (s[0] == '[') and (s[-1] == ']'):
        return [str(x) for x in eval(s)]
    elif isinstance(s, str):
        return [s]
    elif isinstance(s, list):
        return [str(x) for x in s]
    raise NotImplementedError

def get_cache_path(repo_id, branch=None):
    hf_cache_info = scan_cache_dir()
    repos = list(hf_cache_info.repos)
    repo = None
    for r in repos:
        if r.repo_id == repo_id:
            repo = r
            break
    if repo is None:
        return None
    revs = list(repo.revisions)
    if branch is not None:
        revs = [r for r in revs if r.refs == frozenset({branch})]
    rev2keep, last_modified = None, 0
    for rev in revs:
        if rev.last_modified > last_modified:
            rev2keep, last_modified = rev, rev.last_modified
    if rev2keep is None:
        return None
    return str(rev2keep.snapshot_path)

def file_size(f, unit='GB'):
    stats = os.stat(f)
    div_map = {
        'GB': 2 ** 30,
        'MB': 2 ** 20,
        'KB': 2 ** 10,
    }
    return stats.st_size / div_map[unit]

def md5(s):
    hash = hashlib.new('md5')
    if osp.exists(s):
        with open(s, 'rb') as f:
            for chunk in iter(lambda: f.read(2**20), b''):
                hash.update(chunk)
    else:
        hash.update(s.encode('utf-8'))
    return str(hash.hexdigest())

def load(f, fmt=None):
    def load_pkl(pth):
        return pickle.load(open(pth, 'rb'))

    def load_json(pth):
        return json.load(open(pth, 'r', encoding='utf-8'))

    def load_jsonl(f):
        lines = open(f, encoding='utf-8').readlines()
        lines = [x.strip() for x in lines]
        if lines[-1] == '':
            lines = lines[:-1]
        data = [json.loads(x) for x in lines]
        return data

    def load_xlsx(f):
        return pd.read_excel(f)

    def load_csv(f):
        return pd.read_csv(f)

    def load_tsv(f):
        return pd.read_csv(f, sep='\t')

    handlers = dict(pkl=load_pkl, json=load_json, jsonl=load_jsonl, xlsx=load_xlsx, csv=load_csv, tsv=load_tsv)
    if fmt is not None:
        return handlers[fmt](f)

    suffix = f.split('.')[-1]
    return handlers[suffix](f)


import base64
import io
from PIL import Image

def decode_base64_to_image(base64_string, target_size=-1):
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    if image.mode in ('RGBA', 'P'):
        image = image.convert('RGB')
    if target_size > 0:
        image.thumbnail((target_size, target_size))
    return image


def decode_base64_to_image_file(base64_string, image_path, target_size=-1):
    image = decode_base64_to_image(base64_string, target_size=target_size)
    image.save(image_path)
    
class MMERealWorld(nn.module):

    DATASET_MD5 = {
        'MME-RealWorld': '7d7cc66f7fe0f56ebc68fdddf2b447da',
        'MME-RealWorld-CN': 'cbec7caf59402a4167872abbdca1d6bd',
    }
    SYS = {
        'MME-RealWorld': 'Select the best answer to the above multiple-choice question based on the image. \
            Respond with only the letter (A, B, C, D, or E) of the correct option. \nThe best answer is:',
        'MME-RealWorld-CN': '根据图像选择上述多项选择题的最佳答案。只需回答正确选项的字母（A, B, C, D 或 E）。\n 最佳答案为：',
    }

    @classmethod
    def supported_datasets(cls):
        return ['MME-RealWorld', 'MME-RealWorld-CN']

    def load_data(self, dataset='MME-RealWorld', repo_id='yifanzhang114/MME-RealWorld-Base64'):
        def check_integrity(pth):
            data_file = osp.join(pth, f'{dataset}.tsv')

            if not os.path.exists(data_file):
                return False

            if md5(data_file) != self.MD5:
                return False
            data = load(data_file)
            for video_pth in data['video_path']:
                if not osp.exists(osp.join(pth, video_pth)):
                    return False
            return True
        
        def generate_tsv(pth):
            tsv_file = os.path.join(pth, f'{dataset}.tsv')

            if os.path.exists(tsv_file):
                print(f'{tsv_file} already exists.')
                return

            json_dir = os.path.join(pth, dataset)
            json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

            data_list = []
            for json_file in json_files:
                with open(os.path.join(json_dir, json_file), 'r') as f:
                    data = json.load(f)
                    for item in tqdm(data):
                        choice_prompt = 'The choices are listed below:\n' if dataset == 'MME-RealWorld' else '选项如下所示:\n'
                        data_list.append({
                            'index': item['index'],
                            'image': item['image'],
                            'question': item['question'],
                            'multi-choice options': choice_prompt + '\n'.join(item['multi-choice options']),
                            'answer': item['answer'],
                            'category': item['category'],
                            'l2-category': item['l2-category']
                        })
            df = pd.DataFrame(data_list)
            df.to_csv(tsv_file, sep='\t', index=False)
            print(f'TSV file saved to {tsv_file}')

        # Check if dataset is cached and has integrity
        update_flag = False
        cache_path = get_cache_path(repo_id)
        if cache_path is not None and check_integrity(cache_path):
            dataset_path = cache_path
            print(f'Using cached dataset from {cache_path}')
        else:
            from huggingface_hub import snapshot_download
            # Download or find the dataset path
            dataset_path = snapshot_download(repo_id=repo_id, repo_type='dataset')
            generate_tsv(dataset_path)
            update_flag = True

        data_path = os.path.join(dataset_path, f'{dataset}.tsv')
        if file_size(data_path, 'GB') > 1:
            local_path = data_path.replace('.tsv', '_local.tsv')
            if not osp.exists(local_path) or os.environ.get('FORCE_LOCAL', None) or update_flag:
                from vlmeval.tools import LOCALIZE
                LOCALIZE(data_path, local_path)
            data_path = local_path
        return load(data_path)

    # Given one data record, return the built prompt (a multi-modal message), can override
    def build_prompt(self, line):
        if isinstance(line, int):
            line = self.data.iloc[line]

        if self.meta_only:
            tgt_path = toliststr(line['image_path'])
        else:
            tgt_path = self.dump_image(line)

        question = line['question']

        choice_prompt = line['multi-choice options'] + '\n'
        question += choice_prompt + self.SYS[self.dataset_name] + '\nThe best answer is:'

        msgs = []
        if isinstance(tgt_path, list):
            msgs.extend([dict(type='image', value=p) for p in tgt_path])
        else:
            msgs = [dict(type='image', value=tgt_path)]
        msgs.append(dict(type='text', value=question))
        return msgs