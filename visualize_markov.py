import matplotlib.pyplot as plt
import networkx as nx
import random
import ast
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MarkovChainVisualizer:
    def __init__(self, master):
        self.master = master
        master.title("Markov Chain Visualizer")
        master.geometry("1200x800")
        
        # Create frames
        self.control_frame = ttk.Frame(master, padding="10")
        self.control_frame.pack(fill=tk.X, side=tk.TOP)
        
        self.graph_frame = ttk.Frame(master)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add controls
        ttk.Label(self.control_frame, text="Start Word:").grid(row=0, column=0, padx=5, pady=5)
        self.start_word_var = tk.StringVar()
        self.start_word_entry = ttk.Combobox(self.control_frame, textvariable=self.start_word_var)
        self.start_word_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.control_frame, text="Depth:").grid(row=0, column=2, padx=5, pady=5)
        self.depth_var = tk.IntVar(value=2)
        self.depth_spinbox = ttk.Spinbox(self.control_frame, from_=1, to=5, textvariable=self.depth_var, width=5)
        self.depth_spinbox.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(self.control_frame, text="Max Branches:").grid(row=0, column=4, padx=5, pady=5)
        self.max_branches_var = tk.IntVar(value=3)
        self.max_branches_spinbox = ttk.Spinbox(self.control_frame, from_=1, to=10, textvariable=self.max_branches_var, width=5)
        self.max_branches_spinbox.grid(row=0, column=5, padx=5, pady=5)
        
        self.visualize_button = ttk.Button(self.control_frame, text="Visualize", command=self.visualize_chain)
        self.visualize_button.grid(row=0, column=6, padx=5, pady=5)
        
        self.generate_button = ttk.Button(self.control_frame, text="Generate Text", command=self.generate_text)
        self.generate_button.grid(row=0, column=7, padx=5, pady=5)
        
        # Text output area
        self.output_frame = ttk.LabelFrame(self.master, text="Generated Text", padding="10")
        self.output_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, height=4)
        self.output_text.pack(fill=tk.X, expand=True)
        
        # Load transitions
        self.transitions = self.load_transitions("word_transitions.txt")
        
        # Set up initial matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Populate start words dropdown
        self.start_word_entry['values'] = sorted(list(self.transitions.keys())[:200])  # Limit to first 200 for performance
        if len(self.transitions) > 0:
            self.start_word_var.set(random.choice(list(self.transitions.keys())))
    
    def load_transitions(self, file_path):
        transitions = {}
        encodings = ["utf-8", "latin-1", "cp1252"]
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    for line in f:
                        if ":" in line:
                            word, next_words_str = line.strip().split(":", 1)
                            try:
                                next_words = ast.literal_eval(next_words_str.strip())
                                transitions[word] = next_words
                            except (SyntaxError, ValueError):
                                # Skip malformed lines
                                continue
                print(f"Successfully loaded transitions using {encoding} encoding")
                return transitions
            except UnicodeDecodeError:
                print(f"Failed to decode with {encoding}, trying next encoding...")
                continue
            except FileNotFoundError:
                print(f"Error: File {file_path} not found")
                return {}
        
        print("Failed to load transitions with any encoding")
        return {}
    
    def visualize_chain(self):
        start_word = self.start_word_var.get()
        depth = self.depth_var.get()
        max_branches = self.max_branches_var.get()
        
        if not start_word or start_word not in self.transitions:
            start_word = random.choice(list(self.transitions.keys()))
            self.start_word_var.set(start_word)
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges through BFS
        queue = [(start_word, 0)]
        visited = set([start_word])
        G.add_node(start_word)
        
        while queue:
            current_word, current_depth = queue.pop(0)
            
            if current_depth >= depth:
                continue
            
            if current_word in self.transitions:
                # Get top N next words by frequency
                next_words = sorted(self.transitions[current_word].items(), 
                                   key=lambda x: x[1], reverse=True)[:max_branches]
                
                total = sum(count for _, count in next_words)
                
                for next_word, count in next_words:
                    probability = count / total if total > 0 else 0
                    G.add_node(next_word)
                    G.add_edge(current_word, next_word, weight=count, 
                              label=f"{probability:.2f}")
                    
                    if next_word not in visited:
                        visited.add(next_word)
                        queue.append((next_word, current_depth + 1))
        
        # Clear the current figure
        self.ax.clear()
        
        # Set up layout
        pos = nx.spring_layout(G, k=0.3, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', 
                              node_size=1500, alpha=0.8, ax=self.ax)
        
        # Highlight starting word
        nx.draw_networkx_nodes(G, pos, nodelist=[start_word], 
                              node_color='red', node_size=1800, ax=self.ax)
        
        # Draw edges with varying width based on weight
        edges = G.edges(data=True)
        weights = [data['weight'] for _, _, data in edges]
        max_weight = max(weights) if weights else 1
        
        nx.draw_networkx_edges(G, pos, width=[1 + (w/max_weight) * 5 for w in weights], 
                              edge_color='gray', alpha=0.7, 
                              connectionstyle='arc3,rad=0.1', ax=self.ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=self.ax)
        
        # Draw edge labels (probabilities)
        edge_labels = {(u, v): data['label'] for u, v, data in G.edges(data=True)}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, 
                                    font_size=8, ax=self.ax)
        
        # Set up plot
        self.ax.set_title(f"Markov Chain from '{start_word}' (Depth: {depth}, Max Branches: {max_branches})")
        self.ax.axis('off')
        
        # Draw the plot
        self.canvas.draw()
    
    def generate_text(self):
        start_word = self.start_word_var.get()
        
        if not start_word or start_word not in self.transitions:
            start_word = random.choice(list(self.transitions.keys()))
            self.start_word_var.set(start_word)
        
        # Generate text using weighted random selection
        word = start_word
        sentence = [word]
        
        for _ in range(25):  # Generate 25 words
            if word not in self.transitions:
                break
                
            next_words = self.transitions[word]
            if not next_words:
                break
                
            # Choose next word based on weights
            words = list(next_words.keys())
            weights = list(next_words.values())
            
            word = random.choices(words, weights=weights, k=1)[0]
            sentence.append(word)
        
        # Clear output text and display new sentence
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', " ".join(sentence))

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkovChainVisualizer(root)
    root.mainloop()
