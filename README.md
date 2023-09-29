# spoonfed

This is a Python application that interfaces with [Anki](https://apps.ankiweb.net/) to fill what I feel is a resource gap in my language-learning workflow. It is inspired by the Anki deck [Spoonfed Chinese](https://promagma.gumroad.com/l/IEmpwF), which I used daily for a few years while studying Mandarin. 

## The Problem
Here's the workflow I like to follow when learning a language:
1. Start with a Pimsleur course to get the sound of the language into my head and learn some basic phrases;
2. Learn the writing system so I can start reading ASAP;
3. Spend a few months reading beginner-friendly content to gradually build my vocabulary;
4. Find some conversation partners, listen to podcasts, etc.
5. Graduate to reading native speaker content when it starts feeling enjoyable to do so.

I find there's a gap in resources available for phase 3: it is hard to find beginner-friendly text that is not so easy I find it boring, and not so hard I find it frustrating. Also, beginner resources are too often surrounded by English context or instruction, which I find detracts from the quality of the resource. 

## The Solution
Ideally, during phase 3 I would like to have access to text (with native speaker audio) that strictly follows the [i+1 rule](https://en.wikipedia.org/wiki/Input_hypothesis): that is, each time I go to read a new sentence, it includes exactly one word I haven't seen before. This ensures I can understand the bulk of the sentence, while still being surprised and stimulated by a comfortable amount of novelty. 

This application tries to fill that gap by using generative AI to do the following:
1. Load all the words from sentences I have learned to date in a particular langauge from my Anki account;
2. Load all the words from sentences I have _not_ learned yet in that language from my Anki account (or alternatively, generate high-frequency words I haven't seen yet);
3. Use an LLM API to generate sentences that include exactly 1 word I haven't learned yet, and otherwise only words I've already learned;
4. Use a TTS API to generate audio for those sentences;
5. Export the resulting sentences, along with English translation and audio, to my Anki deck for that language.

## Usage
It's not done yet.
