import json
import urllib.parse
import boto3
import random

print('Loading function')

s3 = boto3.resource('s3')

trump_factor = 5

def clean_text(text):
    currently_good = True
    clean_text = ''
    for letter in text.replace("\n", "").replace("<APPLAUSE>", " *APPLAUSE*").replace('"','').replace(':','').lower():
        if letter == '<':
            currently_good = False
        elif letter == '>':
            currently_good = True
        elif currently_good and letter in {'?', '.', '!', ',', '--'}:
            clean_text += (" " + letter)
        elif currently_good:
            clean_text += letter
    return clean_text

def get_dictionary(text):
    dictionary = {}
    starting_words = {}
    #print(words)
    for i,word in enumerate(text):
        currentCount = dictionary.get(word)
        dictionary[word] = (currentCount or 0) + 1
        if i != 0 and text[i] == '.':
            starting_words = (starting_words.get(word) or 0) + 1
    return dictionary, starting_words

def get_likely_next_words(previous_word, current_word, transcript):
    likely_next_words = {}
    more_likely_next_words = {}
    for i,word in enumerate(transcript):
        if word == current_word and i + 1< len(transcript):
            next_word = transcript[i+1]
            currentCount = likely_next_words.get(next_word)
            likely_next_words[next_word] = (currentCount or 0) + 1
            if i > 0 and transcript[i - 1] == previous_word:
                more_likely_next_words[next_word] = (currentCount or 0) + 1
    print(likely_next_words)
    print(more_likely_next_words)
    return likely_next_words, more_likely_next_words

def get_speeches(speaker):
    my_bucket = s3.Bucket('user-transcripts')
    files = list(my_bucket.objects.filter(Prefix=speaker))
    body = ''
    for file in files[5:25]:
        retrieved_file = file.get()
        body += retrieved_file['Body'].read().decode('utf-8')
    return body

def prune_word_choice(possible_next_words, probable_next_words):
    likely_next_words = {}
    total_probability = 0
    for word in possible_next_words:
        increased_probability = int(pow(possible_next_words[word] + (probable_next_words.get(word) or 0), trump_factor))
        likely_next_words[word] = increased_probability
        total_probability += increased_probability
    return likely_next_words, total_probability



def lambda_handler(event, context):
    body = get_speeches(event['speaker'])
    words = clean_text(body).replace("  ", " ").split(" ")
    #print(words)
    #word_count = get_dictionary(words)
    # print(len(word_count))
    current_word = words[int(random.random() * len(words))]
    previous_word = ''
    sentance = current_word

    while current_word not in {'.', '!', '?','*APPLAUSE*'}:
        possible_next_words, probable_next_words = get_likely_next_words(previous_word,current_word, words)
        likely_next_words, total_probability = prune_word_choice(possible_next_words, probable_next_words)
        if len(likely_next_words) == 0:
            print("dead end")
            break
        #print(likely_next_words)
        patience = 0.0
        tolerance = random.random()
        for word in likely_next_words:
            if patience/total_probability > tolerance or len(likely_next_words) == 1:
                sentance += " " + word
                previous_word = current_word
                current_word = word
                break
            patience += likely_next_words[word]
            print("patience/total_probability," + str(patience/total_probability) + "\n tolerance:" + str(tolerance))
    return sentance
