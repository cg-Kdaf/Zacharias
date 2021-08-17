import spacy
from spacy import displacy
from os import path
# from nltk.corpus import wordnet as wn

print("start\n\n")
project_root = path.split(path.dirname(path.abspath(__file__)))[0]


# def find_antonyms(word):
#     antonyms = []
#     for syn_set in wn.synsets("have"):
#         for l in syn_set.lemmas():
#             if l.antonyms():
#                 antonyms.append(l.antonyms()[0].name())
#     return list(dict.fromkeys(antonyms))


nlp = spacy.load("en_core_web_lg")


def find_corresponding_action(speech, actions, minimum):
    highest_rate = 0
    speech_nlp = nlp(speech)
    highest_rate_id = 0
    power = 1. if any(doc.pos_ == "NOUN" for doc in speech_nlp) else 0.8
    for id, action in enumerate(actions):
        factor = nlp(action).similarity(speech_nlp)
        if factor > minimum and factor > highest_rate:
            highest_rate_id = id
            highest_rate = factor
    # displacy.serve(speech_nlp, style="dep")
    return(highest_rate_id, highest_rate, power)


def split_sentence_clauses(text):
    # TODO add proper descriptions everywhere and clean the code. Also remove unused lines.
    seen = set() # keep track of covered words
    doc = nlp(text)
    chunks = []
    for sent in doc.sents:
        # for cc in sent.root.children:
        #     print(cc.dep_)
        heads = [cc for cc in sent.root.children if cc.dep_ in ['conj', "ccomp"]]

        for head in heads:
            words = [ww for ww in head.subtree]
            for word in words:
                seen.add(word)
            chunk = (' '.join([ww.text for ww in words]))
            chunks.append( (head.i, chunk) )

        unseen = [ww for ww in sent if ww not in seen]
        chunk = ' '.join([ww.text for ww in unseen])
        chunks.append( (sent.root.i, chunk) )

    chunks = sorted(chunks, key=lambda x: x[0])

    # print([chunk[1] for chunk in chunks])
    return([chunk[1] for chunk in chunks])
    # displacy.serve(doc, style="dep")


def test_samples():
    actions = open(path.join(project_root, "tests/basic_actions"), "r").readlines()
    for id in range(len(actions)):
        actions[id] = actions[id].replace("\n", "").split(" - ")[1]
    sentences_ = open(path.join(project_root, "tests/intent_action_correspondance.txt"), "r")
    sentences_ = sentences_.readlines()
    sentences = []
    for id in range(len(sentences_)):
        if sentences_[id] != "\n":
            action_id, sentence = sentences_[id].replace("\n", "").split(" - ")
            action_id = int(action_id)
            sentences.append([action_id, sentence])
    # example = sentences[14][1]
    # split_sentence_clauses(example)
    # exit()

    error_length = 0
    for sentence in sentences:
        clauses = split_sentence_clauses(sentence[1])
        found_action_id = 0
        factor = 0.
        for clause in clauses:
            id, fac, power = find_corresponding_action(clause, actions, 0.7)
            if fac*power > factor:
                # print(clause)
                found_action_id, factor = id, fac*power
        if found_action_id != sentence[0]-1:
            print(clauses, factor)
            print(f"'{sentence[1]}'   ->   Error")
            print(f"found : \n   {actions[found_action_id]} \ninstead of\n   {actions[sentence[0]-1]} \n")
            error_length += 1
            # displacy.serve(nlp(sentence[1]), style="dep")
    print(f"Error rate : {error_length/len(sentences)}")


test_samples()
