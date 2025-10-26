"""
This python file uses the JSON file of functions, and generates a dataset represented by a pkl file
Each item in the dataset consists of the function name, java 8 function and java 11 function
Each java 8 function and java 11 function consists of the function name, source code string and function length
"""
import pickle, os
import json

def store_pickle(array, filepath):
    """
    Function to store an array as a .pkl file
    :param array: Python Array of data to serialize
    :param filepath: File path to store the serialized array at, including the file extension (.pkl)
    :return: None
    """
    if os.path.exists(filepath):
        # Delete the pkl file if it already exists
        print("Deleting " + filepath + " as it already exists")
        os.remove(filepath)
    with open(filepath, "wb") as my_file:
        # Store the array to the pkl file
        pickle.dump(array, my_file)
        print("Stored Dataset to: " + filepath)


def generate_dataset_from_json(filepath):
    """
    Function to generate a dataset pkl from a JSON file
    Each data item in the dataset is a dictionary with the function name and a Java 8 and 11 implementation
    :param filepath: Filepath to the JSON file containing the dataset
    :return: Array representation of the dataset
    """
    print("Generating dataset from JSON file")

    # Instantiate an empty array to hold the dataset as it is being built
    dataset = []

    # Open the JSON file
    with open(filepath, "r", encoding="utf-8") as jsonfile:
        # Load the JSON file into the 'data' variable
        data = json.load(jsonfile)

        # Iterate over each item in the JSON file
        for entry in data:
            # Create the java_8_function dictionary
            java_8_function = {
                # Get the function name, function string, and calculate the function length
                'name': entry['name'],
                'string': entry['java8'],
                'length': len(entry['java8'].split('\n'))
            }
            # Create the java_11_function dictionary
            java_11_function = {
                # Get the function name, function string, and calculate the function length
                'name': entry['name'],
                'string': entry['java11'],
                'length': len(entry['java11'].split('\n'))
            }
            # Create the data item itself using the java_8_function and java_11_function
            res = {
                'name': entry['name'],
                'java_8_function': java_8_function,
                'java_11_function': java_11_function
            }
            # Store the data item into the dataset
            dataset.append(res)

    # Return the array representation of the dataset
    return dataset


if __name__ == "__main__":
    print("Started build_secondary_dataset.py")
    dataset = generate_dataset_from_json("secondary_functions.json")
    store_pickle(dataset, "./../Shared_Files/secondary_dataset.pkl")
