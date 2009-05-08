def alterfile():
    f = open('out', 'r')
    o = open('disc_graph', 'w')
    o.write('# trav wait cost\n')
    for line in f:
        if line.startswith('['):
            o.write(line.replace(',', '').replace('[', '').replace(']', ''))
    f.close()
    o.close()


if __name__ == "__main__":	
	alterfile()
