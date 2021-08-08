print('orderConverter')
oldFileLines = []
newFileLines = []
with open('orders - Backup.txt') as f:
    oldFileLines = f.readlines()
    for line in oldFileLines:
        print()
        newLine = '{"name": "' + line + '","defaultWeight": 0.5, "weightOffset":, 0}'
        newFileLines.append(newLine + ',\n')
    f.close()

with open('orders - Backup.txt', 'w') as f:
    f.writelines(newFileLines)
    f.close()