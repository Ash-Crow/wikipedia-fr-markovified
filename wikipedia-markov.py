#!/usr/bin/env python
# -*- coding: utf-8 -*-

import markovify

user = "Jean-Jacques_Georges"
user = "TomT0m"
#user = "Simon_Villeneuve"
user = "Starus"
user = "TigH"

# Get raw text as string.
with open("users/{}.txt".format(user)) as f:
    text = f.read()

state = 2

# Build the model.
text_model = markovify.Text(text, state_size=state)

# Print five randomly-generated sentences
for i in range(5):
    print(text_model.make_sentence())

print("==========")
# Print three randomly-generated sentences of no more than 140 characters
for i in range(3):
    print(text_model.make_short_sentence(140))

f.close()
