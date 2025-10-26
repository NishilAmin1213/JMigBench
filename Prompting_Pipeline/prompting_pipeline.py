from mistralai import Mistral
from codebleu import calc_codebleu
# pip install mistralai, tree-sitter-java==0.23.2
# pip installed codebleu==0.7.1(via github link)
    # pip install git+https://github.com/k4black/codebleu.git
from Shared_Files.utils import *


def store_result_pickle(results_array, filepath):
    """
    Function to store an array as a .pkl file
    :param results_array: array of the dataset with the generated data and result metrics included (to serialize)
    :param filepath: filepath to store the pkl file of results to
    :return: None
    """
    if os.path.exists(filepath):
        # Delete the pkl file if it already exists
        print("Deleting " + filepath + " as it already exists")
        os.remove(filepath)
    with open(filepath, "wb") as my_file:
        # Store the array to the pkl file
        pickle.dump(results_array, my_file)
        print("Stored candidate functions to " + filepath)


def get_prompt_messages(string):
    """
    Function to generate the role based prompt based on the input string
    :param string: Java 8 Function to include in the prompt
    :return: prompt_messages - an array of dictionaries which represents a role based prompt
    """
    prompt_messages = [
        # Formulate the system prompt
        {"role": "system", "content":
            "You are a senior Java engineer. Convert Java 8 code to Java 11 while preserving behavior."
            "Change any syntax in the Java 8 code that was removed or deprecated by Java 11."
            "Output ONLY the Java 11 method."
         },
        # Formulate the user prompt and inject the java 8 string between the <Java>...</Java> tags
        {"role": "user", "content":
            "Migrate the following Java 8 method (encapsulated within the <Java> and </Java> tags) to Java 11.\n\n"
            "<Java>\n" + string + "</Java>"
         },
    ]
    # Return the array of prompt messages
    return prompt_messages


def prompt_mistral_api(java_8_string, function_name, model="codestral-latest"):
    """
    Function to prompt the mistral API using an input string and model choice
    :param java_8_string: The Java 8 string to include in the prompt
    :param model: The MistralAI Model to send the prompt to
    :return: A string of the Generated Java 11 Function (post extraction)
    """
    print("Prompting Mistral API: " + function_name)

    # Initialise the MistralAPI client using the API key from the environment variable 'MISTRAL_API_KEY'
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

    # Generate the prompt messages array using the function above.
    prompt_messages = get_prompt_messages(java_8_string)

    # Prompt the mistral API and store the response in to 'response'
    response = client.chat.complete(
        model=model,
        messages=prompt_messages,
        temperature=0,
        max_tokens=2048
    )

    # Extract textual data from the response
    response_message = response.choices[0].message.content
    # Isolate the Java 11 code which is placed within '''java ... '''
    generated_code = response_message[response_message.find("```java\n") + 8:len(response_message) - 4]

    # Return the string representation of the isolated java code
    return generated_code


def run_program(dataset, prompt_function, output_filepath):
    """
    Function to run the prompting pipeline over the whole dataset
    :param dataset: Dataset to process through the LLM
    :param prompt_function: Function to use to prompt the LLM (allows some other LLMs to be plugged into this function)
    :param output_filepath: filepath to store the results dataset to
    :return:
    """
    print("Starting the Prompt Pipeline")
    # Prepare data structure to store the dataset with the results included
    dataset_including_results = []

    # Iterate over each data item in the dataset
    for data_item in dataset:
        # Locate function strings in the dataset
        java_8_string = data_item['java_8_function']['string']
        java_11_string = data_item['java_11_function']['string']

        # Prompt the mistral LLM using the Java 8 function
        generated_java_11_mistral = prompt_function(java_8_string, data_item['name'])

        # Add the generated string to the data item
        data_item['generated_java_11_string'] = generated_java_11_mistral

        # Calculate the codebelu comparison between the input Java 8 code and the true Java 11 code and store the metrics to the data item
        data_item['java_8_11_comparison'] = calc_codebleu(predictions=[java_8_string], references=[java_11_string], lang="java")
        # Calculate the codebleu comparison between the generated Java 11 code and the true Java 11 code and store the metrics to the data item
        data_item['java_11_11_comparison'] = calc_codebleu(predictions=[generated_java_11_mistral], references=[java_11_string], lang="java")

        # Append the data item with the results to the new dataset
        dataset_including_results.append(data_item)

    # Store the dataset containing results to a new pkl file (for further processing)
    store_result_pickle(dataset_including_results, output_filepath)


if __name__ == '__main__':
    print("Program Started")

    # Declare the Mistral API Key
    os.environ['MISTRAL_API_KEY'] = "QQBs9YH3MvPEZ8U8Zsb1suTjS0EMyZS5"

    # Run the secondary dataset through the pipeline
    print("Started Processing the Secondary Dataset")
    dataset = read_dataset('./../Shared_Files/synthetic_dataset.pkl', silent=False)
    run_program(dataset, prompt_mistral_api, "./../Shared_Files/mistral_results_synthetic_ds.pkl")
    print("Program Completed (Uncomment the remaining lines to process the full dataset)")

    # Run the initial full dataset through the pipeline
    #print("\n\nStarted Processing the Full Dataset")
    #dataset_same = read_dataset('web_scraped_ds_same_params.pkl', silent=False)
    #dataset_diff = read_dataset('web_scraped_ds_diff_params.pkl', silent=False)
    #run_program(dataset_same, prompt_mistral_api, "mistral_results_web_scraped_same_params.pkl")
    #run_program(dataset_diff, prompt_mistral_api, "mistral_results_web_scraped_diff_params.pkl")
