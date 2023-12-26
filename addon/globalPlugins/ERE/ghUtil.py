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
		return request.urlopen(r)

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
		try:
			result = self._request(f"/repos/{owner}/{repo}/issues", data, "POST")
			print("Response from " + result.url + ": " + str(result.status))
			print(result.read())
			return result.status == 201
		except Exception as e:
			import traceback
			print(traceback.format_exc())
			return False