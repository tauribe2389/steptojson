import json
import re
import sys

class StepToJson:

    jsonData = {}
    stepFile = ""

    # Function      : def __init__(self, stepFile):
    # Author        : Tristan Uribe
    # Date          : 8/16/2020
    # Description   : Constructor function that defines the STEP file and sections data will be sorted into.
    # Return        : N/A

    def __init__(self, stepFile):
		self.stepFile = stepFile
		self.jsonData['header'] = []
		self.jsonData['data']  = []

    # Function      : def appendJSON(self, jsonObj, attribute, value):
    # Author        : Tristan Uribe
    # Date          : 8/16/2020
    # Description   : Function that handles adding data into the 'header' and 'data' sections.
    # Return        : Returns the object with the newly added data.

    def appendJSON(self, jsonObj, attribute, type, value):
		if not attribute or not type:
			jsonObj.append([attribute, value])
		else:
			jsonObj.append([attribute, type, value])

		return jsonObj

    # Function      : def jsonWrite(self, fileName):
    # Author        : Tristan Uribe
    # Date          : 8/16/2020
    # Description   : Function that creates JSON file and then dumps collected data to the created file.
    # Return        : N/A

    def jsonWrite(self, fileName):
		with open(fileName, 'w') as outfile:
			json.dump(self.jsonData, outfile)

    # Function      : def sortValue(self, value, lines):
    # Author        : Tristan Uribe
    # Date          : 8/18/2020
    # Description   : Function that removes numeral references in lines and replaces them with the referenced CAD entity
    # Return        : Returns line with numeral references replaced with string of CAD entities

    def sortValue(self, value, lines):
        ref = re.findall("\#\d+", value) # Need to find at the end of the last numeric digit
        refString = ""

        if ref:
            for i in ref:
                for line in lines:
                    refString = re.split("\s=\s?", line)
                    if re.match(i,refString[0]):
                        value = value.replace(i,refString[1])

        return value

    # Function      : def parse(self):
    # Author        : Tristan Uribe
    # Date          : 8/16/2020
    # Description   : Function that parses data from CAD STEP files with format AP214.
    #                 All lines are combined into a single line and then resplit to remove spacing that could cause an error.
    #                 If statements with booleans are used to identify what section the CAD entity is from (header or data) and if it should be added to the JSON file.
    #                 In the data section complex entities are broken into individual entities.
    #                 Each line in the data section is then broken into its entity name, type, and then full entity with local numerical references removed.
    #                 Each line in the header section is broken into its entity name, and then the full entity.
    # Return        : N/A

    def parse(self):
        collect = False
        section = ""
        dataArray = ""
        stringArray = ""
        primeEntity = ""
        entityType = ""
        complexEntity = ""
        parseLines = []
        lines = []
        reg = re.compile("#")

        with open(self.stepFile,"r") as CAD_file:
            CAD_file = CAD_file.read().replace("\n","").replace("\t","")
            parseLines = CAD_file.split(";")
            lines = map(lambda line: line+";", parseLines)

        for line in lines:

            if (line == "DATA;"):
                section = "data"
                collect = True
                continue

            if (line == "HEADER;"):
                section = "header"
                collect = True
                continue

            if (line == "ENDSEC;"):
                collect = False

            if (collect and section == "data"):
                dataArray = re.split("\s=\s?", line)
                value = dataArray[1]
                value = value.replace(" ","")

                if (value[0] == "(" and value[-2] == ")"):
                    value = value[1:-2]
                    complexEntity = re.split(r"[/):]", value)

                    for entity in complexEntity:
                        if entity:
                            entity = entity+")"
                            lines.append(entity)

                    continue

                while reg.search(value) is not None:
                    value = self.sortValue(value, parseLines)

                stringArray = re.split("^(.*?)\(", value)

                primeEntity = stringArray[1]

                if re.search("'(.*?)'", value):
                    entityType = re.search("'(.*?)'", value).group(1)

                if not entityType:
                    entityType = "N/A"

                self.appendJSON(self.jsonData[section], primeEntity, entityType, value)

            if (collect and section == "header"):
                value = line
                value = value.replace(" ","")
                stringArray = re.split("^(.*?)\(", value)
                primeEntity = stringArray[1]
                entityType = None

                self.appendJSON(self.jsonData[section], primeEntity, entityType, value)

        self.jsonWrite('data.json')
