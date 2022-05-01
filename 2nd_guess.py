import numpy as np
import pandas as pd

def calc_pattern(guess_word, target_word):
    num_chars = len(guess_word) # Number of characters in string
    pattern = ["0"] * num_chars # variable to store result
    
    for guess_idx in range(num_chars):
        
        if guess_word[guess_idx] == target_word[guess_idx]:
            pattern[guess_idx] = "2"
        
        else:
            for target_idx in range(num_chars):
                if (guess_idx != target_idx):
                    if (guess_word[guess_idx] == target_word[target_idx]) and (guess_word[target_idx] != target_word[target_idx]):
                        pattern[guess_idx] = "1"
                        target_word = target_word[0:target_idx] + '_' + target_word[target_idx + 1:]
                        break   
        
    return pattern

def create_all_ternary_strings(n, lst = [""]):
    # Function that recursively creates all possible binary strings of length n 
    # Used to determine all possible patterns of wordle squares
    if (n == 0): # Return set of strings
        return lst
    else:
        new_lst = []
        for idx in range(len(lst)): #For each string, add a 0 and a 1 to the end
            string = lst[idx] 
            
            string_and_0 = string + "0"
            string_and_1 = string + "1" 
            string_and_2 = string + "2"
            
            new_lst.append(string_and_0)
            new_lst.append(string_and_1)
            new_lst.append(string_and_2)

        return create_all_ternary_strings(n - 1, new_lst)

all_possible_patterns = create_all_ternary_strings(5)

def get_entropy_fast(guess_word, answer_bank):
    num_words = len(answer_bank)
    pattern_tracker = [''] * num_words

    for word_num, answer_word in enumerate(answer_bank):
        result_array = calc_pattern(guess_word, answer_word)

        result_string = ""

        for letter in result_array:
            result_string += letter

        pattern_tracker[word_num] = result_string 
    
    pattern_tracker = np.array(pattern_tracker)

    num_possible_patterns = len(all_possible_patterns) 
    entropy_tracker = np.empty(num_possible_patterns)

    for idx, pattern in enumerate(all_possible_patterns):
        p = np.sum(pattern_tracker == pattern) / num_words
        if p == 0:
            entropy_tracker[idx] = 0
        else:
            entropy_tracker[idx] = -p * (np.log(p) / np.log(2))
    
    return np.sum(entropy_tracker)

def get_best_guess(guess_list, answer_list): #YYYY
    entropy_tracker = np.empty(len(guess_list))

    for idx, guess_word in enumerate(guess_list):
        entropy_val = get_entropy_fast(guess_word, answer_list)

        entropy_tracker[idx] = entropy_val
    
    best_idx = np.argmax(entropy_tracker)
    best_entropy = entropy_tracker[best_idx]
    best_guess = guess_list[best_idx]

    if np.sum(entropy_tracker == best_entropy) > 1: # Multiple best guesses
        #print("Multiple Best Guesses")
        candidate_guesses = np.array(guess_list)[entropy_tracker == best_entropy]
        for guess_word in candidate_guesses:
            if guess_word in answer_list:
                return guess_word
                
        return best_guess

    return best_guess

def get_patterns(guess_word, answer_bank):
    num_words = len(answer_bank)
    pattern_tracker = [''] * num_words

    for word_num, answer_word in enumerate(answer_bank):
        result_array = calc_pattern(guess_word, answer_word)

        result_string = ""

        for letter in result_array:
            result_string += letter

        pattern_tracker[word_num] = result_string   
        
    result_df = pd.DataFrame({"Target":answer_bank, "Guess":guess_word,"Pattern":pattern_tracker })

    return result_df


answer_bank = pd.read_csv("answer_bank.txt")
answer_list = list(answer_bank["Word"])

guess_bank = pd.read_csv("guess_bank.txt")
guess_list = list(guess_bank["Word"])

# Best 1st guess
initial_guess = "soare"
# Get resulting patterns of all possible answers based upon initial_guess
patterns_df = get_patterns(initial_guess, answer_list)

# List to keep track of best second guess
second_guess_tracker = [''] * len(all_possible_patterns)

# Iterate through all possible patterns
for idx, current_pattern in enumerate(all_possible_patterns): 
    # Get list of all possible answers based upon the pattern we see
    remaining_possible_answers = list(patterns_df[patterns_df["Pattern"] == current_pattern]["Target"])

    # If no answers are possible
    if len(remaining_possible_answers) == 0:
        print(current_pattern, "-> -----")
        second_guess_tracker[idx] = "-----"
    else:
        best_second_guess = get_best_guess(guess_list, remaining_possible_answers)
        print(current_pattern, "->", best_second_guess)
        second_guess_tracker[idx] = best_second_guess


pd.DataFrame({"Pattern":all_possible_patterns,"2nd Guess": second_guess_tracker}).dropna().to_csv("2nd_guess.csv")