from spacy import load as spacy_load
# from spacy import displacy
from os import path
import utils

NLP_MODEL = spacy_load("en_core_web_md")


def intent_to_action(speech: str, actions: list):
    """This function tries to find an action from the speech. It uses Spacy similarity tool.

    Args:
        speech (string): Sentence to be compared to the actions
        actions (string list): List of sentences that describe each actions
    Returns:
        action_id (int): the most probable action that matches the speech
        action_probability (float): probability that the speech matches this action
        probability_multiplier (float): multiplier to lower the probability if sentence data do not
        help to find a corresponding action
    """
    action_probability = 0.
    speech_nlp = NLP_MODEL(speech)
    action_id = 0
    probability_multiplier = 1. if any(doc.pos_ == "NOUN" for doc in speech_nlp) else 0.8
    for id, action in enumerate(actions):
        factor = float(NLP_MODEL(action).similarity(speech_nlp))
        if factor > action_probability:
            action_id = id
            action_probability = factor
    # displacy.serve(speech_nlp, style="dep")
    return(action_id, action_probability, probability_multiplier)


def split_sentence_clauses(sentences):
    """Split the given sentence(s) into a list of clauses. This is using the dependencies given by
    spacy, but the accurary is not optimal since clauses detection is very hard toachieve right.

    This functions helps for example to try sentence similarities with different portions of the
    sentence in order to have more accurate results.

    TODO : Better restituate the punctuation.

    Args:
        sentence (str): Sentence(s) to split
    Returns:
        clauses_list (str list)
    """
    seen = set()  # keep track of covered words
    doc = NLP_MODEL(sentences)
    clauses = []
    for sentence in doc.sents:  # Split into sentences if the input string is a text
        heads = [cc for cc in sentence.root.children if cc.dep_ in ['conj', "ccomp"]]

        for head in heads:
            words = [ww for ww in head.subtree]
            for word in words:
                seen.add(word)
            clause = (' '.join([ww.text for ww in words]))
            clauses.append((head.i, clause))

        unseen = [ww for ww in sentence if ww not in seen]
        clause = ' '.join([ww.text for ww in unseen])
        clauses.append((sentence.root.i, clause))

    clauses = sorted(clauses, key=lambda x: x[0])

    return([clause[1] for clause in clauses])


def test_samples():
    actions = open(path.join(utils.project_root, "tests/basic_actions"), "r").readlines()
    for id in range(len(actions)):
        actions[id] = actions[id].replace("\n", "").split(" - ")[1]
    sentences_ = open(path.join(utils.project_root, "tests/intent_action_correspondance.txt"), "r")
    sentences_ = sentences_.readlines()
    sentences = []
    for id in range(len(sentences_)):
        if sentences_[id] == "-- Checkpoint":
            sentences.append("Checkpoint")
        elif sentences_[id] != "\n":
            action_id, sentence = sentences_[id].replace("\n", "").split(" - ")
            action_id = int(action_id)
            sentences.append([action_id, sentence])

    error_len = 0
    chunk = 0
    chunk_len = 0
    for sentence in sentences:
        if sentence == "Checkpoint":
            print(f"Error rate for chunk {chunk}: {error_len/chunk_len}")
            chunk += 1
            chunk_len = 0
            continue
        clauses = split_sentence_clauses(sentence[1])
        found_action_id = 0
        factor = 0.
        for clause in clauses:
            id, fac, power = intent_to_action(clause, actions)
            if fac*power > factor:
                # print(clause)
                found_action_id, factor = id, fac*power
        chunk_len += 1
        if found_action_id != sentence[0]-1:
            print(clauses, factor)
            print(f"'{sentence[1]}'   ->   Error")
            print(f"""found : \n   {actions[found_action_id]}
                      \rinstead of\n   {actions[sentence[0]-1]} \n""")
            error_len += 1
            # displacy.serve(NLP_MODEL(sentence[1]), style="dep")  # Used to analyse the error


test_samples()
