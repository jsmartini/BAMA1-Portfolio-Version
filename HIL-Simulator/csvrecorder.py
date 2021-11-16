import csv

fname = "test.csv"
f = open(fname, "w")

header = ["X", "Y", "Z" ,"Vx", "Vy", "Vz", "q1", "q2", "q3", "q4", "P", "Q", "R"]

writer =csv.writer(f)

writer.writerow(header)

recorder = lambda row: writer.writerow(row)
