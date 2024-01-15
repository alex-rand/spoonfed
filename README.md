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

## Set-Up

### Anki Collection Set-Up
This app depends on the user having an existing Anki collection. Anki must be open in order for the AnkiConnect API to function properly. You must have two decks for study of the language you wish to use with Spoonfed:
- **The 'learned' deck**, containing cards that are either currently suitable for study (at most i+1), or will be suitable for study by the time they are learned if new cards are learned in the order added.
- ***The 'new' deck**, containing cards with words or phrases that are too difficult to learn (i+2 or higher). 

### User and Language Configuration 
When opening Spoonfed, you are prompted to create a user configuration, or select an existing one. **The name of the user configuration must be the same as the Anki username for the collection containing your 'learned' and 'new' decks.

After selecting a user configuration, you are prompted to create a language configuration. Here you tell Spoonfed the names of your 'learned' and 'new' decks, as well as all of the card types with at least one field containing relevant vocabulary in each of those decks, and the specific fields by card type. This configuration is a crucial step, allowing Anki to 

## Current Functionality
Spoonfed currently supports generative Anki card creation and augmentation in the following ways:

1. **Generate new i+1 sentences with audio** based on your learned vocabulary and the unlearned words containing in the 'new' deck. 
2. **Add audio to existing cards in the 'learned' deck** using the Narakeet API. This is useful for improving cards created before integrating Spoonfed into your workflow, or cards with sentences found in the wild. 

All interactions with generative AI are logged in an SQLite database for analysis. 
## Future Functionalities

- Edit and store LLM-generated sentences.
- Suggest new high-frequency vocabulary to learn based on your current selection.
- Modify the text-generation prompt to focus on specific subject matter or regional idioms.
- Interactively analyze your generative AI usage to track usage over time, and compare generated content quality under different LLM models.
