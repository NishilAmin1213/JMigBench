import os
import javalang
import base64
import time, random, pickle, sys
from web_scraping_utils import make_request
from tqdm import tqdm

def read_candidate_functions(filepath):
    """
    function to deserialize the candidate functions pkl file
    :param filepath: Path to the pickle file to read
    :return: The deserialized candidate functions array
    """
    if os.path.exists(filepath):
        # If the pickle exists, extract the array of repository names
        print("Reading stored candidate functions")
        candidate_functions = pickle.load(open(filepath, "rb"))
        print("Loaded " + str(len(candidate_functions)) + " candidate functions")
        return candidate_functions
    else:
        print(filepath + " does not exist")
        quit(1)


def store_candidate_functions(candidate_functions, filepath):
    """
    Function to serialize the candidate functions array to a pkl file
    :param candidate_functions: array to serialize
    :param filepath: filepath to store the array to
    :return: None
    """
    # Store the array into candidate_functions.pkl, deleting the file if it already exists
    if os.path.exists(filepath):
        print("Deleting " + filepath + " as it already exists")
        os.remove(filepath)
    with open(filepath, "wb") as my_file:
        pickle.dump(candidate_functions, my_file)
        print("Stored candidate functions to " + filepath)


def convert_URL_for_API(standard_URL):
    """
    Function to take a standard UCL and convert it to an API compatible URL
    :param standard_URL: string representation of the URL
    :return: String representation of the API compatible URL
    """
    # Example Original - https://github.com/jenkinsci/jenkins/tree/stable-2.346
    # Example API URL  - https://api.github.com/repos/jenkinsci/jenkins/branches/stable-2.346

    # Extract the repository owner, name and branch
    branch = standard_URL.split("/")[-1]
    owner = standard_URL.split("/")[3]
    name = standard_URL.split("/")[4]

    # Build and return the API compatible URL
    return "https://api.github.com/repos/" + owner + "/" + name + "/branches/" + branch


def find_java_files(repo_url):
    """
    Function to locate java files within a repository
    :param repo_url: URL of the repository to search
    :return: Array of java files where each file is represented by a dictionary
    """
    # Get the sha of the branch
    response_json = utils.make_request(repo_url + "?recursive=1").json()
    sha = response_json['commit']['sha']

    # Use the sha to get the tree representation of the branch
    tree_url = repo_url[:repo_url.find("branches/")] + "git/trees/" + sha + "?recursive=1"
    tree_response = make_request(tree_url)
    tree_json = tree_response.json()

    # Initialise an array to store java files
    java_files = []

    # Iterate through each node of the tree and add java files to the 'java_files' array
    for node in tree_json['tree']:
        if (node['type'] == 'blob') and (node['path'].split(".")[-1] == 'java'):
            java_files.append(node)

    # Return the array of java files (each file is represented by a dictionary)
    return java_files


def find_common_files(files_to_search, reference_files):
    """
    Function to compare two repositored (or two branches) and find common files
    :param files_to_search: The repository to find files in
    :param reference_files: The reference repository to compare files with
    :return: array of common files (where each file is a dictionary)
    """
    res = []
    removed = []

    # Iterate over each file in the repo we are filtering
    # Search for each file in the reference repo
    # If the file exists in both, place it in 'res', if not, place it in 'removed'
    for file in files_to_search:
        path = file['path']

        found = False
        for item in reference_files:
            if item['path'] == path:
                found = True

        if found:
            res.append(file)
        else:
            removed.append(file)

    return res


def combine_modified_java_files(java_8_files, java_11_files):
    """
    Function to combine the modified java files into a single file - essentially creating one dictionary from two dictionaries
    where the java 8 and java 11 file URL are held.
    :param java_8_files: array of java 8 files (array of dictionaries)
    :param java_11_files: array of java 11 files (array of dictionaries)
    :return: array of combined file dictionaries
    """
    combined_files = []

    for file in java_8_files:
        # find file in the java_11_files array
        for item in java_11_files:
            if item['path'] == file['path']:
                # Check if the URL points to the same blob
                if file['url'] != item['url']:
                    # Append a dictionary if the file path, java 8 url and java 11 url to the combined files array
                    combined_files.append({'path': item['path'], 'java_8_url': file['url'], 'java_11_url': item['url']})

    return combined_files


def get_java_source_code(url):
    """
    Function to get the java source code from a file URL
    :param url: URL to retrieve the source code from
    :return: String representation of the source code
    """
    response_json = make_request(url).json()
    content = base64.b64decode(response_json['content']).decode('utf-8')
    return content


def remove_relative_indentation(source_code_string):
    """
    Function to remove any relative indentation from a java function
    :param source_code_string: The string representation of the function to remove indentations from
    :return: A function which starts with no indentation
    """
    # Split the string into lines
    lines = source_code_string.split("\n")

    # For the first line, find how many spaces it has been indented by
    offset = len(lines[0]) - len(lines[0].lstrip(" "))

    # Return the original string if there is no offset
    if offset == 0:
        return source_code_string

    # Connect the lines together, removing the offset spaces from the beginning and placing the newline back
    unindented_string = ""
    for line in lines:
        unindented_string += line[offset:]
        unindented_string += "\n"

    # Return the unindented string
    return unindented_string


def remove_function(source_code, start):
    """
    Function to remove a function from an entire java files source code
    :param source_code: Source code string for an entire java file
    :param start: The start line of the function to extract
    :return: String representation if a single java function
    """
    # instantiate an empty string to represent the result
    res_string = ""
    # Split the input string by \n to isolate lines
    all_lines = source_code.split("\n")
    # Cut out any code from before the function start
    function_onwards = all_lines[start:]

    # Count curly braces and build the res string to hold any code within the function
    brace_counter = 0
    line_counter = 0
    for line in function_onwards:
        res_string = res_string + line + "\n"
        brace_counter += line.count('{')
        brace_counter -= line.count('}')
        line_counter += 1

        if brace_counter == 0:
            break

    # Remove relative string indentation so the function starts with no indentation and the other lines are adjusted accordingly
    res_string = remove_relative_indentation(res_string)

    # Return the number of lines and the function string
    return line_counter, res_string


def extract_function_parameters(function_string):
    """
    Function to extract function parameters from a java function
    :param function_string: String representation of a java function
    :return: Array of strings where each string is an imput parameter
    """
    # Split the function into lines
    function_lines = function_string.split("\n")
    # Initialise a default string to represent parameters
    parameters = ""

    # Find the line with first opening curly bracket
    # Until we find the opening curly bracket, concatenate the line to the parameters string
    for line in function_lines:
        parameters = parameters + "\n" + line
        if "{" in line:
            break

    # split the parameters string by the opening curly brace, and remove the item at index 0
    # This is the string containing the input parameters
    parameters = parameters.split("{")[0]

    # Get the contents inside the '(' and ')' and also split it by the ', '
    # This isolates the function parameters
    parameters = parameters[parameters.find("(")+1:parameters.find(")")]
    parameters = parameters.split(", ")
    if parameters == ['']:
        return []

    # Return what is now an array of parameters
    return parameters


def extract_functions(source_code, url, min_length):
    """
    Function to extract ALL functions from a java function
    :param source_code: Java source code string for an entire java file
    :param url: URL to access the java file (used when building individual functions represented by a dictionary)
    :param min_length: The minimum length of functions to extract
    :return: An array of functions from a java file
    """
    # Initialise an empty array to store functions to
    res_functions = []

    # Identify all methods in the file and store the method node instances in the 'methods' array
    tree = javalang.parse.parse(source_code)
    methods = []
    for path, node in tree:
        if type(node) == javalang.tree.MethodDeclaration:
            methods.append(node)

    # For each method, use the function start and extract the body by counting the '{' and '}'
    for node in methods:
        # Get the function name and start line
        function_start = node.position.line - 1

        # Extract the function body
        function_len, function_string = remove_function(source_code, function_start)

        # Skip the loop if the function is not of a minimum length
        if function_len < min_length:
            continue

        # Extract the function parameters
        function_parameters = extract_function_parameters(function_string)

        # Append a dictionary representation of the function to the array
        res_functions.append({"name":node.name, "length": function_len, "string": function_string, "url": url, "params": function_parameters})

    # Return the array of functions from the file
    return res_functions


def check_for_deprecations(java_function_string):
    """
    Function to check if a java function contains deprecated code
    :param java_function_string: Java function string to check for deprecations
    :return: Boolean - True when the function contains something that was deprecated, False otherwise
    """
    deprecated_search_terms = [
        "JAXBContext", "Marshaller", "Unmarshaller", "DatatypeConverter",
        "WebService", "SOAPBinding", "BindingProvider", "WebServiceClient",
        "DataHandler", "FileDataSource", "CommandMap", "MailcapCommandMap",
        "NamingContextExt", "PortableRemoteObject",
        "UserTransaction", "TransactionManager", "XAResource",
        "javapackager", "wsimport", "wsgen", "xjc", "schemagen",
        "NashornScriptEngineFactory", "ScriptObjectMirror", "NashornScriptEngine", "schemagen",
        "Pack200.newPacker(", "Pack200.newUnpacker("
    ]

    # Set the boolean to false
    found_deprecated_item = False
    # Loop through each item in the predefined array of deprecated terms
    for item in deprecated_search_terms:
        # If the function contains something deprecated, then set the flag to true and stop looping
        if item in java_function_string:
            found_deprecated_item = True
            break

    # Return the boolean value
    return found_deprecated_item


def get_candidate_functions_from_files(file_pair):
    """
    Take a file pair and extract candidate functions from the pair of files
    :param file_pair: Dictionary containing the URL for the java 8 and java 11 file
    :return: An array of dataset candidate functions (An array of dictionaries containing dictionary representations of function pairs)
    """
    # Get the Java 8 and Java 11 source code from the URL
    java_8_code = get_java_source_code(file_pair['java_8_url'])
    java_11_code = get_java_source_code(file_pair['java_11_url'])

    # Set the minimum function length to 10
    min_function_length = 10
    # Extract the functions from the java 8 and java 11 files
    java_8_functions = extract_functions(java_8_code, file_pair['java_8_url'], min_function_length)
    java_11_functions = extract_functions(java_11_code, file_pair['java_11_url'], min_function_length)

    # Initialise two arrays to store dataset candidates
    dataset_candidates_same_params = []
    dataset_candidates_different_params = []

    # Foe each function in the java 8 file
    for java_8_function in java_8_functions:
        if check_for_deprecations(java_8_function["string"]):
            # Check that the Java 8 function has elements which were changed between Java 8 and 11
            for java_11_function in java_11_functions:
                # Iterate over all functons in the Java 11 file
                if (java_8_function['name'] == java_11_function['name']):
                    # Ensure that both functions have the same name
                    if (java_8_function['string'] != java_11_function['string']):
                        # Ensure that both functions are not identical
                        if (java_11_function['params'] == java_8_function['params']):
                            # If the functions have the same input paramaters, append the function (represented by a dictionary)
                            # and name to the dataset_candidates_same_params array
                            dataset_candidates_same_params.append({"name": java_8_function['name'],
                                                       "java_8_function": java_8_function,
                                                       "java_11_function": java_11_function})
                        else:
                            # The functions have different input paramaters, append the function (represented by a dictionary)
                            # and name to the dataset_candidates_different_params array
                            dataset_candidates_different_params.append({"name": java_8_function['name'],
                                                                   "java_8_function": java_8_function,
                                                                   "java_11_function": java_11_function})

    # Return the two dataset candidates arrays (an array of dictionaries containing dictionary representations of functions)
    return dataset_candidates_same_params, dataset_candidates_different_params


def main():
    # Read in the pairs from the text file and iterate over the URL Pairs
    with open("repo_pairs.txt", 'r') as my_file:
        content = my_file.read().strip()
    pairs = content.split('\n\n')

    # Initialise empty arrays to represent the dataset
    res_candidate_functions_same_params = []
    res_candidate_functions_different_params = []

    # Iterate over the URL Pairs
    for pair in pairs:
        # Extract the two URL's from the string and convert them an API compatible URL
        java_8_URL = convert_URL_for_API(pair.split('\n')[0])
        java_11_URL = convert_URL_for_API(pair.split('\n')[1])

        # Get an array of java files in the branch
        java_8_files = find_java_files(java_8_URL)
        java_11_files = find_java_files(java_11_URL)
        num_java_8_files = len(java_8_files)
        num_java_11_files = len(java_11_files)

        # Remove any files that do not exist in both repositories
        java_8_files = find_common_files(java_8_files, java_11_files)
        java_11_files = find_common_files(java_11_files, java_8_files)
        no_common_files = len(java_8_files)

        # Combine necessary information from the file dictionaries into one array, remove identical files at the same time
        java_files = combine_modified_java_files(java_8_files, java_11_files)
        no_changed_files = len(java_files)

        # Output an update with some statistics
        print("Found URL pair:")
        print("Java 8 has " + str(num_java_8_files) + " java files: " + java_8_URL)
        print("Java 11 has " + str(num_java_11_files) + " java files: " + java_11_URL)
        print("Found " + str(no_changed_files) + " modified files of " + str(no_common_files) + " common files")

        # Initialise an array to store candidate functions
        candidate_functions_same_params = []
        candidate_functions_different_params = []

        # Investigate each of the files further
        number_of_files = len(java_files)
        #for index in range(0, number_of_files):
        for index in tqdm(range(number_of_files), file=sys.stdout, leave=False):
            try:
                extracted_functions_same_params, extracted_functions_different_params = get_candidate_functions_from_files(java_files[index])

                # Append functions to the candidate_function arrays
                candidate_functions_same_params = candidate_functions_same_params + extracted_functions_same_params
                candidate_functions_different_params = candidate_functions_different_params + extracted_functions_different_params

                # Time delay due to GitHub API Limitations
                time.sleep(random.uniform(5, 10))
            except javalang.parser.JavaSyntaxError:
                pass

        # Output the total number of candidate functions found
        print("Found " + str(len(candidate_functions_same_params)) + " candidate functions with identical input parameters")
        print("Found " + str(len(candidate_functions_different_params)) + " candidate functions with different input parameters\n")

        # Extend the "res_candidate_functions" array to add in the candidate functions from the current repo
        res_candidate_functions_same_params = res_candidate_functions_same_params + candidate_functions_same_params
        res_candidate_functions_different_params = res_candidate_functions_different_params + candidate_functions_different_params


    # Serialize the candidate functions array so that it can be used later on
    store_candidate_functions(res_candidate_functions_same_params, "./../Shared_Files/web_scraped_ds_same_params.pkl")
    store_candidate_functions(res_candidate_functions_different_params, "./../Shared_Files/web_scraped_ds_diff_params.pkl")


if __name__ == '__main__':
    print("")
    main()
    read_candidate_functions("./../Shared_Files/web_scraped_ds_same_params.pkl")
    read_candidate_functions("./../Shared_Files/web_scraped_ds_diff_params.pkl")
