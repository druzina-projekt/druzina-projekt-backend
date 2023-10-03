import re

text_1 = "58In poklicali so Rebeko in ji rekli: »Ali hočeš iti s tem možem?«"
text_2 = "Rekla je: »Pojdem.« 59Odpustili so torej svojo sestro Rebeko, njeno do-"
text_3 = "jiljo, Abrahamovega hlapca in njegove može. 60Blagoslovili so Rebeko"
text_4 = "in ji rekli:"

parts = re.split(r'(?<=[.?!«»])\s|(?<=[.?!«»])\d', text_2)

print(parts)

# text = "Ketúrini sinovi (//1 Krn 1,32-33)"
# text_2 = "Abrahamova smrt"
#
# clean_text = re.sub(r'\([^)]*\)', '', text_2)
#
# print(clean_text.strip())

# text = "583232323In poklicali so Rebeko in ji rekli: »Ali hočeš iti s tem možem?«"
# match = re.match(r'(\d+)(.*)', text)
#
# if match:
#     number, rest_of_text = match.groups()
#     result = {
#         "Number": number,
#         "Rest of the text": rest_of_text
#     }
# else:
#     result = "No number found at the beginning of the text."
#
# print(result)
