import requests, os, csv

def make_request(url, filters={}):
    """
    function to make the request to the github api and return results
    :param url: URL to send the request to
    :param filters: Any filters to send with the request (defaults to no filters)
    :return: Request result
    """
    headers = {
        "Authorization": "token " + os.environ["GITHUB_KEY"],
        "User-Agent": "Mozilla/5.0"
    }
    return requests.get(url, headers=headers, params=filters)

def generate_avg_stats(filepath):
    """
    Read the CSV of repo statistics to output the average stats for each repo
    :param filepath: Filepath to the CSV file with per-repo statistics
    :return: None
    """
    # Initialize counters
    num_repos = 0
    total_commits = 0
    total_issues = 0
    total_releases = 0

    # Filepath to CSV with
    # ["Repo Name", "Total Commits", "Flagged Commits", "Total Issues", "Flagged Issues", "Total Releases", "Flagged Releases"]
    with open(filepath, mode='r', newline='') as my_file:
        # Open the CSV file
        for repo_line in list(csv.reader(my_file))[1:]:
            # Read each item of the CSV except the header
            # Collect the number of commits, issues and releases
            num_commits = repo_line[1]
            num_issues = repo_line[3]
            num_releases = repo_line[5]

            # Add the number of commits, issues and releases to the counters and increment the number of repo counter
            total_commits += int(num_commits)
            total_issues += int(num_issues)
            total_releases += int(num_releases)
            num_repos += 1

    # Output the stats to the console
    print("Average number of commits per repo: " + str(total_commits/num_repos))
    print("Average number of issues per repo: " + str(total_issues/num_repos))
    print("Average number of releases per repo: " + str(total_releases/num_repos))