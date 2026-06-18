import requests
import sys
# URL of the RFC file
url = 'https://www.rfc-editor.org/rfc/rfc4120.txt'
# url = 'https://www.rfc-editor.org/rfc/rfc4121.txt'

# Fetch the file content from the URL
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Get the text content from the response
text = response.text

# Replace every combination of three spaces on the left with a TAB
# Split the content into lines
lines = text.splitlines()

# Process each line
processed_lines = []
NewParagraph = ''
count = 1
prevline = Header = False
for lineno, line in enumerate(lines):
    Header = False
    if line.startswith("Neuman") or line.startswith("RFC 4120") or len(line) < 1:
        continue

    if "Status of This Memo" in line:
        print(lineno, line)
        processed_lines.append(line)
        prevline = line
        continue

    if not prevline:
        processed_lines.append(line)
        print("not prevline", lineno, line)
        continue

    if len(line.lstrip().rstrip()) == 0:
        if len(NewParagraph) > 0:
            #print("#1 NewParagraph")
            processed_lines.append("\n"+NewParagraph.lstrip())
            NewParagraph = ''

    first_char = line[0]
    # print("first_char", lineno, "|"+first_char+"|", line)
    if first_char.isupper():
        print("Is Upper #1", lineno, line)
        Header = True
        processed_lines.append("\n"+NewParagraph)
        NewParagraph = ''        
        processed_lines.append("\n"+line+" ")
    elif first_char.isdigit():
        processed_lines.append("\n"+NewParagraph.lstrip())
        NewParagraph = ''         
        print("Is digit #1", lineno, line)
        processed_lines.append("\n"+line)
    elif first_char.islower():
        print("Is Lower #1", lineno, line)
        NewParagraph = NewParagraph + rstripline
    elif "}" in first_char or "{" in first_char  or "-" in first_char or "(" in first_char or ")" in first_char or '"' in first_char or "'" in first_char :
        print("Is Chars #1", lineno, line)
        NewParagraph = NewParagraph + rstripline  
    elif line[0:3] == '   ':
        rstripline = line.lstrip().replace("\r", " ").replace("\n", " ").replace("\t", "").replace("  ", " ")
        if len(rstripline) < 1:
            print("Escape #1:", lineno, "|"+rstripline+"|", line)
            continue

        first_char = line[0]  # Get the first character
        # print("first_char", lineno, len(first_char), line)
        if " " in first_char:
            # print("Is Space #1", lineno, line)
            first_char = rstripline[0]
            if first_char.isupper():
                if Header == True:
                    print("Is Upper #2.a", lineno, rstripline)
                    processed_lines.append("\n"+NewParagraph.lstrip())
                    NewParagraph = ''
                    processed_lines.append("\n"+rstripline+" ")
                else:
                    if "." in prevline[-1]:
                        print("Is Upper #2.b", lineno, rstripline)
                        processed_lines.append("\n"+NewParagraph.lstrip())
                        NewParagraph = ''
                        NewParagraph = NewParagraph + " "+ rstripline
                    elif first_char+"." in rstripline:
                        print("Is Upper #2.c", lineno, rstripline)
                        processed_lines.append(rstripline)
                    elif prevline[-1].isdigit() and "..." in prevline:
                        print("Is Upper #2.d", lineno, rstripline)
                        processed_lines.append(rstripline)
                    else:
                        print("Is Upper #2.e", lineno, rstripline)
                        NewParagraph = NewParagraph + " "+ rstripline

            elif first_char.isdigit():
                print("Is digit #2", lineno, rstripline)
                processed_lines.append(rstripline)
            elif first_char.islower():
                print("Is Lower #2", lineno, rstripline)
                NewParagraph = NewParagraph + " "+ rstripline
            elif "}" in first_char or "{" in first_char  or "-" in first_char or "(" in first_char or ")" in first_char or '"' in first_char or "'" in first_char :
                print("Is Chars #2", lineno, rstripline)
                NewParagraph = NewParagraph + " "+ rstripline
            else:
               print("Escaped #2:", lineno, "|"+first_char+"|", rstripline) 

        elif first_char.isupper():
            print("Is Upper #3", lineno, line)
            processed_lines.append("\n"+line+" ")
        elif first_char.isdigit():
            print("Is digit #3", lineno, line)
            processed_lines.append(line)        
        elif first_char.islower():
            print("Is Lower #3", lineno, line)
            NewParagraph = NewParagraph + " " + line
        elif "}" in first_char or "{" in first_char  or "-" in first_char or "(" in first_char or ")" in first_char or '"' in first_char or "'" in first_char :
            print("Is Chars #3", lineno, line)
            NewParagraph = NewParagraph + " " + line
        else:
           print("Escaped #3:", lineno, "|"+first_char+"|", line)            
            
        # NewParagraph = NewParagraph + line
    else:
       print("Escaped #3:", lineno, "|"+first_char+"|", line)


    prevline = line

    count += 1
    # if count > 200:
    # if "There is one exception to this rule." in line:
    #    break

print("-" * 50)
output = "formated.txt"
open(output, "w").close()

with open(output, "a+") as outf: 
    for line in processed_lines:
        outf.write(line+"\n")