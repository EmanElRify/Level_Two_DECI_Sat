# Program 1: Extracting First 2 and Last 2 Characters
def get_first_last_2_chars(input_str):
   if len(input_str) < 2:
       return ""
   else:
       return input_str[:2] + input_str[-2:]


# Test cases
sample_strings = ['udacity-deci', 'deci', ' w', 'de', 'dec']
for string in sample_strings:
   result = get_first_last_2_chars(string)
   print(f"Sample String: '{string}' -> Expected Result : '{result}'")


# BONUS 1: Extracting Names from a Delimited String
def extract_names(long_string):
   names = long_string.split(':')
   for name in names:
       print(name)


# Test case
long_string = "Alice:Bob:Charlie:David:Emily"
extract_names(long_string)


# BONUS 2: Extracting Middle Three Characters
def get_middle_three_chars(input_str):
   middle_index = len(input_str) // 2
   return input_str[middle_index - 1:middle_index + 2]
# Test cases
str1 = "JhonDipPeta"
str2 = "JaSonAy"
result1 = get_middle_three_chars(str1)
result2 = get_middle_three_chars(str2)
print(f"str1 = '{str1}' -> Expected Result = '{result1}'")
print(f"str2 = '{str2}' -> Expected Result = '{result2}'")