import sys
import docx

if len(sys.argv) != 2:
    print("Usage: python tables.py <word document>")
    sys.exit(1)

filename = sys.argv[1]
#output_filename = filename.split('.')[0] + '_translate.' + filename.split('.')[1]
output_filename = filename.split('.')[0] + '.json'


print(filename)
print(output_filename)

# Load the Word document
doc = docx.Document(filename)



# Iterate through the tables in the document
for table in doc.tables:
    print("==============")
    # Create an empty Markdown table string
    markdown_table = ''

    # Iterate through the rows of the table
    for i, row in enumerate(table.rows):
        # Iterate through the cells of the row
        for j, cell in enumerate(row.cells):
            # Get the text inside the cell
            text = cell.text
            # Replace any '|' characters with '\|' to avoid markdown formatting issues
            text = text.replace('|', '\|')
            # Add the cell text to the Markdown table string
            markdown_table += f'|{text.strip()}'
        # Add a newline character to end the row
        markdown_table += '|\n'

        # Add a separator row after the first row
        if i == 0:
            markdown_table += '|'
            for j in range(len(row.cells)):
                markdown_table += '---|'
            markdown_table += '\n'

    # Print the Markdown table string
    print(markdown_table)

