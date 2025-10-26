import os
import pickle, time, random, csv
from web_scraping_utils import make_request, generate_avg_stats

def save_flagged(repo_name, filename, flagged_array):
    """
    Function to append a note to a text file. Used to store flagged items found within repositories.
    :param repo_name: The name of the repository where the flagged item was found
    :param filename: The filename to append the string to
    :param flagged_array: An array containing data about the flagged information
    :return: None
    """
    #[keyword, body, id, place]
    if flagged_array:
        with open(filename, 'a') as my_file:
            my_file.write("\n" + repo_name + "\n")
            for flagged_item in flagged_array:
                my_file.write("    '" + flagged_item[0] + "' found in " + flagged_item[3] + ": " + str(flagged_item[2]) + "\n")


def save_statistics(filename, data):
    """
    Function to append statistics about a repository to a csv file
    :param filename: The csv file fo append the statistics to
    :param data: The array of data to append to the csv file
    :return: None
    """
    exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as my_file:
        writer = csv.writer(my_file)

        # If the CSV does not already exist, write a header in the first row of the csv file
        if not exists:
            writer.writerow(["Repo Name",
                             "Total Commits", "Flagged Commits",
                             "Total Issues", "Flagged Issues",
                             "Total Releases", "Flagged Releases"])

        # Append the statistics to the CSV file
        writer.writerow(data)


def read_open_issues(repo_name):
    """
    Function to read all open issues from a repository
    :param repo_name: The name of the repository to search
    :return: The number of open issues read, along with an array of any flagged issues
    """
    url = "https://api.github.com/repos/" + repo_name + "/issues"

    # Start with page 1
    page = 1
    # Set the empty page boolean to False
    empty_page = False

    # Initialise arrays to store the issues, flagged issues, and a counter of issues with pull requests
    issues = []
    flagged = []
    pr_counter = 0

    # Search until the page is empty
    while not empty_page:
        # Specify filters to include in the request
        filters = {
            "is":"issue",
            "state":"open",
            "per_page": 100,
            "page": page
        }

        # Make a request to the GitHub API to access issues for a certain page
        response = make_request(url, filters)

        if response.status_code == 200:
            # If data is returned, extract the issues on this page
            issues_found = response.json()

            # If 0 issues are found, there are no more pages and we can move on
            if len(issues_found) == 0:
                # Change boolean to prevent the program from entering the loop again
                empty_page = True
                # Skip to the end of this loop
                continue

            # If we are here, there are issues to process
            for issue in issues_found:
                if "pull_request" in issue:
                    pr_counter += 1
                else:
                    issues.append(issue)
        else:
            # If the status is not 200, there was an error, display the status code
            print("Error reading repositories - Status: " + str(response.status_code))

        # Increment the page variable to search the next page
        page += 1
        # Random sleep between 5 and 10 seconds to prevent requests from being rejected
        time.sleep(random.uniform(5, 10))

    # Hard Coded Keyword Arrays
    java8_keywords = ["java8", "jdk8", "8", "1.8"]
    java11_keywords = ["java11", "jdk11", "11"]
    migration_keywords = ["migrate", "migration", "migrated", "upgrade", "upgraded", "update", "updated", "transition",
                          "switched"]

    # Iterate over all issues
    for issue in issues:
        # Set booleans for 3 flags to False
        contains_java8 = False
        contains_java11 = False
        contains_migrate = False

        # Combine Issue Title and Issue Body for searching purposes
        try:
            issue_string = issue["title"] + issue["body"]
        except TypeError:
            issue_string = issue["title"]

        # Change boolean flags if the condition is satisfied
        for word in issue_string.lower().split(" "):
            if word in java8_keywords:
                contains_java8 = True
            if word in java11_keywords:
                contains_java11 = True
            if word in migration_keywords:
                contains_migrate = True

        # if the issue contains java 8, java 11 and migration related terms, then flag the issue
        if contains_java8 and contains_java11 and contains_migrate:
            res = ["Match in Issue: ", issue_string, issue["number"], "issue"]
            flagged.append(res)

    # Returned the array of important data
    return len(issues), flagged


def read_release_notes(repo_name):
    """
    Function to read all release notes from a repository
    :param repo_name: The name of the repository to search
    :return: The number of releases searched and an array of flagged releases
    """
    # Request to the GitHub API to see release notes
    url = "https://api.github.com/repos/" + repo_name + "/releases"

    # Start with page 1
    page = 1
    # Set the empty page boolean to False
    empty_page = False

    # Initialise arrays to store the releases and flagged releases
    releases = []
    flagged = []

    # Search until the page is empty
    while not empty_page:
        # Specify filters to include in the request
        filters = {
            "per_page": 100,
            "page": page
        }

        # Make a request to the GitHub API to access releases in a certain page
        response = make_request(url, filters)

        if response.status_code == 200:
            # If data is returned, extract the issues on this page
            releases_found = response.json()

            # If 0 issues are found, there are no more pages and we can move on
            if len(releases_found) == 0:
                # Change boolean to prevent the program from entering the loop again
                empty_page = True
                # Skip to the end of this loop
                continue

            # If we are here, there are commits to process
            releases += releases_found
        else:
            # If the status is not 200, there was an error, display the status code
            print("Error reading repositories - Status: " + str(response.status_code))

        # Increment the page variable to search the next page
        page += 1

        # Random sleep between 5 and 10 seconds to prevent requests from being rejected
        time.sleep(random.uniform(5, 10))

    # Hard Coded Keyword Arrays
    java8_keywords = ["java8", "jdk8", "8", "1.8"]
    java11_keywords = ["java11", "jdk11", "11"]
    migration_keywords = ["migrate", "migration", "migrated", "upgrade", "upgraded", "update", "updated", "transition",
                          "switched"]

    # Iterate over all releases
    for release in releases:
        # Set booleans for 3 flags to False
        contains_java8 = False
        contains_java11 = False
        contains_migrate = False

        try:
            # Change boolean flags if the condition is satisfied
            for word in release["body"].lower().split(" "):
                if word in java8_keywords:
                    contains_java8 = True
                if word in java11_keywords:
                    contains_java11 = True
                if word in migration_keywords:
                    contains_migrate = True
            # if the release contains java 8, java 11 and migration related terms, then flag the release
            if contains_java8 and contains_java11 and contains_migrate:
                res = ["Match in Release: ", release["body"], release["tag_name"], "release"]
                flagged.append(res)
        except AttributeError:
            # Release has no body, so skip it
            continue

    # Returned the array of important data
    return len(releases), flagged


def read_commit_history(repo_name):
    """
    Function to read the commit history of a repo
    :param repo_name: The name of the repository to search
    :return: The number of commits and the flagged commits themselves
    """
    # Request to the GitHub API to see the commit history
    url = "https://api.github.com/repos/" + repo_name + "/commits"

    # Start with page 1
    page = 1
    # Set the empty page boolean to False
    empty_page = False

    # Initialise arrays to store the commits and flagged commits
    commits = []
    flagged = []

    # Search until the page is empty
    while not empty_page:
        # Specify filters to include in the request
        filters = {
            "per_page": 100,
            "page": page
        }

        # Make a request to the GitHub API to access commits for a certain page
        response = make_request(url, filters)

        if response.status_code == 200:
            # If data is returned, extract the issues on this page
            commits_found = response.json()

            # If 0 issues are found, there are no more pages and we can move on
            if len(commits_found) == 0:
                # Change boolean to prevent the program from entering the loop again
                empty_page = True
                # Skip to the end of this loop
                continue

            # If we are here, there are commits to process
            commits += commits_found
        else:
            # If the status is not 200, there was an error, display the status code
            print("Error reading repositories - Status: " + str(response.status_code))

        # Increment the page variable to search the next page
        page += 1
        # line below is set to 2, instead of 10(which would allow 900 commits) for testing and speed purposes
        if page == 2:
            empty_page = True
            continue
        # Random sleep between 5 and 10 seconds to prevent request from being rejected
        time.sleep(random.uniform(5, 10))

    # Hard Coded Keyword Arrays
    java8_keywords = ["java8", "jdk8", "8", "1.8"]
    java11_keywords = ["java11", "jdk11", "11"]
    migration_keywords = ["migrate", "migration", "migrated", "upgrade", "upgraded", "update", "updated", "transition", "switched"]

    # Iterate over all commits
    for commit in commits:
        # Set booleans for 3 flags to False
        contains_java8 = False
        contains_java11 = False
        contains_migrate = False

        # Change boolean flags if the condition is satisfied
        for word in commit["commit"]["message"].lower().split(" "):
            if word in java8_keywords:
                contains_java8 = True
            if word in java11_keywords:
                contains_java11 = True
            if word in migration_keywords:
                contains_migrate = True

        # if the commit contains java 8, java 11 and migration related terms, then flag the commit
        if contains_java8 and contains_java11 and contains_migrate:
            res = ["Match in Commit: ", commit["commit"]["message"], commit["node_id"], "commit"]
            flagged.append(res)

    # Returned the array of important data
    return len(commits), flagged


def main(continue_scraping=False):
    # Read in the repo names if the file exists
    repos_filepath = "./all_repositories.pkl"
    if os.path.exists(repos_filepath):
        # If the pickle exists, extract the array of repository names
        print("Reading saved repository names")
        repo_names = pickle.load(open(repos_filepath, "rb"))
        number_of_repos = len(repo_names)
        print("Found " + str(number_of_repos) + " repositories")
    else:
        # If the pickle doesn't exist, tell the user to run 'gather_repos.py' and then return here
        print("all_repositories.pkl does not exist - run 'gather_repos.py' first")
        quit(1)

    try:
        # find the last scraped repo name in repo_stats.csv
        with open("./repo_stats.csv", mode='r', newline='') as my_file:
            last_repo = list(csv.reader(my_file))[-1][0]
        # remove the completed repositories
        scraped = repo_names.index(last_repo)+1
        repo_names = repo_names[scraped:]
        print("\nFound existing repo_stats.csv")

    except FileNotFoundError:
        print("\nNo existing repo_stats.csv")
        scraped = 0

        # Delete the flagged_repos and repo_stats files if they already exist
        if os.path.exists("./flagged_repos.txt"):
            os.remove("./flagged_repos.txt")
        if os.path.exists("./repo_stats.csv"):
            os.remove("./repo_stats.csv")


    print("Scraping from repository " + str(scraped))
    # Analyse each repository to see if it is useful or not
    for repo_name in repo_names:
        print("\n\nScraping Repo: " + str(scraped) + "/" + str(number_of_repos))
        print("Repo Name: " + str(repo_name))

        # Call functions to search commit history, open issues and release notes
        num_commits, flagged_commits = read_commit_history(repo_name)
        num_issues, flagged_issues = read_open_issues(repo_name)
        num_releases, flagged_releases = read_release_notes(repo_name)

        combined_flagged = flagged_issues + flagged_releases + flagged_commits

        # Save data from the three arrays into the output file
        save_flagged(repo_name, "./flagged_repos.txt", combined_flagged)

        # Save Repo Statistics to CSV file
        save_statistics("./repo_stats.csv", [repo_name,
                                           num_commits, len(flagged_commits),
                                           num_issues, len(flagged_issues),
                                           num_releases, len(flagged_releases)])

        # Output some Information
        print("Number of Flagged Items: " + str(len(combined_flagged)))

        scraped += 1


if __name__ == '__main__':
    main(True)
    generate_avg_stats("./repo_stats.csv")