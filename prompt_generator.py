import random, string, re

with open('words.txt', 'r') as f:
    words = f.read().splitlines()

def generate_normal_prompt():
    word = ''
    while len(word) < 4:
        word = random.choice(words)

    match random.randint(0,1):
        case 0:
            length = random.randint(3, 4)
            index = random.randint(0, len(word) - length)
            regex = word[index:index+length]
        case 1:
            length = random.randint(3, 4)
            regex = ''.join(random.sample(string.ascii_lowercase, length))


    matches = 0
    for word in words:
        if re.match('^.*' + regex + '.*$', word):
            matches += 1
    
    if matches >= 10 and matches <= 1000 and regex not in words:
        return regex
    else:
        return generate_normal_prompt()

def generate_regex_prompt(difficulty):
    word1 = random.choice(words)
    word2 = random.choice(words)

    while len(word1) < 3:
        word1 = random.choice(words)
    while len(word2) < 3:
        word2 = random.choice(words)

    regex = ""

    # Generate 2 random letters
    letters = ''.join(random.sample(string.ascii_lowercase, 2))
    letter1 = letters[0]
    letter2 = letters[1]

    # Generate 2 random 2-character substrings
    index = random.randint(0, len(word1) - 2)
    substring1 = word1[index:index+2]
    index = random.randint(0, len(word2) - 2)
    substring2 = word2[index:index+2]

    # Generate 2 strings of 4-7 unique random letters in [ ]
    matching_list1 = "[" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"
    matching_list2 = "[" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"

    # Generate 2 strings of 4-7 unique random letters in [^ ]
    negated_matching_list1 = "[^" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"
    negated_matching_list2 = "[^" + ''.join(random.sample(string.ascii_lowercase, random.randint(3, 5))) + "]"

    # Generate 2 number ranges
    num_range1 = "{" + str(random.randint(0, 3)) + "," + str(random.randint(6, 10)) + "}"
    num_range2 = "{" + str(random.randint(0, 3)) + "," + str(random.randint(6, 10)) + "}"

    # Generate 2 character ranges (e.g. [a-z])
    char_range1 = "[" + random.choice('abcdefghijklm') + "-" + random.choice('nopqrstuvwxyz') + "]"
    char_range2 = "[" + random.choice('abcdefghijklm') + "-" + random.choice('nopqrstuvwxyz') + "]"

    # Generate 6 more segments for the ors
    index = random.randint(0, len(word1) - 2)
    substring3 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    substring4 = word2[index:index+2]
    index = random.randint(0, len(word1) - 2)
    substring5 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    substring6 = word2[index:index+2]
    index = random.randint(0, len(word1) - 2)
    substring7 = word2[index:index+2]
    index = random.randint(0, len(word2) - 2)
    substring8 = word2[index:index+2]

    # Generate 2 option based string matches
    or1 = "(" + substring3 + "|" + substring4 + "|" + substring5 + ")"
    or2 = "(" + substring6 + "|" + substring7 + "|" + substring8 + ")"

    match difficulty:     
        case 'regex-easy':
            options1 = [letter1, substring1, matching_list1]
            options2 = [letter2, substring2, matching_list2]
            begin = ['.+', '.*', letter1, letter2, '\w*', '\w+']
            connect = ['.+', '.*', '\w*', '\w+']

            match(random.randint(1, 8)):
                case 1: regex = random.choice(options1) + random.choice(connect)
                case 2: regex = random.choice(begin) + random.choice(options1)
                case 3: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2)
                case 4: regex = random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)
                case other: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)

            matches = 0
            for word in words:
                if re.match('^' + regex + '$', word):
                    matches += 1
            
            if matches >= 50 and matches <= 1000:
                return regex
            else:
                return generate_regex_prompt(difficulty)
            
        case 'regex-hard':
            options1 = [letter1, substring1, matching_list1, negated_matching_list1, char_range1, or1]
            options2 = [letter2, substring2, matching_list2, negated_matching_list2, char_range2, or2]
            begin = ['.+', '.*', letter1, letter2, matching_list1, matching_list2, '\w*', '\w+']
            connect = ['.+', '.*', '+', '*', '+.+', '+.*', '?', num_range1, num_range2, '\w*', '\w+'] 

            match(random.randint(1, 8)):
                case 1: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2)
                case 2: regex = random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)
                case other: regex = random.choice(begin) + random.choice(options1) + random.choice(connect) + random.choice(options2) + random.choice(connect)

            matches = 0
            for word in words:
                if re.match('^' + regex + '$', word):
                    matches += 1
            
            if matches > 10 and matches <= 500:
                return regex
            else:
                return generate_regex_prompt(difficulty)

prompts = []

for i in range(5000):
    prompts.append(generate_regex_prompt('regex-hard'))

prompts = list(set(prompts))

with open('hard_regex_prompts.txt', 'w') as f:
    for prompt in prompts:
        f.write(prompt + '\n')

print("Done")