#!/usr/bin/env python
# -*- coding: utf-8 -*-

import markovify
import sys

if len(sys.argv) > 1:
    user = sys.argv[1]
else:
    user = "Ash_Crow"


# Get raw text as string.
with open("users/{}.txt".format(user)) as f:
    text = f.read()

state = 2

# Build the model.
text_model = markovify.Text(text, state_size=state)

# Print five randomly-generated sentences
for i in range(5):
    print(text_model.make_sentence(tries=42))

print("==========")
# Print three randomly-generated sentences of no more than 140 characters
#for i in range(3):
#    print(text_model.make_short_sentence(140))

f.close()
