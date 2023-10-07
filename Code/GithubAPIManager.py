import datetime
import requests
import json
import logging
import time

logging.basicConfig(level=logging.DEBUG)


class GithubAPIManager:
    apiLimit = -1
    firstReqTime = datetime.time
    currentTokenIndex = 0
    resetTime = 0

    tokens = ["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", ""]

    def __init__(self):
        self.BASE_URL = "https://" + self.tokens[0] + "@api.github.com"
        self.GithubToken = self.tokens[0]
        self.header = {
            'Authorization': self.GithubToken
        }

    def getAPILimit(self):
        status = json.loads(requests.get(self.BASE_URL + "/rate_limit", headers=self.header).text)
        remaining = status['resources']['core']['remaining']
        reset = status['resources']['core']['reset']

        return [remaining, reset]

    def switchTokens(self):
        lastTokenIndex = self.currentTokenIndex

        while 1:
            self.currentTokenIndex = (self.currentTokenIndex + 1) % len(self.tokens)
            self.GithubToken = self.tokens[self.currentTokenIndex]

            remainingStatus = self.getAPILimit()
            apiLimitLeft = remainingStatus[0]
            self.apiLimit = apiLimitLeft
            self.resetTime = remainingStatus[1]

            if apiLimitLeft == 0:
                if self.currentTokenIndex == lastTokenIndex:
                    currentTime = int(datetime.datetime.now().timestamp())
                    if currentTime < self.resetTime:
                        interval = self.resetTime - currentTime
                        logging.info('Waiting for ' + str(interval) + ' seconds...')
                        time.sleep(interval)

                        remainingStatus = self.getAPILimit()
                        self.apiLimit = remainingStatus[0]
                        self.resetTime = remainingStatus[1]
                        break

        self.BASE_URL = "https://" + self.GithubToken + "@api.github.com"

    def ensureAPILimitAllowed(self):
        if self.apiLimit == -1:
            remainingStatus = self.getAPILimit()
            self.apiLimit = remainingStatus[0]
            self.resetTime = remainingStatus[1]
            logging.info('REMAINING CALLS: ' + str(self.apiLimit))

        if self.apiLimit == 0:
            self.switchTokens()

        self.apiLimit -= 1

    def makingGithubCall(self, endpoint):
        self.ensureAPILimitAllowed()
        fullEndpoint = self.BASE_URL + endpoint

        logging.info(fullEndpoint)

        response = requests.get(url=fullEndpoint, headers=self.header)

        if response.status_code != 200:
            logging.error('net error: ' + str(response.status_code))

        return json.loads(response.text)