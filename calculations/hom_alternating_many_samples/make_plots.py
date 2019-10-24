
def read_data(filename:str):
    result = dict()
    with open(filename, 'r') as file:
        for line in file:
            if 'names' in line:
                continue
            if 'end' in line:
                break
            tmp = line.split('\t\t')
            state = tmp[0]
            count = tmp[1]
            result[state] = int(count)
    return result

def get_filenames():
    result = []
    for S in [0,1]:
        for qpm in [2,3]:
                    for trotter_steps in [1,2,5]:
                        tmp = {"S":S, "qpm":qpm, "trotter_steps":trotter_steps}
                        filename="hom_S_"+str(S)+"_qpm_"+str(qpm)+"_steps_" + str(trotter_steps)+"_alternating_1"
                        tmp["filename"]=filename
                        result.append(tmp)
    return result

def mask_data(data:dict, valid_keys:list = ["|2>_a|0>_b","|0>_a|2>_b", "|020>_a|000>_b", "|000>_a|020>_b"]):
    masked_data = dict()
    masked_data['invalid']=0
    for k, v in data.items():
        if k in valid_keys:
            masked_data[k]=v
        else:
            masked_data['invalid']+=v
    return masked_data

if __name__ == "__main__":
    
    filenames = get_filenames()
    for f in filenames:
        try:
            data = read_data(filename=f['filename']+".pdf_data")
        except:
            print("filename=", f['filename']+".pdf_data", " not found")
            continue
        label=""
        for k,v in f.items():
            if k == "filename": 
                continue
            label+= str(k)+"="+str(v)+"\n"
        
        from matplotlib import pyplot as plt
        plt.ylabel("counts")
        plt.xlabel("state")
        plt.ylim(0,500)
        masked_data = mask_data(data)
        names = [k for k in masked_data.keys()]
        values = [v for v in masked_data.values()]
        print("label=", label)
        print("names=", names, "\nvalues=", values)
        plt.bar(names, values, label=label)
        plt.legend()
        plt.savefig(fname=f['filename']+".pdf")
        plt.cla()



