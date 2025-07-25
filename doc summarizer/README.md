# Legal Document Analyzer 📚⚖️

## Project Overview
This Legal Document Analyzer is an NLP project demonstrating the application of transformer models for legal document summarization. The project implements two approaches: (1) a fine-tuned BART-based model and (2) a proof-of-concept custom transformer architecture.

## 🤗 Hugging Face Hosted Model

The fine-tuned model is available on Hugging Face: [sanatann/legal-summarizer-bart](https://huggingface.co/sanatann/legal-summarizer-bart)

---

## 🚀 Demo

You can directly use the fine-tuned model with the following code:

```python
from transformers import pipeline

summarizer = pipeline("summarization", model="sanatann/legal-summarizer-bart")

text = "Your long legal document here..."

summary = summarizer(text)

print(summary)
```

## 🗂️ Dataset
The project uses a comprehensive legal document dataset from Zenodo (https://zenodo.org/records/7152317), containing:

- Indian Legal Abstracts (IN-Abs)
- Indian Legal Extendeds (IN-Ext)
- UK Legal Abstracts (UK-Abs)

## Implementation Approaches

### 1. Fine-tuned Model Approach (Primary Implementation)

The primary implementation uses a fine-tuned model based on the BART architecture:

- **Base Model**: facebook/bart-large-cnn
- **Fine-tuning Process**: The model was fine-tuned on the legal documents dataset using Hugging Face's Transformers library
- **Training Infrastructure**: A100 GPU
- **Training Parameters**: 
  - 4 epochs
  - Learning rate: 2e-5
  - Batch size: 16
  - Gradient accumulation steps: 2

This approach yielded better results than the from-scratch implementation due to:
- Leveraging pre-trained language knowledge
- Computational efficiency through transfer learning
- Better handling of legal terminology and complex sentence structures

The fine-tuned model was further enhanced with a PPO-based reinforcement learning approach to optimize for ROUGE and BLEU scores.

### 2. Custom Transformer Architecture (Proof of Concept)

The custom transformer implementation provided a valuable learning experience and exploration of the architecture:

- **Architecture Components**:
  - Multi-Head Attention mechanism
  - Positional Encoding
  - Encoder-Decoder structure
  - Layer Normalization
  - Feed-Forward Networks

- **Tokenization**:
  - Byte Pair Encoding (BPE)
  - Vocabulary size of 50,000 tokens

While theoretically sound, this approach faced significant challenges:
- Limited by computational resources despite using A100 GPUs
- Insufficient training data for a from-scratch transformer
- Legal text complexity requiring deeper contextual understanding

## Why Fine-tuning Was Preferred

Despite having access to A100 GPUs, we opted for the fine-tuned approach because:

1. **Computational Efficiency**: Training transformers from scratch requires enormous computational resources and time, even with high-end GPUs
2. **Data Constraints**: Legal documents are specialized and not as abundant as general text corpora
3. **Transfer Learning Benefits**: Pre-trained models already understand language structure, allowing us to focus on domain adaptation
4. **Performance**: Fine-tuned models demonstrate significantly better performance on specialized tasks with limited datasets

## Project Achievements

The project successfully delivered:

1. A working legal document summarizer based on fine-tuned BART
2. A proof-of-concept custom transformer implementation
3. An RL-enhanced model using PPO to optimize summary quality
4. A complete legal text preprocessing pipeline
5. Integration with Hugging Face for easy model access

## Performance and Limitations

- The fine-tuned model achieves competitive performance on legal summarization tasks
- The model performs best on texts similar to its training data (Indian and UK legal documents)
- Custom transformer implementation demonstrated the challenges in training large language models from scratch
- Current limitation: Processing extremely long legal documents requires chunking strategies


## Technical Requirements

### Dependencies

- PyTorch
- Transformers
- Tokenizers
- NLTK
- RougeScore
- SacreBLEU
- Stable-Baselines3 (for RL optimization)

## Conclusion

This project demonstrates both the practical approach (fine-tuning) and theoretical exploration (custom implementation) of transformer models for legal document analysis. While the fine-tuned approach proved more effective given resource constraints, the custom implementation provided valuable insights into transformer architecture and the challenges of training language models from scratch.
