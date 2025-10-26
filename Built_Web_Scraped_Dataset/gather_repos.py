import os
import time
import pickle
import random
from web_scraping_utils import make_request

def get_java_repos(minimum_stars, results_per_page):
    """
    Function to search github and gather repositories that match certain criteria
    :param minimum_stars: The minimum number of stars that the repo must have
    :param results_per_page: The number of results per page to scrape
    :return:
    """
    # Form a base URL
    base_url = "https://api.github.com/search/repositories"


    # Perform an initial request to find out how many results there are
    params = {"q": "language:Java stars:>" + str(minimum_stars)}
    response = make_request(base_url, params)
    if response.status_code == 200:
        num_results = response.json()["total_count"]
        print("Identified " + str(num_results) + " repositories")
    else:
        print("Error getting the number of repositories - Status: " + str(response.status_code))
        num_results = 0

    # Calculate the number of pages to read based on the total number of results and the specified results per page
    pages_to_search = (num_results // results_per_page) + 1
    # Initialise an empty array to store results
    all_repositories = []

    # Iterate over each page and store the repositories into the all_repositories array
    for page in range(1, pages_to_search+1):
        print("Searching page: " + str(page))

        # Specify filters, page and number of results - Sort results by number of forks from high to low
        filters = {
            "q": "language:Java stars:>10000",
            "sort": "forks",
            "order": "desc",
            "per_page": results_per_page,
            "page": page
        }

        # Make the request to the API
        response = make_request(base_url, filters)

        if response.status_code == 200:
            # If data is returned, extract the individual repository names and append them to all_repositories
            items = response.json().get("items")

            for repo in items:
                if "full_name" in repo:
                    all_repositories.append(repo["full_name"])
        else:
            # If the status is not 200, there was an error, display the status code
            print("Error reading repositories - Status: " + str(response.status_code))

        # Random sleep between 10 and 15 seconds to prevent request from being rejected
        time.sleep(random.uniform(10,15))

    # Return the repository names that were found
    return all_repositories


if __name__ == '__main__':
    # Read all Java repositories using the search constraints below
    minimum_stars = 10000
    results_per_page = 100
    all_repositories = get_java_repos(minimum_stars, results_per_page)

    # Output statistics
    print("Found " + str(len(all_repositories)) + " repositories")

    # Store the repository names into all_repositories.pkl, deleting the file if it already exists
    repos_filepath = "./all_repositories.pkl"
    if os.path.exists(repos_filepath):
        print("Deleting all_repositories.pkl as it will be replaced")
        os.remove(repos_filepath)
    with open(repos_filepath, "wb") as my_file:
        pickle.dump(all_repositories, my_file)
        print("Storing repositories to all_repositories.pkl")
