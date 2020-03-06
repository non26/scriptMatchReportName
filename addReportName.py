import re
import pandas as pd
import copy
# _ADDREPORTNAMEFILE = r"C:\Users\EiCh9001\PycharmProjects\PyNielsen\fromGithub\addReportName\parameter.txt"

_ADDREPORTNAMEFILE = r"C:\nonContent\addReportName\parameter.txt"
parameter = r"C:\nonContent\addReportName\TrendCheck_UAT.xlsx"

def splitClient(file):
    listLine = []  # list of client
    listClient = []  # list of client's detail
    with open(file, "r") as infile:
        for line in infile:
            if line != "\n":
                listLine.append(line.strip())
                continue
            elif listLine:
                listClient.append(listLine.copy())
                listLine = []
                continue
    return listClient

def filterUnfilledReportName(listOfClient: list):
    """
    this filter clients out of report-name-filled clients
    and store the report-name-unfilled clients to the variable "unFilledReportName"
    then store the 'catNo' and 'reportLine' of report-name-unfilled clients to the variable
    "infoClient"
    :param listOfClient :
    :return :
    """
    pair = []  # a pair of two items 'catNo', 'reportLine'
    infoClient = []  # [[catNo,reportLine]]
    filledReportName = [] # filled report name
    unFilledReportName = []  # unfilled report name
    for client in listOfClient:
        catNo = client[0]
        reportName = client[1]
        reportLine = client[2]
        if reportName.find("ReportName") != -1:
            equalSign = reportName.rfind("=")
            semiColon = reportName.rfind(";")
            # if there is no error, indicating that report name is filled
            reportNameString = reportName[equalSign+1:semiColon].strip() # if filled, it'll be null, if not, it'll not null
            if bool(reportNameString):
                filledReportName.append(client)
            else:  # if there is error, indicating that report name is unfilled
                # cat no.
                underscore = catNo.rfind("_")
                semiColon = catNo.rfind(";")
                catNoString = catNo[underscore+1:semiColon].strip()
                pair.append(catNoString)
                # report line
                equalSign = reportLine.rfind("=")
                semiColon = reportLine.rfind(";")
                reportLineString = reportLine[equalSign+1:semiColon].strip()
                pair.append(reportLineString)
                # detail
                unFilledReportName.append(client)
                infoClient.append(pair.copy())
                pair = []
    # for item in unFilledReportName:
    #     print(item)
    # print("*"*20)
    # for item in filledReportName:
    #     print(item)
    # "unFilledReportName" and "infoClient" must have the same length
    return unFilledReportName, infoClient, filledReportName

def matchDBname(fileForMatching, unfilledClient, infoUnfilled):
    """
    unfilledClientName and infoUnfilled must have the same length
    because each element in the infoClient extracted from the unfilledClient
    from the function 'filterUnfilledReportName'
    NOTE: "unfilledClient", "infoUnfilled" must have the same length
    :param fileForMatching: excel file used to match 'ReportName'
    :param unfilledClient: report-name-unfilled client
    :param infoUnfilled: info of 'catNo' and 'reportLine' of  report-name-unfilled client
    :return: "unfilledClient" which is the clients that already filled the reportName
            "keepUnFilledIndex" which is used to keeping the index of unfilled reportName
                                that corresponding to the clients in the unfilledClient
    """
    unfilledClient = copy.deepcopy(unfilledClient)
    newFilledClient = []
    reportName = "Define ReportName="
    _matchReportName = pd.DataFrame(pd.read_excel(fileForMatching))[["CATE_NO", "REPORTNAME", "REPORTLINE"]]
    unFilled = []
    for index, info in enumerate(infoUnfilled):
        catNo = int(info[0])
        groups = _matchReportName.groupby(by="CATE_NO")
        try:
            g = groups.get_group(catNo)
        except KeyError:
            unFilled.append(unfilledClient[index].copy())
            continue
        else:
            try:
                reportLine = int(info[1])
                h = g.groupby(by="REPORTLINE")
                pairCatNoReportLine = h.get_group(reportLine)
            except KeyError:
                unFilled.append(unfilledClient[index].copy())
                continue
            else: # indicate that there is a pair of catNo and reportLine
                if len(pairCatNoReportLine) == 1:
                    indexOfReportName = pairCatNoReportLine.index[0]
                    # dbName = reportName
                    DbName = pairCatNoReportLine.at[indexOfReportName, "REPORTNAME"]
                    reportName += DbName+";"
                    reportName = f"{reportName}"
                    # reposition of info of client lis\t
                    unfilledClient[index][1] = reportName
                    newFilledClient.append(unfilledClient[index].copy())
                    reportName = "Define ReportName="
                else:
                    unFilled.append(unfilledClient[index].copy())
    return newFilledClient, unFilled

def writeToTxt(filledClient, unfilledClient):
    with open("matchingReportName.txt", "w") as inFile:
        # write the clients that already filled the reportName
        for client in filledClient:
            for line in client:
                inFile.write(str(line)+"\n")
            inFile.write("\n")
        # write a separator that stays between the filled reportName and
        # unfilled reportName
        inFile.write("\n")
        inFile.write("#"*200+"\n")
        inFile.write("\n")
        # write the clients that can not be filled due to conflicts
        for client in unfilledClient:
            for line in client:
                inFile.write(str(line)+"\n")
            inFile.write("\n")
if __name__ == "__main__":
    test1 = splitClient(_ADDREPORTNAMEFILE)
    # print(len(test1))
    unfillClient1, info, filledClient1 = filterUnfilledReportName(test1)
    # print(len(unfillClient1), len(filledClient1), len(unfillClient1)+len(filledClient1))
    filledClient2, unfillClient1 = matchDBname(parameter, unfillClient1, info)
    # print(len(filledClient2), len(unfillClient1), len(filledClient2)+len(unfillClient1))
    filledClient1.extend(filledClient2)
    # print(len(filledClient1), len(unfillClient1), len(filledClient1)+len(unfillClient1))
    writeToTxt(filledClient1, unfillClient1)


