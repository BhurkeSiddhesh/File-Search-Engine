"""
Test Model Comparison and Ranking

Tests that compare outputs from multiple downloaded models
and can rank them based on response quality.
"""

import unittest
import os
import time
from typing import List, Dict, Tuple


class TestModelComparison(unittest.TestCase):
    """Tests for comparing and ranking multiple LLM models."""
    
    @classmethod
    def setUpClass(cls):
        """Set up models for testing - runs once before all tests."""
        cls.models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        cls.available_models = []
        
        # Find all downloaded .gguf models
        if os.path.exists(cls.models_dir):
            for f in os.listdir(cls.models_dir):
                if f.endswith('.gguf'):
                    cls.available_models.append(os.path.join(cls.models_dir, f))
        
        print(f"\nFound {len(cls.available_models)} models for testing")
        
        # Test questions for comparison
        cls.test_questions = [
            {
                "question": "What is 2 + 2?",
                "expected_keywords": ["4", "four"],
                "context": "Basic arithmetic: 2 plus 2 equals 4."
            },
            {
                "question": "What color is the sky?",
                "expected_keywords": ["blue", "azure"],
                "context": "The sky appears blue during the day due to light scattering."
            },
            {
                "question": "What is the capital of France?",
                "expected_keywords": ["paris"],
                "context": "France is a country in Europe. Its capital city is Paris."
            }
        ]
    
    def test_models_available(self):
        """Test that at least one model is available for testing."""
        self.assertGreater(
            len(self.available_models), 0,
            "No models found. Download at least one model to run comparison tests."
        )
    
    def test_model_loading(self):
        """Test that all available models can be loaded."""
        if not self.available_models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        for model_path in self.available_models[:2]:  # Test first 2 models to save time
            model_name = os.path.basename(model_path)
            with self.subTest(model=model_name):
                try:
                    llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
                    self.assertIsNotNone(llm)
                    del llm  # Free memory
                except Exception as e:
                    self.fail(f"Failed to load model {model_name}: {e}")
    
    def test_single_model_generation(self):
        """Test that a single model can generate text."""
        if not self.available_models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        model_path = self.available_models[0]
        model_name = os.path.basename(model_path)
        
        try:
            llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
            output = llm("Hello, how are you?", max_tokens=20)
            
            self.assertIn('choices', output)
            self.assertGreater(len(output['choices']), 0)
            self.assertIn('text', output['choices'][0])
            
            generated_text = output['choices'][0]['text']
            self.assertIsInstance(generated_text, str)
            self.assertGreater(len(generated_text.strip()), 0)
            
            del llm
            print(f"\n{model_name} generated: {generated_text[:50]}...")
            
        except Exception as e:
            self.fail(f"Generation failed with {model_name}: {e}")
    
    def test_compare_multiple_models(self):
        """Test comparing outputs from multiple models on the same question."""
        if len(self.available_models) < 2:
            self.skipTest("Need at least 2 models for comparison")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        question = self.test_questions[0]
        prompt = f"Context: {question['context']}\n\nQuestion: {question['question']}\n\nAnswer:"
        results = []
        
        for model_path in self.available_models[:2]:
            model_name = os.path.basename(model_path)
            try:
                llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
                
                start_time = time.time()
                output = llm(prompt, max_tokens=50)
                latency = time.time() - start_time
                
                generated_text = output['choices'][0]['text'].strip()
                token_count = output.get('usage', {}).get('completion_tokens', 0)
                
                results.append({
                    'model': model_name,
                    'answer': generated_text,
                    'latency': latency,
                    'tokens': token_count
                })
                
                del llm
                
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                continue
        
        self.assertGreater(len(results), 0, "No models produced output")
        
        # Print comparison results
        print("\n=== Model Comparison Results ===")
        for r in results:
            print(f"\nModel: {r['model']}")
            print(f"Answer: {r['answer'][:100]}...")
            print(f"Latency: {r['latency']:.2f}s")
    
    def test_rank_models_by_accuracy(self):
        """Test ranking models by answer accuracy (keyword matching)."""
        if len(self.available_models) < 2:
            self.skipTest("Need at least 2 models for ranking")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        question = self.test_questions[0]
        prompt = f"Context: {question['context']}\n\nQuestion: {question['question']}\n\nAnswer:"
        scores = []
        
        for model_path in self.available_models[:2]:
            model_name = os.path.basename(model_path)
            try:
                llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
                output = llm(prompt, max_tokens=50)
                generated_text = output['choices'][0]['text'].strip().lower()
                
                # Score based on expected keywords
                score = sum(1 for kw in question['expected_keywords'] if kw.lower() in generated_text)
                
                scores.append({
                    'model': model_name,
                    'answer': generated_text,
                    'score': score
                })
                
                del llm
                
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                continue
        
        # Sort by score (descending)
        ranked = sorted(scores, key=lambda x: x['score'], reverse=True)
        
        print("\n=== Model Ranking by Accuracy ===")
        for i, r in enumerate(ranked, 1):
            print(f"{i}. {r['model']} (score: {r['score']})")
            print(f"   Answer: {r['answer'][:80]}...")
        
        self.assertGreater(len(ranked), 0, "No models were ranked")
    
    def test_rank_models_by_speed(self):
        """Test ranking models by response latency."""
        if len(self.available_models) < 2:
            self.skipTest("Need at least 2 models for ranking")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        prompt = "Hello, describe yourself in one sentence."
        latencies = []
        
        for model_path in self.available_models[:2]:
            model_name = os.path.basename(model_path)
            try:
                llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
                
                start_time = time.time()
                output = llm(prompt, max_tokens=30)
                latency = time.time() - start_time
                
                latencies.append({
                    'model': model_name,
                    'latency': latency,
                    'answer': output['choices'][0]['text'].strip()[:50]
                })
                
                del llm
                
            except Exception as e:
                print(f"Error with {model_name}: {e}")
                continue
        
        # Sort by latency (ascending - faster is better)
        ranked = sorted(latencies, key=lambda x: x['latency'])
        
        print("\n=== Model Ranking by Speed ===")
        for i, r in enumerate(ranked, 1):
            print(f"{i}. {r['model']} ({r['latency']:.2f}s)")
        
        self.assertGreater(len(ranked), 0, "No models were ranked")


class TestModelQuality(unittest.TestCase):
    """Tests for model output quality assessment."""
    
    def test_response_coherence(self):
        """Test that model responses are coherent (not gibberish)."""
        models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        if not os.path.exists(models_dir):
            self.skipTest("Models directory not found")
        
        models = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith('.gguf')]
        
        if not models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        model_path = models[0]
        llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
        
        prompt = "The weather today is"
        output = llm(prompt, max_tokens=20)
        response = output['choices'][0]['text'].strip()
        
        # Check for basic coherence
        self.assertGreater(len(response), 3, "Response too short")
        
        # Check that response contains actual words
        words = response.split()
        valid_words = [w for w in words if len(w) > 1 and w.isalpha()]
        self.assertGreater(len(valid_words), 0, "Response contains no valid words")
        
        del llm
    
    def test_response_length_control(self):
        """Test that max_tokens parameter is respected."""
        models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        
        if not os.path.exists(models_dir):
            self.skipTest("Models directory not found")
        
        models = [os.path.join(models_dir, f) for f in os.listdir(models_dir) if f.endswith('.gguf')]
        
        if not models:
            self.skipTest("No models available")
        
        try:
            from llama_cpp import Llama
        except ImportError:
            self.skipTest("llama_cpp not installed")
        
        model_path = models[0]
        llm = Llama(model_path=model_path, n_ctx=512, verbose=False)
        
        prompt = "Tell me a very long story about:"
        output = llm(prompt, max_tokens=10)
        
        tokens_used = output.get('usage', {}).get('completion_tokens', 0)
        
        # Allow some tolerance
        self.assertLessEqual(tokens_used, 15, "Max tokens not respected")
        
        del llm


if __name__ == '__main__':
    unittest.main(verbosity=2)
