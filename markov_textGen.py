import re
from nltk.tokenize import word_tokenize
import random


def process_text(file_path):
    txt=[]
    with open(file_path, "r",encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line!='':txt.append(line)
    return txt

text_data = process_text("train.txt")
print("number of lines = ", len(text_data))

def clean_txt(txt):
    cleaned_txt = []
    for line in txt:
        line = line.lower()
        line = re.sub(r"[,.\"\'!@#$%^&*(){}?/;`~:<>+=-\\]", "", line)
        tokens = word_tokenize(line)
        words = [word for word in tokens if word.isalpha()]
        cleaned_txt+=words
    return cleaned_txt

cleaned_text_data = clean_txt(text_data)
# print(cleaned_text_data[:10])
print("number of words = ", len(cleaned_text_data))

def build_markov_chain(words, order=3):
    markov_model = {}
    for i in range(len(words) - 2*order + 1):
        curr_state, next_state = "", ""
        for j in range(order):
            curr_state += words[i+j] + " "
            next_state += words[i+j+order] + " "
        curr_state = curr_state[:-1]
        next_state = next_state[:-1]
        if curr_state not in markov_model:
            markov_model[curr_state] = {}
            markov_model[curr_state][next_state] = 1
        else:
            if next_state in markov_model[curr_state]:
                markov_model[curr_state][next_state] += 1
            else:
                markov_model[curr_state][next_state] = 1
    
    # calculating transition probabilities
    for curr_state, transition in markov_model.items():
        total = sum(transition.values())
        for state, count in transition.items():
            markov_model[curr_state][state] = count/total
        
    return markov_model


def generate_story(markov_model, limit=100, start='my god'):
    n = 0
    curr_state = start
    next_state = None
    story = ""
    story+=curr_state+" "
    while n<limit:
        next_state = random.choices(list(markov_model[curr_state].keys()),
                                    list(markov_model[curr_state].values()))
        
        curr_state = next_state[0]
        story+=curr_state+" "
        n+=1
    return story


n_gram=input("Enter the n-gram order (default is 3, max 5): ") or 3

markov_model = build_markov_chain(cleaned_text_data, order=int(n_gram))

print("number of states in the Markov model = ", len(markov_model))

if n_gram == '1':
    default_start_word = "the"
elif n_gram == '2':
    default_start_word = "the murder"
elif n_gram == '3':
    default_start_word = "the murder of"
elif n_gram == '4':
    default_start_word = "the murder of roger"
elif n_gram == '5':
    default_start_word = "the murder of roger ackroyd"

start_word = input(f"Enter a start word (default is '{default_start_word}'): ") or default_start_word

# print(markov_model["roger ackroyd"])
print(generate_story(markov_model, limit=20,start=start_word))