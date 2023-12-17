# coding: utf-8

import json
from urllib import request
from urllib import parse
from urllib import error

BASE_URL = "https://api.github.com"

class GhUtil:
	def __init__(self, token):
		self._token = token

	def _getHeader(self):
		ret = {
			"X-GitHub-Api-Version": "2022-11-28",
			"Authorization": "Bearer " + self._token,
			"User-Agent": "EnglishReadingEnhancer",
			"accept": "application/vnd.github+json",
			"Content-Type": "application/json",
		}
		return ret

	def _request(self, url, data=None, method=None):
		r = request.Request(BASE_URL + url, headers=self._getHeader(), data=data, method=method)
		try:
			with request.urlopen(r) as response:
				s = response.read()
			obj = json.loads(s)
			return obj
		except error.HTTPError as e:
			print(e)
			return {"error": str(e)}

	def root(self):
		return self._request("")

	def createIssue(self, owner, repo, title, body, labels=()):
		if type(labels) == str:
			labels = (labels,)
		data = {
			"title": title,
			"body": body,
			"labels": labels,
		}
		data = json.dumps(data)
		data = data.encode("utf-8")
		result = self._request(f"/repos/{owner}/{repo}/issues", data, "POST")
		return result


if __name__ == "__main__":
	obj = GhUtil("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")
	# result = obj.root()
	result = obj.createIssue("kitabatake1013", "gh_issue_test", "Test Issue", "Hello.\n\nThis is test.", "sent_from_application")
