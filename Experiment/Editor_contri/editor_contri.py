import xml.etree.ElementTree as ET
import xml.dom.minidom
import re
import difflib
import collections
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import sys
import matplotlib.pyplot as plt

author_contribution = collections.defaultdict(lambda: 0)
similarity_arr = []
revision_no_arr = []


def split_sentences(self, text):
    import textwrap
    text = text.replace('.\n', '. ').replace('\r', '')
    text = text.replace('\n', '. ').replace('\r', '')
    text = textwrap.dedent(text).strip()
    text = re.sub('([A-Z][a-z]+)', r' \1', text)
    text = re.sub(' +', ' ', text)
    text = " ".join(text.split())
    st = text.strip() + '. '
    sentences = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', st)
    # (? <=\p{Lt}.[.?]) + (?=\p{Lu})
    return sentences


def similarity_score(paragraph, revision):
    s1 = s2 = ""
    if len(paragraph) < len(revision):
        s1 = paragraph
        s2 = revision
    else:
        s2 = paragraph
        s1 = revision
    max_similarity = 0

    s1_sentences = split_sentences(s1)
    s2_sentences = split_sentences(s2)

    for each in s1_sentences:
        match = get_close_matches(each, s2_sentences, cutoff=0.4)


    # sw contains the list of stopwords
    sw = stopwords.words('english')

    # tokenization
    X_list = word_tokenize(s1)

    # remove stop words from string
    X_set = {w for w in X_list if w not in sw}

    for i in range(len(s2) - len(s1)):
        Y_list = word_tokenize(s2[i:i + len(s1)])
        l1 = []
        l2 = []
        Y_set = {w for w in Y_list if w not in sw}

        # form a set containing keywords of both strings
        rvector = X_set.union(Y_set)
        for w in rvector:
            if w in X_set:
                l1.append(1)  # create a vector
            else:
                l1.append(0)
            if w in Y_set:
                l2.append(1)
            else:
                l2.append(0)

        c = 0
        # cosine formula
        for j in range(len(rvector)):
            c += l1[j] * l2[j]
        cosine = 0
        if sum(l1) != 0 and sum(l2) != 0:
            cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
        if max_similarity < cosine:
            max_similarity = cosine

    return max_similarity


def max_cosine_similarity(paragraph, revision):
    s1 = s2 = ""
    if len(paragraph) < len(revision):
        s1 = paragraph
        s2 = revision
    else:
        s2 = paragraph
        s1 = revision
    max_similarity = 0


    # sw contains the list of stopwords
    sw = stopwords.words('english')

    # tokenization
    X_list = word_tokenize(s1)

    # remove stop words from string
    X_set = {w for w in X_list if w not in sw}

    for i in range(len(s2) - len(s1)):
        Y_list = word_tokenize(s2[i:i + len(s1)])
        l1 = []
        l2 = []
        Y_set = {w for w in Y_list if w not in sw}

        # form a set containing keywords of both strings
        rvector = X_set.union(Y_set)
        for w in rvector:
            if w in X_set:
                l1.append(1)  # create a vector
            else:
                l1.append(0)
            if w in Y_set:
                l2.append(1)
            else:
                l2.append(0)

        c = 0
        # cosine formula
        for j in range(len(rvector)):
            c += l1[j] * l2[j]
        cosine = 0
        if sum(l1) != 0 and sum(l2) != 0:
            cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
        if max_similarity < cosine:
            max_similarity = cosine

    return max_similarity


# Main Function
# if len(sys.argv) < 2:
#     print("Input Format: python3 script_name input_file_name")
#     exit()

file_name = "/home/neeru/WORK/Data folder/article_list/Bill_Gates.knolml"  # sys.argv[1]

tree = ET.parse(file_name)
root = tree.getroot()
last_rev = ""
count = 0
length = len(root[0].findall('Instance'))

revision_list = []
author_list = []

for each in root.iter('Instance'):
    instanceId = int(each.attrib['Id'])
    for child in each:
        if 'Contributors' in child.tag:
            author_list.append(child[0].text)
        if 'Body' in child.tag:
            revision = child[0].text
            revision = re.sub(r'\*?\{\{[^\}]*\}\}', "", revision)
            revision = re.sub(r'\*?\[\[[^\]]*\]\]', "", revision)
            revision = re.sub(r'\*?\<[^\>]*\>', "", revision)
            revision = ' '.join(revision.split())
            revision_list.append(revision)

print(revision_list[int(len(revision_list) / 2)])

import os
paraFiles = os.listdir("/home/neeru/WORK/Data folder/Summaries/Bill Gates/")
for f in paraFiles:
    summary = open("/home/neeru/WORK/Data folder/Summaries/Bill Gates/"+f, "r")
    paragraph = summary.read()
    # paragraph = input("Enter paragraph: ")
    last_val = 0
    print("\nRunning...\n")
    for i in range(len(revision_list)):
        curr_val = max_cosine_similarity(paragraph, revision_list[i])
        print(author_list[i], "Similarity:", curr_val, "Progress:", i, "/", len(revision_list))
        similarity_arr.append(curr_val)
        revision_no_arr.append(i + 1)
        if last_val == 1.0 and curr_val == 1.0:
            continue
        if author_contribution[author_list[i]] == 0 or author_contribution[author_list[i]] > curr_val:
            author_contribution[author_list[i]] = curr_val
        last_val = curr_val

    print("\nContributions of author(s) to the given paragraph:\n")

    saveFile = open(f+"_list.txt", "w")
    for x in sorted(author_contribution.items(), key=lambda x: x[1]):
        print(x[0], "\n--->", x[1])
        saveFile.write(x[0], "\n--->", x[1])

    plt.plot(revision_no_arr, similarity_arr)
    plt.xlabel("Revision number")
    plt.ylabel("Similarity value")
    plt.show()
    plt.savefig(f+'_plot.png')