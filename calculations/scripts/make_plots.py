import glob

def read_data(filename:str):
    result = dict()
    with open(filename, 'r') as file:
        for line in file:
            if 'names' in line:
                continue
            if 'end' in line:
                break
            tmp = line.split('\t')
            state = tmp[0]
            count = tmp[1]
            result[state] = int(count)
    return result

def get_filenames():
    filenames=glob.glob("*.pdf_data")
    return filenames

def mask_data(data:dict, valid_keys:list = ["|2>_a|0>_b","|0>_a|2>_b", "|020>_a|000>_b", "|000>_a|020>_b", "1000", "0010"]):
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
    #print("filenames:\n", filenames)
    for f in filenames:
        try:
            data = read_data(filename=f)
        except:
            print("filename=", f, " not found")
            continue
        
        from matplotlib import pyplot as plt
        plt.ylabel("counts")
        plt.xlabel("state")
        plt.ylim(0,1000)
        masked_data = mask_data(data)
        names = [k for k in masked_data.keys()]
        values = [v for v in masked_data.values()]
        plt.bar(names, values)
        fout = f.split(".")[0]+".pdf"
        plt.savefig(fname=fout)
        plt.cla()



