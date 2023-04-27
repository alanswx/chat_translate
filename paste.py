import json
import sys
import docx
import openai
import re


def load_json_file(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
        return data


if len(sys.argv) != 2:
    print("Usage: python paste.py <word document>")
    sys.exit(1)

filename = sys.argv[1]
json_filename = filename.split('.')[0] + '.json'


print(filename)
print(json_filename)

# Load the Word document
doc = docx.Document(filename)


translation = load_json_file(json_filename)

records = []
# Open the text file
for record in translation:

    # Get the original text
    original_text = record["orig"]
    chat_output = record["chat_output"]
    # Parse the free-form data structure
    data = {}
    data["ORIGINAL"]=original_text
    data["index"]=record["index"]
    data["nojap"]=record["nojap"]
    lines = chat_output.split("\n")
    print("LINES[")
    print(lines)
    print("]LINES")
    key = None
    value_lines = []
    for line in lines:
            line = line.strip()
            if line:
                if line.startswith("UNKNOWN"):
                    data["UNKNOWN"]="true"
                print(line) 
                if line.count(":") == 1 and line.index(":") > 0 and not " " in line[:line.index(":")]:
                    if key:
                        data[key] = "\n".join(value_lines)
                        value_lines = []
                    key, value = line.split(":", 1)
                    data[key.strip()] = value.strip().lstrip()
                    if (len(value.strip())):
                       value_lines.append(value.strip())
                elif key:
                    value_lines.append(line)

    if key and value_lines:
            data[key] = "\n".join(value_lines)

    records.append(data)
    # Do something with the data
    print("====")
    print(record)
    print("Original Text: ", original_text)
    print("Parsed Data: ", data)
print("-----")
print(records)


translations = {
    "パーソナルコンピュータ": "personal computer",
}

def lookup_translation(phrase, translation_table):
    if phrase in translation_table:
        return translation_table[phrase]
    else:
        return None

count = 0

# Iterate over each paragraph in the document
for para in doc.paragraphs:
  # Extract the text from the paragraph
  text = para.text
  trans = para.text
  if (count < len(records)):
    orig = records[count]["ORIGINAL"]
    if ("CORRECTED_TRANSLATION" in records[count]):
      trans = records[count]["CORRECTED_TRANSLATION"]
    elif ("TRANSLATION" in records[count]):
      trans = records[count]["TRANSLATION"]
    print('count:'+ str(count))
    print('doctext:'+ text)
    if len(text.strip().lstrip())<1:
      continue
    print('orig:'+ orig)
    print('trans:'+trans)
    print("CHECK:")
    print(text==orig)
    print(text,'|',orig)
    print("____")
    newtrans = lookup_translation(trans, translations)
    if (newtrans) :
      print("GOT NEW TRANS")
      trans=newtrans
    if ("CONFIDENCE" in records[count]):
      confidence = records[count]["CONFIDENCE"]
      if (confidence=="0"):
         badtranslation=True
      else:
         print("CONFIDENCE: "+confidence)
    if ("UNKNOWN" in records[count]):
      badtranslation = True
    if ("Unknown" in records[count]):
      badtranslation = True
    badtranslation = False
    if len(orig) == 0:
      badtranslation = True
    #if len(records[count].original) and len(records[count].original) < 15  and len(records[count].translated) / len(records[count].original)  > 5:
    #  print("SIZE??")
    #  badtranslation = True
 
    if badtranslation == False:
      print("DOSUB")
      para.text = trans

  else:
    print("problem")
    print(count)
  count = count + 1

 

doc.save('NEW.docx')
 
