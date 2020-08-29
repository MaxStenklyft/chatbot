import json
import urllib.parse
import boto3
import random

print('Loading function')

s3 = boto3.resource('s3')

def clean_text(text):
    currently_good = True
    clean_text = ''
    for letter in text.replace("\n", "").replace("<APPLAUSE>", " *APPLAUSE*").replace('"','').replace(':','').lower():
        if letter == '<':
            currently_good = False
        elif letter == '>':
            currently_good = True
        # treating each of these characters as their own word by putting a space before them
        elif currently_good and letter in {'?', '.', '!', ',', '--'}:
            clean_text += (" " + letter)
        elif currently_good:
            clean_text += letter
    return clean_text

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
    # print(likely_next_words)
    # print(more_likely_next_words)
    return likely_next_words, more_likely_next_words

def get_speeches(speaker):
    my_bucket = s3.Bucket('user-transcripts')
    files = list(my_bucket.objects.filter(Prefix=speaker))
    body = ''
    #Rathern than read in all speeches, I arbitrarily selected a subset for performance reasons
    for file in files[5:25]:
        retrieved_file = file.get()
        body += retrieved_file['Body'].read().decode('utf-8')
    return body

def assess_next_words(possible_next_words, probable_next_words, trump_factor):
    likely_next_words = {}
    total_probability = 0
    for word in possible_next_words:
        increased_probability = int(pow(possible_next_words[word] + (probable_next_words.get(word) or 0), trump_factor))
        likely_next_words[word] = increased_probability
        total_probability += increased_probability
    return likely_next_words, total_probability


def lambda_handler(event, context):
    body = get_speeches(event['speaker'])
    trump_factor = event['trump_factor']
    words = clean_text(body).replace("  ", " ").split(" ")
    current_word = words[int(random.random() * len(words))]
    previous_word = ''
    sentance = current_word

    while current_word not in {'.', '!', '?','*APPLAUSE*'}:
        possible_next_words, probable_next_words = get_likely_next_words(previous_word,current_word, words)
        likely_next_words, total_probability = assess_next_words(possible_next_words, probable_next_words, trump_factor)
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
            #print("patience/total_probability," + str(patience/total_probability) + "\n tolerance:" + str(tolerance))
    return sentance
