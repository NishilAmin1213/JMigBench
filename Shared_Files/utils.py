import os, pickle

def read_dataset(filepath, silent=True):
    if os.path.exists(filepath):
        # If the pickle exists, extract the array of function_pairs
        dataset = pickle.load(open(filepath, "rb"))
        if not silent:
            print("Loaded " + str(len(dataset)) + " data items from " + filepath)
        return dataset
    else:
        print(filepath + " does not exist")
        quit(1)