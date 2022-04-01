import json
import sys
import re

def parseFile (f):
    d = json.load(f)
    regex=r'(test: \(group(.*\n)+)Run status'
    regex1=re.compile('SC=(.*) fio_pods=(.*)')
    #print(d['stdout'])
    for line in d['stdout'].split('\n'):
        t = re.search(regex1,line)
     #   print(t)
        if t == None : 
            continue
        sc,pods = t.groups()    
        print('\nstorage_class={} \nfio_pods={}\n'.format(sc,pods))
    
    m = re.search(regex,d['stdout'],re.MULTILINE)
    print('{}'.format(m.group(1)))

for fname in sys.argv[1:]:
#    print(fname)
    with open(fname,'r') as f:
        parseFile(f)
