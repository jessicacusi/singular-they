"""Rule-based Baseline Model to substitute binary pronouns to singular 'they'."""

import pandas as pd
import re


def preprocessing(raw_data):
    """
    Lowercase original and gold sentences, remove <<< >>> that encase binary pronouns
    from original data collection process, and remove extra spaces.

    :param raw_data: dataframe with index, text id, original-text, and gold-text
    :return: dataframe with cleaned original and gold sentences
    """

    original_text = raw_data['original-text']
    gold_text = raw_data['gold-text']
    for i in range(len(raw_data)):
        lower = original_text[i].lower()
        clean = re.sub('(<<<)|(>>>)', '', lower)
        rm_extraspace = re.sub('\s\s', ' ', clean)
        raw_data['original-text'][i] = rm_extraspace
        lower_gold = gold_text[i].lower()
        raw_data['gold-text'][i] = lower_gold
    preprocessed_data = raw_data

    return preprocessed_data


def pronoun_replacement(preprocessed_data):
    """
    Replace binary pronoun forms with corresponding singular they forms.

    :param preprocessed_data: dataframe with cleaned original and gold sentences
    :return: dataframe with switched pronouns
    """

    for i in range(len(preprocessed_data)):
        s = preprocessed_data['original-text'][i]
        replaced_data = re.sub('he/she', 'they', s)
        replaced_data = re.sub('his/her', 'their', replaced_data)
        replaced_data = re.sub('him/her', 'them', replaced_data)
        replaced_data = re.sub('his/hers', 'theirs', replaced_data)
        preprocessed_data['original-text'][i] = replaced_data
    they_data = preprocessed_data

    return they_data


def verb_adjustment(they_data):
    """
    Change verb forms from third-person singular to third-person plural.

    :param they_data: dataframe with switched pronouns
    :return: dataframe with corrected verbs
    """

    for i in range(len(they_data)):
        s = they_data['original-text'][i]
        be = re.search('they is', s)
        have = re.search('they has', s)
        do = re.search('they does', s)
        pattern = r'\bthey\s+(\S*?s)\b'
        reg_verb = re.search(pattern, s)

        if be:
            new_data = re.sub('they is', 'they are', s)
        elif have:
            new_data = re.sub('they has', 'they have', s)
        elif do:
            new_data = re.sub('they does', 'they do', s)
        elif reg_verb:
            new_data = re.sub(pattern,
                              lambda match: 'they ' + match.group(1)[:-1] if match.group(1).endswith(
                                  's') else match.group(
                                  0), s)
        else:
            new_data = they_data['original-text'][i]
        they_data['original-text'][i] = new_data
        clean = they_data

    return clean


def matcher(clean):
    """
    Add score column to dataframe: 1 for original and gold are identical, 0 if not.

    :param clean: dataframe with corrected verbs
    :return: dataframe with score column
    """

    score = []
    for i in range(len(clean)):
        if clean.iloc[i]['original-text'] == clean.iloc[i]['gold-text']:
            score.append(1)
        else:
            score.append(0)

    clean['score'] = score
    final_data = clean

    return final_data


def metrics(final_data):
    """
    Get accuracy metrics.

    :param final_data: dataframe with score column
    :return: number of matching sentences, accuracy score
    """

    sum_score = final_data['score'].sum()
    accuracy = sum_score / len(final_data)

    return sum_score, accuracy


if __name__ == "__main__":
    path = "test_data.tsv"
    raw_data = pd.read_csv(path, delimiter='\t')
    preprocessed_data = preprocessing(raw_data)
    they_data = pronoun_replacement(preprocessed_data)
    clean = verb_adjustment(they_data)
    final_data = matcher(clean)
    sum_score, accuracy = metrics(final_data)
    print('Number of correct/matching sentences: ', sum_score)
    print('Accuracy = ', accuracy)
    # uncomment below to print csv
    # final_data.to_csv(r'/Users/jessicacusi/Desktop/final_data.csv', index=False)
