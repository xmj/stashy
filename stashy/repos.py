from .helpers import Nested, ResourceBase, IterableResource
from .errors import ok_or_error, response_or_error
from .pullrequests import PullRequests


class Repository(ResourceBase):
    def __init__(self, slug, url, client, parent):
        super(Repository, self).__init__(url, client, parent)
        self._slug = slug

    @response_or_error
    def delete(self):
        """
        Schedule the repository to be deleted
        """
        return self._client.delete(self.url())

    @response_or_error
    def update(self, name):
        """
        Update the name of a repository.

        The repository's slug is derived from its name. If the name changes the slug may also change.
        """
        return self._client.post(self.url(), data=dict(name=name))

    @response_or_error
    def get(self):
        """
        Retrieve the repository
        """
        return self._client.get(self.url())

    @response_or_error
    def branches(self, filterText=None, orderBy=None):
        """
        Retrieve the branches matching the supplied filterText param.
        """
        params = {}
        if filterText is not None:
            params['filterText'] = filterText
        if orderBy is not None:
            params['orderBy'] = orderBy
        return self._client.get(self.url('/branches'), params=params)

    @response_or_error
    def _get_default_branch(self):
        return self._client.get(self.url('/branches/default'))

    @ok_or_error
    def _set_default_branch(self, value):
        return self._client.put(self.url('/branches/default'), data=dict(id=value))

    default_branch = property(_get_default_branch, _set_default_branch, doc="Get or set the default branch")

    def browse(self, at=None, type=False, blame='', noContent=''):
        params = {}
        if at is not None:
            params['at'] = at
        if type is not None:
            params['type'] = type
        if blame:
            params['blame'] = blame
        if noContent:
            params['noContent'] = noContent

        return self.paginate("/browse", params=params)

    def changes(self, until, since=None):
        """
        Retrieve a page of changes made in a specified commit.

        since: the changeset to which until should be compared to produce a page of changes.
               If not specified the parent of the until changeset is used.

        until: the changeset to retrieve file changes for.
        """
        params = dict(until=until)
        if since is not None:
            params['since'] = since
        return self.paginate('/changes', params=params)

    def commits(self, until, since=None, path=None):
        """
        Retrieve a page of changesets from a given starting commit or between two commits.
        The commits may be identified by hash, branch or tag name.

        since: the changeset id or ref (exclusively) to restrieve changesets after
        until: the changeset id or ref (inclusively) to retrieve changesets before.
        path: an optional path to filter changesets by.

        Support for withCounts is not implement.
        """
        params = dict(until=until, withCounts=False)
        if since is not None:
            params['since'] = since
        if path is not None:
            params['path'] = path
        return self.paginate('/commits', params=params)

    pull_requests = Nested(PullRequests, relative_path="/pull-requests")


class Repos(ResourceBase, IterableResource):
    @response_or_error
    def create(self, name, scmId="git"):
        return self._client.post(self.url(), data=dict(name=name, scmId=scmId))

    def __getitem__(self, item):
        return Repository(item, self.url(item), self._client, self)


Repos.all.im_func.func_doc = """Retrieve repositories from the project"""