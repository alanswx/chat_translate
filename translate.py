import docx
import openai
import re
import json

def truncate_string(s):
    if len(s) > 500:
        truncated = s[-300:]
        last_space_idx = truncated.rfind(' ')
        if last_space_idx != -1 and last_space_idx < len(truncated) - 1:
            truncated = '...' + truncated[last_space_idx + 1:]
        return truncated
    else:
        return s

# Load the Word document
doc = docx.Document("docs/page_066_do.docx");
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
          prompt=f"""Below is a set of Japanese text generated from an OCR of a manual for a
1980s era microcomputer. The goal is to create a usable translation to help
developers who cannot read Japanese. 

Do the following:
1. Look at the input OCR-generated text
2. Determine if it makes sense given being from a microcomputer user manual
3. If the text makes sense, does not likely contain OCR errors, please
produce output of a section TRANSLATION followed by the translation and
jump to step 6
4. If the text does not make sense or likely contains OCR errors, and it
is possible to predict the original text, then try to guess the likely
original text and output CORRECTED_TEXT followed by a guess of the
corrected text and CORRECTED_TRANSLATION followed by the corrected
translation. Then jump to step 6.
5. Output UNKNOWN
6. Generate an output block CONFIDENCE where you estimate the liklihood
that the translation is the correct of the original Japanese text before
OCR where 0 means very low likelihood and 10 meaning high likelihood.

previous text:
{prev}

text:
{text}
"""
          #prompt=f"Translate the following text about the Japanese FM-7 computer into English: {text}"
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

          #translated_text = translation.choices[0].text.strip()

          # Write the translated text to the file
          entry["chat_output"]=translated_text
          tr_output.append(entry)
          f.write(translated_text + "\n")
          para_count = para_count + 1
          #if (para_count>5):
          #   exit()
          #exit()
with open('translated.json', 'w') as f:
    json.dump(tr_output, f)
