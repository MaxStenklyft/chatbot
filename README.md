This is a probability based chatbot lambda. It reads in speeches from an S3 bucket, selects a random start word, and uses the occurrences of proceeding word(s) from the speeches to tack on another word until hitting the end of sentence.

The probability of each proceeding word is proportional to the number of occurrences in the speeches. The probability of the next word is also increased proportional to the number of times the two proceeding words lead to that word. I also added what I call a "trump" factor, to allow exponentially increase of word probability based on the two aforementioned factors.

Strict probability can only get this chatbot so far, so while I would love to tinker with this iteration more and polish it, any future enhancements will likely come in the form of a larger rework to introduce a neural network.

Credits: The speeches I initially used were collected from http://www.thegrammarlab.com/?nor-portfolio=corpus-of-presidential-speeches-cops-and-a-clintontrump-corpus
This program is very closely based off of an assignment I completed at the University of Wisconsin Madison, in a Introduction to AI class, instructed by Jerry Zhu (http://pages.cs.wisc.edu/~jerryzhu/)
