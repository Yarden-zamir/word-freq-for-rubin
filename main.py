from collections import Counter
from os import getenv
import re

from collections import Counter
import re
import glob
import nltk
from nltk.corpus import stopwords
import pandas as pd
import requests

YOUR_SHEET_ID = getenv("SHEET_ID")

r = requests.get(
    f"https://docs.google.com/spreadsheet/ccc?key={YOUR_SHEET_ID}&output=csv"
)
open("dataset.csv", "wb").write(r.content)
data = pd.read_csv("dataset.csv")
data_sources_column = data[
    "whitelist datasources"
]  # a list of big strings that contain words we want
blacklist_words_column = data["blacklist words"]  # a list of words we don't want

blacklist_words_list = blacklist_words_column.to_list()

word_counts = Counter()
nltk.download("stopwords")

for data_source in data_sources_column:
    data_source = str(data_source).lower()
    for line in data_source.split("\n"):  # iterates through every line
        words: list[str] = line.replace(" ", " ").replace("\r","").split(" ")
        words = [
            word.removesuffix(".")
            .removesuffix("?")
            .removesuffix("!")
            .removesuffix(",")
            .replace("\n", "")
            .removesuffix("s")
            for word in words
        ]
        words = [
            word
            for word in words
            if word not in stopwords.words("english")
            and word not in blacklist_words_list
            and word.removesuffix("s") not in blacklist_words_list
            and word.removesuffix("s") not in stopwords.words("english")
            and word not in ["", " ", "  ", "nan", "/","=","+","-","–"]
            and not word.isnumeric()
        ]
        word_counts.update(words)
# Get the most common words and their counts
# Filter out words that appear in the nltk corpus
top_words = word_counts.most_common(12000)
total_words = sum(count for _, count in top_words)

# Start Markdown table
markdown_table = "| Rank | Word | Count | Percentage | Cumulative Percentage | Definition | Translation |\n"
markdown_table += "|------|------|-------|------------|-----------------------|------------|-------------|\n"

cumulative_percentage = 0
rank = 1
for word, count in top_words:
    clean_word = word.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace(":", "").replace(";", "").replace("!", "").replace("?", "").replace(".", "").replace(",", "").replace(" ", "-")
    definition = f"[definition](https://www.dictionary.com/browse/{clean_word})"

    translation = f"[translation](https://translate.google.com/?hl=iw&sl=auto&tl=iw&text={clean_word}&op=translate)"
    percentage = (count / total_words) * 100
    cumulative_percentage += percentage
    markdown_table += f"| {rank} | {word} | {count} | {percentage:.2f}% | {cumulative_percentage:.2f}% | {definition} | {translation} |\n"
    rank += 1

print(
    f"source: [google sheets](https://docs.google.com/spreadsheets/d/{YOUR_SHEET_ID})  "
)
print(
    f"to build, run [build_table workflow](https://github.com/Yarden-zamir/word-freq-for-rubin/actions/workflows/build_table.yml)"
)
print(markdown_table)
print(
    "<br>".join(
        [
            # just the words in order without their frequency
            word
            for word, _ in top_words
        ]
    )
)
print(top_words[:20])
