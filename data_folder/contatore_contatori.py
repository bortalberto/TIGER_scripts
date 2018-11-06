import GEM_OFFLINE_classes
filename=raw_input("Insert file name:")
contatore =0
microcunter =0
with open(filename, 'r') as f:
    while True:
        linea = f.readline().split()
        # print microcunter
        # print contatore
        if linea[0] == "Contatore_arrivato_a":
            # print "trovo{}, mi aspetto {}".format(linea[1],contatore+1)
            if int(linea [1]) != contatore+1:
                print "\nCounter packet lost\n"
                contatore=contatore+1
            else:
                contatore=contatore+1
            if microcunter!= 20:
                print "\n Filler pack lost\n"
                microcunter =0
            else:
                microcunter =0

        else:
            microcunter=microcunter+1

