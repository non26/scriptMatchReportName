reportName = 'Define ReportName=RM00407;'
equalSign = reportName.rfind("=")
semiColon = reportName.rfind(";")
# if there is no error, indicating that report name is filled
reportNameString = reportName[equalSign+1:semiColon].strip()
print(reportNameString)