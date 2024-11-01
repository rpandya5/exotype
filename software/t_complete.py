import requests
from collections import defaultdict, Counter
import re
import os

class TextPredictor:
    def __init__(self):
        self.word_freq = Counter()
        self.bigram_freq = defaultdict(Counter)
        self.trigram_freq = defaultdict(lambda: defaultdict(Counter))
        self.common_words = set()
        self.common_phrases = []
        self.valid_words = set()
        self.is_trained = False

    def load_common_words(self):
        common_words = """the and to a of in is it you that he was for on are with as I his they be at one have this from or had by hot but some what there we can out other were all your when up use word how said an each she which do their time if will way about many then them would write like so these her long make thing see him two has look more day could go come did my sound no most number who over know water than call first people may down side been now find any new work part take get place made live where after back little only round man year came show every good me give our under name very through just form much great think say help low line before turn cause same mean differ move right boy old too does tell sentence set three want air well also play small end put home read hand port large spell add even land here must big high such follow act why ask men change went light kind off need house picture try us again animal point mother world near build self earth father head stand own page should country found answer school grow study still learn plant cover food sun four thought let keep eye never last door between city tree cross since hard start might story saw far sea draw left late run don't while press close night real life few stop"""
        self.common_words = set(common_words.split())
        self.common_phrases = ["can you", "do you", "how are", "what is", "where is", "when is", "why is", "who is", "is it", "are you", "will you", "could you", "would you", "should I", "can I", "may I", "I am", "you are", "he is", "she is", "they are", "we are", "it is"]

    def train_model(self):
        if self.is_trained:
            return
        if not os.path.exists('big.txt'):
            big_txt_url = "http://norvig.com/big.txt"
            response = requests.get(big_txt_url)
            with open('big.txt', 'w', encoding='utf-8') as f:
                f.write(response.text)

        with open('big.txt', 'r', encoding='utf-8') as f:
            text = f.read().lower()

        words = re.findall(r'\w+', text)
        self.word_freq.update(words)

        for w1, w2, w3 in zip(words, words[1:], words[2:]):
            self.bigram_freq[w1][w2] += 1
            self.trigram_freq[w1][w2][w3] += 1

        self.valid_words = set(word for word, freq in self.word_freq.items() if freq > 1)
        self.is_trained = True
        print("Model trained successfully.")

    def predict(self, context, num_predictions=4):
        words = context.lower().split()
        if not words:
            return [context + word for word in self.common_words][:num_predictions]

        current_word = words[-1]
        prev_word = words[-2] if len(words) > 1 else ""
        prev_prev_word = words[-3] if len(words) > 2 else ""

        for phrase in self.common_phrases:
            if context.lower().endswith(phrase[:len(context)]) and phrase != context.lower():
                return [context + phrase[len(context):]]

        if prev_prev_word and prev_word:
            predictions = self.trigram_freq[prev_prev_word][prev_word].most_common(num_predictions * 4)
        elif prev_word:
            predictions = self.bigram_freq[prev_word].most_common(num_predictions * 4)
        else:
            predictions = self.word_freq.most_common(num_predictions * 4)

        filtered_predictions = []
        for word, _ in predictions:
            if word.startswith(current_word) and word != current_word:
                if word in self.valid_words:
                    filtered_predictions.append(context[:-len(current_word)] + word)
            if len(filtered_predictions) == num_predictions:
                break

        if len(filtered_predictions) < num_predictions:
            for word in self.common_words:
                if word.startswith(current_word) and word != current_word:
                    prediction = context[:-len(current_word)] + word
                    if prediction not in filtered_predictions:
                        filtered_predictions.append(prediction)
                    if len(filtered_predictions) == num_predictions:
                        break

        if len(filtered_predictions) < num_predictions:
            completions = [w for w in self.valid_words if w.startswith(current_word) and w != current_word]
            for completion in completions:
                prediction = context[:-len(current_word)] + completion
                if prediction not in filtered_predictions:
                    filtered_predictions.append(prediction)
                if len(filtered_predictions) == num_predictions:
                    break

        boosted_predictions = []
        for pred in filtered_predictions:
            if pred.split()[-1] in self.common_words:
                boosted_predictions.insert(0, pred)
            else:
                boosted_predictions.append(pred)

        return boosted_predictions[:num_predictions] if boosted_predictions else [context] * num_predictions