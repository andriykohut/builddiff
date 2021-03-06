import requests

from requests.compat import urljoin


class Build(object):

    """Jenkins build."""

    def __init__(self, auth, url, job, number, **kwargs):
        """Wraps jenkins build info.

        :auth: Requests auth instance.
        :url: Jenkins url.
        :job: Job name.
        :number: Build number.
        :data: Info dict.

        """
        self._auth = auth
        self.url = url
        self.job = job
        self.number = number
        self._data = kwargs

    def console_output(self):
        """Get console output of build.

        :returns: string with full console output.

        """
        return requests.get(
            urljoin(self.url, "/job/{}/{}/consoleText".format(self.job, self.number)), auth=self._auth
        ).text

    def __getitem__(self, attr):
        return self._data[attr]

    def __setitem__(self, attr, val):
        self._data[attr] = val

    def __str__(self):
        return "job: {} build: {}".format(self.job, self.number)


class Jenkins(object):

    """Get job and build data from jenkins."""

    def __init__(self, auth, url):
        """Create a wrapper for querying Jenkins api.

        :auth: How to authenticate (requests.auth instance).
        :url: Jenkins url.

        """
        self._auth = auth
        self._url = url

    def builds(self, job, tree):
        """Grab builds info.

        :job: job name.
        :tree: List of fields to get.
        :returns: List with builds info.

        """
        url = urljoin(self._url, '/job/{}/api/json/build'.format(job))
        params = "depth=1&tree=builds[{}]".format(','.join(tree))
        for build in requests.get(url, params, auth=self._auth).json()['builds']:
            yield Build(self._auth, self._url, job, build['number'], **build)

    def matching_builds(self, job, tree, match_map):
        """Find bulds where key matches regex.

        Note: tree should contain key.

        :job: Job name.
        :tree: List of fields to get.
        :match_map: dict where keys are fields (from tree), and values are regular expression objects.
        :returns: Generator object with matching builds.

        """
        if not set(tree).issuperset(set(match_map.keys())):
            raise ValueError("Keys in match_map should be subset of tree")
        for build in self.builds(job, tree):
            matches = [regex.match(build[field]) for field, regex in match_map.items()]
            if all(matches):
                build['matches'] = matches
                yield build
