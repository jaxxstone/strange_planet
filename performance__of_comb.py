from itertools import combinations
from itertools import combinations_with_replacement
import time
from datetime import timedelta
import csv

#n = int(input ("Enter the total number of individuals: ")) # number of people
m = int(input("Enter the number of species: ")) # number of groups
iter_no = 100

with open('performance.csv', 'w') as csvfile:
    filewriter = csv.writer(csvfile, delimiter=' ',
                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for n in range(100):
        for iter in range (iter_no):
            exec_time = 0.0
        #    start = time.process_time()
            start = time.clock()
            lst = range(n, -1, -1)
            alist = []
            # need to replace the following 5 lines with the iterative construct as further below
            # complexity of python comb_with_repl is O(r * (n! / (r! (n - r)!))), discussed at the link below
            # see: http://stackoverflow.com/questions/20764926/combinations-without-using-itertools-combinations
            for comb in combinations_with_replacement(lst,m):
                if sum(comb) == n:
                    alist.append(comb)        
            #print (alist)
            total_combinations = len(alist)
            end = time.clock()
            exec_time = exec_time + (end - start)
    #       exec_time = time.process_time() - start # in seconds
        exec_time = exec_time/iter_no
        filewriter.writerow([n, total_combinations, exec_time])    
        print ("i = " + str(n) + " # of comb: " + str(total_combinations) + " Time: " + str(exec_time) )
    #    print(timedelta(seconds=exec_time))
