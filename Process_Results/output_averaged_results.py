import os, pickle
from Shared_Files.utils import *
import numpy as np
from categorize import categorize
from deprecated_terms import secondary_deprecated_search_terms
import matplotlib.pyplot as plt


def read_results(filepath):
    return read_dataset(filepath)

def plot_keyword_removal_bar_chart(keyword_analysis):
    """
    Function to plot a bar chart depicting the number keywords in the initial code and the number that were removed
    :param keyword_analysis: Dictionary where the keys are keyword categories and each sub-dictionary stores counts
        for the total and removed number of keywords
    :return: None
    """
    # Identify keyword categories from the keys of the keyword_analysis dictionary
    categories = keyword_analysis.keys()

    # Initialise arrays to store data for plotting bars
    removed = []
    total = []
    labels = []

    # For each keyword category, add the relevant data into the arrays for plotting
    for keyword_group in categories:
        removed.append(keyword_analysis[keyword_group]['removed'])
        total.append(keyword_analysis[keyword_group]['total'])
        percentage_removed = str(round(keyword_analysis[keyword_group]['removed'] / keyword_analysis[keyword_group]['total'] * 100, 2)) + '%'
        labels.append(keyword_group + " - " + percentage_removed)

    # Calculate overall percentage removed (overall for all keyword in the dataset)
    percent_removed = round(sum(removed) / sum(total)*100, 2)

    # Create an array to position the bars
    x = np.arange(len(categories))
    width = 0.35

    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(11, 6))

    # Create the bar for the number of removed keywords and the bar for the total number of keywords
    removed_bar = ax.bar(x + width / 2, removed, width, label="Removed: " + str(percent_removed) + "% success rate ")
    total_bar = ax.bar(x - width / 2, total, width, label="Total: " + str(sum(total)) + " keywords")

    # Add labels to the axis of the bar chart
    ax.set_ylabel("Number of Keywords")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.legend()

    # Annotate bars with values
    for bars in [removed_bar, total_bar]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha="center", va="bottom")

    # Format the layout and save the plot to an SVG
    plt.tight_layout()
    plt.savefig("./../Outputs/Keyword Removal Bars.svg")


def calc_keyword_removal_success(filepath, deprecated_search_terms):
    """
    Function to calculate the number of keywords that were removed from the initial code
    :param filepath: Filepath to the results dataset
    :param deprecated_search_terms: Array of keyword terms that could be removed
    :return: None
    """
    # Read the results dataset from the pkl file
    data_array = read_results(filepath)

    # Initialise counters for the total number of functions and successfully migrated functions
    total_count = 0
    success_count = 0
    # Initialise counters for the total number of keywords and the number of removed keywords
    num_keywords_in_java_8_code = 0
    num_successfully_removed_keywords = 0

    # This will have keyword groups as keys and then a sub dictionary to hold removed and total count
    keyword_analysis = {}

    # Iterate over each data item in the results dataset
    for data_item in data_array:
        # Increment the count of the total number of functions
        total_count += 1
        # get the java 8 function and generated java 11 function strings
        java_8_function = data_item["java_8_function"]['string']
        generated_java_11_function = data_item["generated_java_11_string"]

        # Check the Java 8 function for any deprecated keywords and the category for any matches in the array
        deprecated_terms_in_java_8 = []
        for keyword in deprecated_search_terms:
            if keyword in java_8_function:
                deprecated_terms_in_java_8.append(categorize(keyword))

        # Check the generated Java 11 function for any deprecated keywords and the category for any matches in the array
        deprecated_terms_in_generated_java_11 = []
        for keyword in deprecated_search_terms:
            if keyword in generated_java_11_function:
                deprecated_terms_in_generated_java_11.append(categorize(keyword))

        # if there are no keywords left in the generated code, the migration is successful
        if deprecated_terms_in_generated_java_11 == []:
            # Increment the function succes count
            success_count += 1

        # Count how many of the keywords were in the java 8 code and how many were in the java 11 code
        num_keywords_in_java_8 = len(deprecated_terms_in_java_8)
        num_keywords_in_generated_java_11 = len(deprecated_terms_in_generated_java_11)
        # Add these values to the keyword wise counters
        num_keywords_in_java_8_code += num_keywords_in_java_8
        num_successfully_removed_keywords += num_keywords_in_java_8 - num_keywords_in_generated_java_11

        # Check if any keywords were carried forward
        for keyword in deprecated_terms_in_java_8:
            carried_forward = False
            if keyword in deprecated_terms_in_generated_java_11:
                carried_forward = True


            # Increment the total count for the keyword category in the dictionary
            # If the keyword category does not exist as a key, create it and initialize values
            try:
                keyword_analysis[keyword]['total'] += 1
            except KeyError:
                # The keyword does not exist in the dict
                keyword_analysis[keyword] = {}
                keyword_analysis[keyword]['total'] = 1
                keyword_analysis[keyword]['removed'] = 0

            # If a keyword was not carried forward, increment the counter for the removed count in the dictionary
            # Create the removed item and initialize the value if it does not already exist.
            if not carried_forward:
                try:
                    keyword_analysis[keyword]['removed'] += 1
                except KeyError:
                    keyword_analysis[keyword]['removed'] = 1

    # Plot the bar chart using the keyword_analysis dictionary
    plot_keyword_removal_bar_chart(keyword_analysis)

    # Output some statistics to the console
    print("\nSuccessfully Migrated Functions: " + str(round(success_count/total_count*100, 2)) + "%")
    print("Successfully Removed Terms: " + str(round(num_successfully_removed_keywords/num_keywords_in_java_8_code*100, 2)) + "%")



def get_avg_stats(model_name, filepaths):
    """
    Function to calculate the average codebleu statistics for the results dataset
    :param model_name: Name of the model that was used (for labelling the output)
    :param filepaths: Filepath to the results dataset
    :return: None
    """
    # Read the results dataset from the pickle file
    data_array = []
    for path in filepaths:
        data_array = data_array + read_results(path)

    # Initialise arrays to store prefect match functions, or functions where codebleu measurements were not available
    complete_match_functions = []
    failed_codebleu_functions = []

    # Initialize the function counter
    function_count = 0

    # Create an array or metric labels
    metrics = ['codebleu', 'ngram_match_score', 'weighted_ngram_match_score', 'syntax_match_score', 'dataflow_match_score']
    # Initialize dictionary to hold the total codebleu scores of the generated functions
    total_scores_generated = {"codebleu":0,  "ngram_match_score":0, "weighted_ngram_match_score":0, "syntax_match_score":0, "dataflow_match_score":0}
    # Initialize dictionary to hold the total codebleu scores of the java 8 functions
    total_scores_input = {"codebleu":0,  "ngram_match_score":0, "weighted_ngram_match_score":0, "syntax_match_score":0, "dataflow_match_score":0}

    # Iterate over each data item in the data array
    for data_item in data_array:
        # if dataflow match score is 0, then ignore the metric as codebleu failed to scan the function
        if data_item['java_11_11_comparison']['dataflow_match_score'] == 0:
            # store it to the array and skip the rest of the processing
            failed_codebleu_functions.append(data_item['name'])
            continue

        # Increment the function count (only for functions where codebleu metrics were used)
        # This ensures that the average is correctly computed
        function_count += 1

        if data_item['java_11_11_comparison']['codebleu'] == 1:
            # this function entirely matched the ground truth function, so store it to the array
            complete_match_functions.append(data_item['name'])

        # for each metric, add the score for the current function to the counter arrays
        for metric in metrics:
            total_scores_generated[metric] = total_scores_generated[metric] + data_item['java_11_11_comparison'][metric]
            total_scores_input[metric] = total_scores_input[metric] + data_item['java_8_11_comparison'][metric]


    # Output Metrics in a Tabulated Format
    print("Average CodeBLEU score for " + str(function_count) + " of " + str(function_count + len(failed_codebleu_functions)) + " functions from the " + model_name + ":")
    print("Metric".ljust(30) + "Java 11 Comparison".ljust(25) + "Java 8 vs 11 Comparison".ljust(25) + "Difference".ljust(25))
    print("-" * 80)

    for metric in metrics:
        avg_mistral = total_scores_generated[metric] / function_count
        avg_base = total_scores_input[metric] / function_count
        print(metric.ljust(30) + (format(round(avg_mistral, 2))).ljust(25) + (format(round(avg_base, 2))).ljust(25) + (format(round(avg_base - avg_mistral, 2)).ljust(25)))

    # Output other information to the console
    print("")
    print(str(len(complete_match_functions)) + " functions had a complete match")
    print(str(len(complete_match_functions)) + " Complete Match Functions: " + str(complete_match_functions))
    print(str(len(failed_codebleu_functions)) + " Failed Codebleu Function: " + str(failed_codebleu_functions))



if __name__ == "__main__":
    # This file uses the result pkl files to output statistics about the results
    filepath = './../Shared_Files/mistral_results_synthetic_ds.pkl'

    # Output average codebleu statistics for the secondary dataset
    print('')
    get_avg_stats("Mistral API - Secondary Dataset", [filepath])

    # Calculate keyword removal success for the secondary dataset
    calc_keyword_removal_success(filepath, secondary_deprecated_search_terms)
    print("\nUncomment line 229 below to show average statistics for the full dataset (requires mistral_results_same.pkl and mistral_results_diff.pkl")

    # Output average codebleu statistics for the full dataset
    #get_avg_stats("Mistral API - Full Dataset", ["mistral_results_same.pkl", "mistral_results_diff.pkl"])









