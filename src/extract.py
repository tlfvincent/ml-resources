import markdown
import ssl
import urllib.request
import re
from github import Github

import pandas as pd

_URL = "https://github.com/tlfvincent/ml-resources/blob/main/README.md"

# https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
_GITHUB_TOKEN = "my_github_token"


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


def extract_github_repo_statistics(github_repo_links):
    """

    Parameters
    ----------
    github_repo_links : list
        Contains links to Github repositories extracted from input data.

    Returns
    -------

    """
    g = Github(_GITHUB_TOKEN)

    for link in github_repo_links[0:5]:
        try:
            repo_name = link.split('github.com/')[1]
            repo_stats = g.get_repo(repo_name)
            print(f"Repository {repo_name}:")
            print(f"Star Count: {repo_stats.stargazers_count}")
            print(f"Last Modification Date: {repo_stats.last_modified}")
            print("---------------------")
        except:
            pass


if __name__ == "__main__":

    html_data = extract_data(_URL)

    github_repo_links = extract_links(html_data)

    extract_github_repo_statistics(github_repo_links)
