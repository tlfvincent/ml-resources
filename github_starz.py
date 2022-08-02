"""
extract

This module extracts Github statistics for repositories listed in the
`https://github.com/tlfvincent/ml-resources/blob/main/README.md` file. The
statistics collected are:
- watchers_cnt: number of watchers on the repository
- subscribers_cnt: number of watchers on the repository
- last_modified_at: last timestamp when repository was modified
- last_release_at: last release timestamp for the repository
- contributor_cnt: number of contributors to the repository
"""

import markdown
import ssl
import urllib.request
import re
from github import Github

import pandas as pd

_URL = "https://github.com/tlfvincent/ml-resources/blob/main/README.md"

# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
_GITHUB_TOKEN = "your_github_token"


def extract_data(url):
    """
    Extract raw HTML data from specified URL.

    Parameters
    ----------
    url : str
        URL parameter to extract raw data from.

    Returns
    -------
    data : str
        Raw html data extracted from URL.
    """

    # we will opt out of certificate verification on a single connection
    # see `https://peps.python.org/pep-0476/` for more details
    context = ssl._create_unverified_context()

    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, context=context)
    html_data = resp.read()

    return html_data


def extract_links(data):
    """
    Extract any link found in the input string that contains the
    `github.com` pattern.

    Parameters
    ----------
    data : str
        Raw html data extracted from URL.

    Returns
    -------
    github_repo_links : list
        Contains links to Github repositories extracted from input data.
    """
    html = markdown.markdown(data, output_format='html')
    links = list(set(re.findall(r'href=[\'"]?([^\'" >]+)', html)))
    links = list(filter(lambda l: l[0] != "{", links))
    github_repo_links = [link for link in links if 'github.com' in link]

    return github_repo_links


def extract_github_repo_statistics(github_repo_links, print_out=True):
    """

    Parameters
    ----------
    github_repo_links : list
        Contains links to Github repositories extracted from input data.
    print_out : boolean, default to True
        If set to True, then print out results

    Returns
    -------
    github_stats : dict-like
    """
    g = Github(_GITHUB_TOKEN)

    github_stats = {}

    for link in github_repo_links[0:5]:
        try:
            repo_name = link.split('github.com/')[1]
            repo_stats = g.get_repo(repo_name)

            github_stats[repo_name] = [
                repo_stats._name.value,
                repo_stats._homepage.value,
                repo_stats._description.value,
                repo_stats.watchers_count,
                repo_stats.subscribers_count,
                repo_stats.get_commits()[0].last_modified,
                repo_stats.get_releases()[0].published_at,
                len(repo_stats.get_stats_contributors())
            ]

            if print_out:
                print(f"Repository {repo_name}:")
                print(f"Star Count: {repo_stats.stargazers_count}")
                print(f"Last Modification Date: {repo_stats.last_modified}")
                print("---------------------")
        except:
            pass

    return github_stats


if __name__ == "__main__":
    """
    This is the entrypoint for the module.
    """
    html_data = extract_data(_URL)

    github_repo_links = extract_links(html_data)

    github_stats = extract_github_repo_statistics(github_repo_links)

    results = pd.DataFrame.from_dict(
        github_stats,
        orient="index",
        columns=[
            "Name",
            "Homepage",
            "Description",
            "Watchers",
            "Subscribers",
            "Last Modification Date",
            "Last Release Date",
            "Contributor Count"
        ]
    )

    repo_markdown = results.to_markdown(index=False)
