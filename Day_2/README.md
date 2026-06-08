# ML4Proteins
**Author/contact:** Jonathan Funk ([jonfu@dtu.dk](mailto:jonfu@dtu.dk))

Welcome to **ML4Proteins**! Here you will learn about the concepts and methods of machine learning for protein engineering using open Python tools such as scikit-learn and PyTorch.
The course is primarily aimed to newcomers to the field and mostly geared to biotechnology, and bioinformatic students who had some contact with machine learning and Python before.
If you are new to both machine learning and Python, then this course might be challenging at times.
The course material is closely linked to our research and will bring introduce you to bleeding edge research questions we are thinking about on a daily basis. This is our first course 
on the subject matter and we hope to make the course as useful as possible. We want the course to be as useful as possible, so please let us know if we can make improvements!

The exercises are designed in conjunction with the university course [27666 AI-guided Protein Science: From Design to Engineering](https://kurser.dtu.dk/course/2024-2025/27666?menulanguage=en)
of the Technical University of Denmark (DTU), but can also be taken without the course material. Some course material will be made available online (links will be shared).

## Getting Started
To get started with the course material, create a Python environment and install the course dependencies.

```bash
python -m pip install -r requirements.txt
```
Verify that the environment installed successfully by opening Python and importing the main packages.

```python
import sklearn
import torch

print(sklearn.__version__)
print(torch.__version__)
```
This should print the installed package versions.

## Next Steps
Once your environment is set up and ready, you can proceed to the course content.

## How to Work Through the Exercises

These exercises are designed for active discussion, not only code completion. A productive rhythm is:

1. Predict what you expect before running a model or visualization.
2. Run the code and compare the output with your prediction.
3. Explain the result to a neighbor in plain language.
4. Write down one misconception, surprise, or limitation before moving on.

The notebooks include checkpoints for pair discussion, interpretation, and model-diagnosis questions. Use those prompts even when the code already runs.

Happy Learning!
