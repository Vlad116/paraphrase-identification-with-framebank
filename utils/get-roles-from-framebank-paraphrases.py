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

        for num, line in enumerate(fbFile, 1):
            if num == current_line:
                if pred_delimeter in line:
                    pred = re.sub("^\s+|\n|\r|\s+$", '', substring_after(line, pred_delimeter))
                    roles += pred + ' '
                    # print('pred: ', pred)
                    current_line += 1
                    continue
                elif 'Arg(' in line:
                    arg = re.sub("^\s+|\n|\r|\s+$", '', substring_after(line, arg_delim))
                    arg_role = line[line.find(arg_role_start_char) + 1 : line.find(arg_role_end_char)]
                    roles += arg + ' '
                    # print('ARG: ', arg)
                    # print('ARG role: ', arg_role)
                    current_line += 1
                    continue          
                elif line == '\n':
                    roles = roles[:len(roles) - 1]
                    phrases_roles[current_phrase] = roles
                    roles = ""
                    current_line += 1
                    continue

                # print('\nphrase: ', line.replace("\n",""))
                current_line += 2
                current_phrase = line.replace("\n","")
    
    return phrases_roles

roles_dictionary = create_roles_dictionary(framebank_file)

# for key,value in roles_dictionary.items():
#     print('Phrase: ' + key + ' Roles: ' + value)

def read_tsv_and_find_roles(file, writer):
    file_reader = csv.DictReader(file, delimiter='\t',quotechar="'", quoting=csv.QUOTE_MINIMAL)
    line_count = 0

    for row in file_reader:
        if line_count == 0:
            # print(f'Column names are {" ".join(row)}')
            line_count += 1

        q1 = row["question1"]
        q2 = row["question2"]
        roles1 = roles_dictionary[q1] if q1 in roles_dictionary.keys() and roles_dictionary[q1] != "" else "none"
        roles2 = roles_dictionary[q2] if q2 in roles_dictionary.keys() and roles_dictionary[q2] != "" else "none"

        writer.writerow({
            'question1': q1, 
            'roles1': roles1,
            'question2': q2,
            'roles2': roles2, 
            'is_duplicate': row["is_duplicate"]
            })
        line_count += 1

def write_roles_to_tsv(file, writer):
    file_reader = csv.DictReader(file, delimiter='\t',quotechar="'", quoting=csv.QUOTE_MINIMAL)
    line_count = 0

    for row in file_reader:
        if line_count == 0:
            # print(f'Column names are {" ".join(row)}')
            line_count += 1

        q1 = row["question1"]
        q2 = row["question2"]

        roles1 = roles_dictionary[q1] if q1 in roles_dictionary.keys() and roles_dictionary[q1] != "" else "none"
        roles2 = roles_dictionary[q2] if q2 in roles_dictionary.keys() and roles_dictionary[q2] != "" else "none"

        writer.writerow({
            'roles1': roles1,
            'roles2': roles2, 
            'is_duplicate': row["is_duplicate"]
        })

        line_count += 1
        
def convert_tsv_data_to_with_role(train_file=paraphrases_tsv, test_file=paraphrases_gold_tsv, output_file=paraphrases_with_roles, roles_file=roles_file):
    # question1 question2 is_duplicate
    with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
        fieldnames = ['question1','roles1','question2','roles2','is_duplicate']
        delimiter = '\t'
        quotechar = "'"
        quoting = quoting=csv.QUOTE_MINIMAL
        output_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
        output_writer.writeheader()

        with open(roles_file, mode='w', encoding='utf-8', newline='') as roles_file:
            roles_fieldnames = ['roles1', 'roles2', 'is_duplicate']
            roles_writer = csv.DictWriter(roles_file, fieldnames=roles_fieldnames, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
            roles_writer.writeheader()

            with open(train_file, mode='r', encoding='utf-8') as tsv_file:
                read_tsv_and_find_roles(tsv_file,output_writer)

            with open(test_file, mode='r', encoding='utf-8') as tsv_file:
                read_tsv_and_find_roles(tsv_file,output_writer)

            with open(train_file, mode='r', encoding='utf-8') as tsv_file:
                write_roles_to_tsv(tsv_file,roles_writer)
            
            with open(train_file, mode='r', encoding='utf-8') as tsv_file:
                write_roles_to_tsv(tsv_file,roles_writer)

convert_tsv_data_to_with_role()

# import pandas as pd

# def create_roles_list(framebank_file=framebank_file):
#     with open(framebank_file, encoding="utf8") as fbFile:

#         # Удалить пробелы и переносы строк в выделенном pred/arg
#         regexp = "^\s+|\n|\r|\s+$"
#         pred_delimeter = '=====Pred: '
#         arg_delim = ': '
#         arg_role_start_char = '('
#         arg_role_end_char = ')'

#         current_line = 1 
#         # строка с предложением которое анализируем
#         current_phrase = ''
#         # выделененные после анализа роли
#         roles = ""
#         roles_list = []

#         for num, line in enumerate(fbFile, 1):
#             if num == current_line:
#                 if pred_delimeter in line:
#                     pred = re.sub("^\s+|\n|\r|\s+$", '', substring_after(line, pred_delimeter))
#                     roles += pred + ' '
#                     # print('pred: ', pred)
#                     current_line += 1
#                     continue
#                 elif 'Arg(' in line:
#                     arg = re.sub("^\s+|\n|\r|\s+$", '', substring_after(line, arg_delim))
#                     arg_role = line[line.find(arg_role_start_char) + 1 : line.find(arg_role_end_char)]
#                     roles += arg + ' '
#                     # print('ARG: ', arg)
#                     # print('ARG role: ', arg_role)
#                     current_line += 1
#                     continue          
#                 elif line == '\n':
#                     roles = roles[:len(roles) - 1]
#                     roles_list.append(roles)
#                     roles = ""
#                     current_line += 1
#                     continue

#                 # print('\nphrase: ', line.replace("\n",""))
#                 current_line += 2
#                 current_phrase = line.replace("\n","")
    
#     return roles_list
        
# def write_roles_to_tsv(output_file=output_file):

#     labels_from_train = pd.read_csv(paraphrases_tsv, sep='\t', usecols=["is_duplicate"])
#     labels_from_test = pd.read_csv(paraphrases_gold_tsv, sep='\t', usecols=["is_duplicate"])

#     df_res = pd.concat([labels_from_train, labels_from_test])
#     labels = df_res.squeeze()
#     roles_list = create_roles_list()

#     with open(output_file, mode='w', encoding='utf-8', newline='') as output_file:
#         fieldnames = ['roles1','roles2','is_duplicate']
#         delimiter = '\t'
#         quotechar = "'"
#         quoting = quoting=csv.QUOTE_MINIMAL
#         output_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=delimiter, quotechar=quotechar, quoting=quoting)
#         output_writer.writeheader()        

#         line_numb = 1
#         first_roles = ''
#         print(len(labels))
#         print(len(roles_list))

#         for role in roles_list:
#             if line_numb % 2 == 1:
#                 first_roles = role
#                 line_numb += 1
#                 continue

#             output_writer.writerow({
#                 'roles1': first_roles,
#                 'roles2': role, 
#                 'is_duplicate': labels[line_numb - 1]
#             })
            
#             line_numb += 1

# write_roles_to_tsv()