import docx
import openai
import re
import json
import sys

def truncate_string(s):
    if len(s) > 500:
        truncated = s[-300:]
        last_space_idx = truncated.find(' ')
        if last_space_idx != -1 and last_space_idx < len(truncated) - 1:
            truncated = truncated[last_space_idx + 1:]
        return truncated
    else:
        return s




if len(sys.argv) != 2:
    print("Usage: python translate.py <word document>")
    sys.exit(1)

filename = sys.argv[1]
#output_filename = filename.split('.')[0] + '_translate.' + filename.split('.')[1]
output_filename = filename.split('.')[0] + '.json'


print(filename)
print(output_filename)

# Load the Word document
doc = docx.Document(filename)
# Authenticate to OpenAI API
with open("openapi.key", 'r') as f:
        lines = f.readlines()
openai.api_key=lines[0].strip().lstrip()

para_count = 0


prev = ""

tr_output = []

# Open a file for writing the translated text
with open("translated.txt", "w", encoding="utf-8") as f:
    
    # Iterate over each paragraph in the document
    for para in doc.paragraphs:
    
        # Extract the text from the paragraph
        text = para.text

        # Clean the text by removing unwanted characters
        text = re.sub(r'[^\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\uFF00-\uFFEF\u4E00-\u9FAF\w\s]','',text)
        noJapanese = True
        # Use regular expression to check for Japanese characters
        if re.search("[\u3040-\u309f\u30a0-\u30ff\u3005-\u3006\u30e0-\u9fcf]", text):
           noJapanese = False
        else:
           noJapanese = True


        entry = {}
        entry["index"]=para_count
        entry["orig"]=text
        entry["nojap"]=noJapanese
        print("---\r\n")
        print(len(text))
        print(noJapanese)
        print(text)
        f.write("\n---\n"+para.text+"\n")
        if (len(text)>0 and noJapanese==False):
          # Translate the text from Japanese to English using the OpenAI API
          prompt=f"""You are an AI whose job it is to produce the best translation from some
OCR text_to_translate from a 1980s era Japanese microcomputer manual. To help you,
you have previous_text which is the OCR output of the text that came
before the text_to_translate.

Do the following:

1. Look at the input OCR-generated text_to_translate
2. Determine if text_to_translate makes sense given being from a
microcomputer user manual, if so output the translation of
text_to_translate in a section TRANSLATION, jump to step 5
3. If text_text_to_translate does not make sense due to possible OCR
errors, then attempt to correct for the OCR errors and output the
translation of the corrected text_to_translate in a section
CORRECTED_TRANSLATION, jump to step 5
4. Output UNKNOWN
5. Generate an output block CONFIDENCE containing an estimate between 0
and 10 of he liklihood that the translation is the correct of the
original Japanese text before OCR where 0 means very low likelihood and
10 meaning high likelihood.

text_to_translate: text:
{text}


previous_text:
{prev}
"""
          prev = prev + ' ' + text 
          prev = truncate_string(prev)

          print(prompt)
          translation = openai.ChatCompletion.create(
          #    engine="text-davinci-002",
          #     model="gpt-4",
               model="gpt-3.5-turbo",
          #    engine="text-davinci-003",
          #    engine="text-davinci-002",
              messages=[{"role": "user", "content": prompt}],
              max_tokens=1024,
              n=1,
              top_p=1,
              frequency_penalty=0,
              presence_penalty=0,
              stop=None,
              temperature=0.00,
          )

          # Get the translated text
          print(translation)
          translated_text = translation["choices"][0]["message"]["content"]
          print(translated_text)

          #translated_text = translation.choices[0].text.strip()

          # Write the translated text to the file
          entry["prompt"]=prompt
          entry["chat_output"]=translated_text
          tr_output.append(entry)
          f.write(translated_text + "\n")
          para_count = para_count + 1
          #if (para_count>5):
          #   exit()
          #exit()
with open(output_filename, 'w') as f:
    json.dump(tr_output, f)
