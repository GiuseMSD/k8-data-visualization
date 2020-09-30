import json
import requests
import sys

class gitPulls ():

    def __init__(self, config):

        with open(config) as f:
            data = json.load(f)

        self.repositories = data["repos"]
        #self.username = data["gituser"]
        #self.token = data ["token"]
        self.url = data["url"]

    def getPullRequests (self):

        for repo in self.repositories:
            print ("\nFetching pull requests from repo " + repo)

            temp_url = self.url + repo + "/pulls"
            req = requests.get(temp_url)#, auth=(self.username, self.token))
            data = req.json()

            empty = True

            try:
                for pullRequest in data:
                    empty = False
                    print("\nRepository Name: " + pullRequest["base"]["repo"]["name"])
                    print("PR Link: " + pullRequest["html_url"])

                    all_reviewers = ""
                    for reviewer in pullRequest["requested_reviewers"]:
                        all_reviewers += reviewer["login"] + ", "

                    if (all_reviewers == ""):
                        all_reviewers = "not assigned"
                    else:
                        all_reviewers = all_reviewers[:-2]

                    print("Reviewer(s): " + all_reviewers)
                    print("Date Created: " + str(pullRequest["created_at"]))

                if (empty):
                    print("There are no pull requests in " + repo)

            except:
                print("Unexpected error:", sys.exc_info()[0])

gp = gitPulls("config.json")
gp.getPullRequests()