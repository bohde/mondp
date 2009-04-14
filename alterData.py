def alterfile():
    f = open('outres', 'r')
    o = open('out2', 'w')
    o.write('# trav wait cost\n')
    for line in f:
        if line.startswith('['):
            o.write(line.replace(',', '').replace('[', '').replace(']', ''))
    f.close()
    o.close()