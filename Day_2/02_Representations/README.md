# Introduction
**Author/contact:** Jonathan Funk ([jonfu@dtu.dk](mailto:jonfu@dtu.dk))

These exercises provide an introduction to protein representations and representation learning through latent variable models (LVMs). Latent variable models are a great way to teach foundational principles of modern machine learning algorithms, and generative models.

We are going to cover:

- **Simple representations**:
    a. Revision of OHE and introduction of **BLOSUM** encodings and **biochemical** encodings.  
    b. Introduction to **latent variable models**.

### What You'll Learn

1. **Simple representations**  
   - What are protein representations, and why do they matter?  
   - What are inductive biases?  
   - What should be paid attention to when constructing representations?  

2. **Latent variable models and representation learning**  
   - What is representation learning?  
   - How does it differ from simple protein representations?  
   - How to train an LVM—specifically, a Variational Autoencoder.  
   - Controlling inductive biases in LVM training and architecture.  

### How We'll Proceed

We will begin by revisiting the exercises from day one using new tools. We will explore representation learning 
methods and study their effects on model performance.  
Next, we will train latent variable models and examine the resulting representations and their influence on model performance.  
Finally, we will connect these representations to standard **scikit-learn** and **PyTorch** workflows.

The key teaching goal is to make students reason about inductive bias. For each representation, students should be able to explain what biological similarity it makes visible to a model and what information it may hide.