import re
import csv

def process_line(line):
    # Удаляем запятые внутри кавычек и убираем кавычки
    return re.sub(r'"([^"]*)"', lambda m: m.group(1).replace(',', ''), line)

with open('fatsecret.csv', 'r') as infile, open('output.csv', 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    count = 0
    for line in infile:
        processed_line = process_line(line.strip())
        # Разделяем строку на поля по запятым
        fields = processed_line.split(',')
        writer.writerow(fields)
        count += 1
        print(count)
