# MME-RealWorld: Could Your Multimodal LLM Challenge High-Resolution Real-World Scenarios that are Difficult for Humans?

![VQA](https://img.shields.io/badge/Task-ImageQA-red) 
![Multi-Modal](https://img.shields.io/badge/Task-Multi--Modal-red) 
![MME-RealWorld](https://img.shields.io/badge/Dataset-MME--RealWorld-blue)  
![Gemini](https://img.shields.io/badge/Model-Gemini-green) 
![GPT-4V](https://img.shields.io/badge/Model-Claude-green) 
![GPT-4o](https://img.shields.io/badge/Model-GPT--4o-green)

<p align="center">
    <img src="./asset/name_logo.jpg" width="100%" height="100%">
</p>

<font size=7><div align='center' > [[🍎 Project Page](https://mme-realworld.github.io/)] [[📖 arXiv Paper](https://arxiv.org/pdf/2405.21075)] [[📊 Dataset](https://github.com/BradyFU/MME-RealWorld?tab=readme-ov-file#-dataset)][[🏆 Leaderboard](https://MME-RealWorld.github.io/home_page.html#leaderboard)]  </div></font>



---

## 🔥 News

* **`2024.08.20`** 🌟 We are very proud to launch MME-RealWorld, which contains 13K high-quality images, annotated by more than 30 workers, resulting in 29K question-answer pairs that cover 43 subtasks across five real-world scenarios.


## 👀 MME-RealWorld Overview

Comprehensive evaluation of Multimodal Large Language Models (MLLMs) has recently garnered widespread attention in the research community. However, we observe that existing benchmarks present several common barriers that make it difficult to measure the significant challenges that models face in the real world, including: 1) small data scale leading to large performance variance; 2) reliance on model-based annotations, resulting in significant model bias; 3) restricted data sources, often overlapping with existing benchmarks and posing a risk of data leakage; 4) insufficient task difficulty and discrimination, especially the limited image resolution. To tackle these issues, we introduce <strong>MME-RealWorld</strong>. Initially, we collect more than **300K** images from public datasets and the Internet, filtering **13K** high-quality images for data annotation. With the participation of professional **25** annotators and **7** researchers, we annotate **29K** question-answer pairs that cover **43** subtasks across five real-world scenarios, extremely challenging even for humans. We further conduct a thorough evaluation involving **28** prominent MLLMs, such as GPT-4o, Gemini 1.5 Pro, and Claude 3.5 Sonnet. Our results show that existing models perform poorly in multiple real-world tasks, and there is a significant gap among different models. We hope that MME-RealWorld will further inspire the research community to improve and evolve this field. Our work distinguishes from existing benchmarks through five key features:

* ***Scale, Diversity, and Real-World Utility.*** Our image themes cover $6$ key domains and $14$ sub-class images, offering a highly diverse set of images. Our $43$ sub-class tasks are all closely related to real-world specific tasks, providing high practical value and making it the largest fully human-annotated MLLM benchmark.
    
* ***Quality.*** (1) *Image Resolution.* Many image details contain important information, such as a scoreboard in a sports event. Only with high-resolution images can such critical details be understood, providing the expected assistance to humans. (2) *Annotation.* All annotations are completed manually, with 7 experts cross-checking the results to ensure data quality.

* ***Safety.*** Our data does not overlap with any existing MLLM benchmark, minimizing *the risk of data leakage*. Additionally, our annotations do not rely on any models, thus *avoiding model biases*. With over $30$ annotators, including several with professional knowledge backgrounds, we ensure that our dataset has no significant personal biases.

* ***Difficulty and Distinguishability.*** The dataset's challenges are mainly in the following aspects: (1) *Performance*. Even the most advanced model has not exceeded $55\%$ accuracy in basic perception tasks, with reasoning tasks being even more difficult. (2) *Distinguishability.* There are significant differences between models, with a clear gap between earlier works like LLaVA and more advanced recent models. (3) *Computation*. Due to the high resolution of the selected images, some models exhibit very slow processing speeds, thus our data also poses computational efficiency challenges.
   
* ***MME-RealWorld-CN.*** Existing Chinese benchmark ([liu2023mmbench](https://arxiv.org/pdf/2307.06281)) is usually translated from its English version. This has two problems: 

   (1) *Question-image mismatch.* The image may relate to an English scene, which is not intuitively connected to a Chinese question.

    (2) *Translation mismatch* ([tang2024mtvqa](https://arxiv.org/pdf/2405.11985)), where machine translation is not precise and perfect enough. 

    We collect additional images and ensure that all images focus on Chinese scenarios, asking Chinese workers for annotation. This results in $5,917$ QA pairs.

<p align="center">
    <img src="./asset/MME_RealWorld.png" width="100%" height="100%">
</p>

## 📐 Dataset Examples

<p align="center">
    <img src="./asset/teaser_task.png" width="100%" height="100%">
</p>

<div align='center' >
<details>
<summary> Click to expand more examples</summary>
<p align="center">
    <img src="./asset/monitoring_location.png" width="100%" height="100%">
    <img src="./asset/reasoning_scene.png" width="100%" height="100%">
</details>
</div>


## 🔍 Dataset

**License**:
```
MME-RealWorld is only used for academic research. Commercial use in any form is prohibited.
The copyright of all images belongs to the image owners.
If there is any infringement in MME-RealWorld, please email yifanzhang.cs@gmail.com and we will remove it immediately.
Without prior approval, you cannot distribute, publish, copy, disseminate, or modify MME-RealWorld in whole or in part. 
You must strictly comply with the above restrictions.
```

Please send an email to **yifanzhang.cs@gmail.com**. 🌟


## 🔮 Evaluation Pipeline

📍 **Prompt**:

The common prompt used in our evaluation follows this format:

```
[Image] [Question] The choices are listed below:
(A) [Choice A]
(B) [Choice B]
(C) [Choice C]
(D) [Choice D]
(E) [Choice E]
Select the best answer to the above multiple-choice question based on the image. Respond with only the letter (A, B, C, D, or E) of the correct option. 
The best answer is:
```



📍 **Evaluation**: 

To extract the answer and calculate the scores, we add the model response to a JSON file. Here we provide an example template [output_test_template.json](./evaluation/output_test_template.json). Once you have prepared the model responses in this format, please refer to the evaluation script [eval_your_results.py](./evaluation/eval_your_results.py), and you will get the accuracy scores across categories, subtasks, and task types. 
The evaluation does not introduce any third-party models, such as ChatGPT.

```bash
python eval_your_results.py \
    --results_file $YOUR_RESULTS_FILE \
```
Please ensure that the `results_file` follows the specified JSON format stated above.

📍 **Leaderboard**: 

If you want to add your model to our [leaderboard](https://MME-RealWorld.github.io/home_page.html#leaderboard), please send model responses to **bradyfu24@gmail.com**, as the format of [output_test_template.json](./evaluation/output_test_template.json).


## 📈 Experimental Results
- **Evaluation results of different MLLMs on the perception tasks.**

<p align="center">
    <img src="./asset/results_perception.png" width="96%" height="50%">
</p>


- **Evaluation results of different MLLMs on the reasoning tasks.**

<p align="center">
    <img src="./asset/results_reasoning.png" width="96%" height="50%">
</p>

- **Evaluation results of different MLLMs on the perception tasks of MME-RealWorld-CN.**

<p align="center">
    <img src="./asset/results_perception_cn.png" width="96%" height="50%">
</p>

- **Evaluation results of different MLLMs on the reasoning tasks of MME-RealWorld-CN.**

<p align="center">
    <img src="./asset/results_reasoning_cn.png" width="96%" height="50%">
</p>


## :black_nib: Citation

If you find our work helpful for your research, please consider citing our work.   

```bibtex
@article{fu2024video,
  title={MME-RealWorld: The First-Ever Comprehensive Evaluation Benchmark of Multi-modal LLMs in Video Analysis},
  author={Fu, Chaoyou and Dai, Yuhan and Luo, Yondong and Li, Lei and Ren, Shuhuai and Zhang, Renrui and Wang, Zihan and Zhou, Chenyu and Shen, Yunhang and Zhang, Mengdan and others},
  journal={arXiv preprint arXiv:2405.21075},
  year={2024}
}
```

## 📜 Related Works

Explore our related researches:
-  **[MME]** [MME: A Comprehensive Evaluation Benchmark for Multimodal Large Language Models](https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models/tree/Evaluation)
-  **[Awesome-MLLM]** [A Survey on Multimodal Large Language Models](https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models)

