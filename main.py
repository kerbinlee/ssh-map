import re

if __name__ == "__main__":
    with open('auth.log','r') as file:
        failedPattern = re.compile('Failed password for .* from [0-9]*[.][0-9]*[.][0-9]*[.][0-9]* ')
        ipPattern = re.compile('[0-9]*[.][0-9]*[.][0-9]*[.][0-9]*')

        for line in file:
            lineResult = failedPattern.search(line)
            if lineResult != None:
                print(ipPattern.search(lineResult.group(0)).group(0))
