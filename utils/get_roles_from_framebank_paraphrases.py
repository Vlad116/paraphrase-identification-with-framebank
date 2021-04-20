import re
import numpy
import csv

framebank_file = '../data/paraphrases_all_framebank.txt'
paraphrases_tsv = '../data/paraphrases.tsv'
paraphrases_gold_tsv = '../data/paraphrases_gold.tsv'

roles_file = '../data/framebank_roles.tsv'
paraphrases_with_roles = '../data/paraphrases_framebank.tsv'

def substring_after(s, delim):
    return s.partition(delim)[2]

def create_roles_dictionary(framebank_file=framebank_file):
    with open(framebank_file, encoding="utf8") as fbFile:
        # Удалить пробелы и переносы строк в выделенном pred/arg
        regexp = "^\s+|\n|\r|\s+$"
        pred_delimeter = '=====Pred: '
        arg_delim = ': '
        arg_role_start_char = '('
        arg_role_end_char = ')'

        current_line = 1 
        # строка с предложением которое анализируем
        current_phrase = ''
        # выделененные после анализа роли
        roles = ""
        phrases_roles = {}

        tokenized_phr_line = 2
        roles_in_phrase_map = {}
        phrases_tokenized_ph = {}

        for num, line in enumerate(fbFile, 1):
            if num == current_line:
                if pred_delimeter in line:
                    pred = re.sub("^\s+|\n|\r|\s+$", '', substring_after(line, pred_delimeter))
                    roles += pred + ','
                    roles_in_phrase_map[pred] = '<pred>'
                    # print('pred: ', pred)
                    current_line += 1
                    continue
                elif 'Arg(' in line:
                    arg = re.sub("^\s+|\n|\r|\s+$", '', substring_after(line, arg_delim))
                    arg_role = line[line.find(arg_role_start_char) + 1 : line.find(arg_role_end_char)]
                    roles += arg_role + ','
                    roles_in_phrase_map[arg] = arg_role
                    # print('ARG: ', arg)
                    # print('ARG role: ', arg_role)
                    current_line += 1
                    continue          
                elif line == '\n':
                    roles = roles[:len(roles) - 1]
                    phrases_roles[current_phrase] = roles_in_phrase_map                    
                    roles_in_phrase_map = {}
                    roles = ""
                    current_line += 1
                    continue

                tokenized_phr_line = current_line + 1
                current_line += 2
                current_phrase = line.replace("\n","")

            if num == tokenized_phr_line:
                phrases_tokenized_ph[current_phrase] = line.replace("\n","") 

    return phrases_roles, phrases_tokenized_ph

roles_dictionary, tokenized_ph_dictionary = create_roles_dictionary(framebank_file)

def align_tokens_lenght(tokenized_phrase,phrase_roles):
    tokens = tokenized_phrase.split()
    roles_tokens = []
    
    for token in tokens:
        if token in phrase_roles:
            roles_tokens.append(phrase_roles[token])
        else:
            roles_tokens.append('<unk>')
    return roles_tokens

def read_tsv_and_find_roles(file, writer):
    file_reader = csv.DictReader(file, delimiter='\t', quoting=csv.QUOTE_NONE)
    line_count = 0

    for row in file_reader:
        if line_count == 0:
            # print(f'Column names are {" ".join(row)}')
            line_count += 1

        ph1 = row["question1"]
        ph2 = row["question2"]
        
        try:
            tokenized_ph1 = tokenized_ph_dictionary[ph1.rstrip()]
        except KeyError as e:
            print(e)
            print(ph1[len(ph1) - 1:])
            print(ph1[:-1])
            print(ph1[len(ph1) - 1:] == ' ' or ph1[len(ph1) - 1:] == '\t')
            if ph1[len(ph1) - 1:] == ' ' or ph1[len(ph1) - 1:] == '\t':
                tokenized_ph1 = tokenized_ph_dictionary[ph1[:-1]]            
            else:
                continue

        roles1 = align_tokens_lenght(tokenized_ph1, roles_dictionary[ph1.rstrip()])

        tokenized_ph2 = tokenized_ph_dictionary[ph2.rstrip()]
        roles2 = align_tokens_lenght(tokenized_ph2, roles_dictionary[ph2.rstrip()])        
        
        # ','.join() - convert rokes_tokens list to string with ',' separator
        writer.writerow({
            'phrase1': tokenized_ph1, 
            'roles1': ','.join(roles1),
            'phrase2': tokenized_ph2,
            'roles2': ','.join(roles2), 
            'is_duplicate': row["is_duplicate"]
        })

        line_count += 1

def convert_tsv_data_to_with_role(train_file=paraphrases_tsv, test_file=paraphrases_gold_tsv, output_file=paraphrases_with_roles):
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        fieldnames = ['phrase1','roles1','phrase2','roles2','is_duplicate']
        delimiter = '\t'
        quotechar = ''        
        quoting = quoting=csv.QUOTE_NONE
        output_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=delimiter, quoting=quoting, quotechar=quotechar, escapechar='')
        output_writer.writeheader()

        with open(train_file, mode='r', encoding='utf-8') as tsv_file:
            read_tsv_and_find_roles(tsv_file,output_writer)
        with open(test_file, mode='r', encoding='utf-8') as tsv_file:
            read_tsv_and_find_roles(tsv_file,output_writer)

convert_tsv_data_to_with_role()