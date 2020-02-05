class QuayRepository(object):
    def __init__(self, module, rest):
        self.rest = rest
        self.module = module

    def _repo_url(self, repo=None, other=None):
        url_str = "/api/v1/repository"
        if repo is not None:
            url_str += "/" + str(repo)
        if other is not None:
            url_str += str(other)
        return url_str

    def change_trust(self, repo, body):
        """
        Change the visibility of a repository.

        POST /api/v1/repository/{repository}/changetrust

        Parameters:
            {
                "trust_enabled": true
            }

        Response Messages:
            201 - Successful creation
        """
        other = '/changetrust'
        url = self._repo_url(repo, other)
        response = self.rest.post(url, data=body)

        if response.status_code is not 201:
            self.module.fail_json(msg=response.info)
        return response.info

    def list_all(self):
        """
        Fetch the list of repositories visible to the current user under a variety of situations.

        GET /api/v1/repository

        Parameters:
            {
                "trust_enabled": true
            }

        Response Messages:
            201 - Successful creation
        """
        url = self._repo_url()
        response = self.rest.get(url)

        if response.status_code is not 200:
            self.module.fail_json(msg=response.info)
        return response.info

    def create(self, body=None):
        """
        Create a new repository.

        POST /api/v1/repository

        Parameters:
            body = {
                "repo_kind": "image",
                "namespace": "string",
                "visibility": "public",
                "repository": "string",
                "description": "string"
            }

        Response Messages:
            201 - Successful creation
            400 - Bad Request
            401 - Session required
            403 - Unauthorized access
            404 - Not found
        """
        if body is None:
            body = dict(self.module.params)

        url = self._repo_url()
        response = self.rest.post(url, data=body)

        if response.status_code is not 201:
            self.module.fail_json(msg=response.info)
        return response.info

    def change_visibility(self, repo):
        """
        Change the visibility of a repository.

        post /api/v1/repository/{repository}/changevisibility


        Parameters:
            {
                "visibility": "public"
            }

        Response Messages:
            201 - Successful creation
        """
        other = '/changevisibility'
        url = self._repo_url(repo, other)
        response = self.rest.post(url)

        if response.status_code is not 201:
            self.module.fail_json(msg=response.info)
        return response.info

    def delete(self, repo):
        """
        Delete a repository.

        DELETE /api/v1/repository/{repository}

        Parameters:
            None

        Response Messages:
            204 - Deleted
            400 - Bad Request
            401 - Session required
            403 - Unauthorized access
            404 - Not found
        """
        url = self._repo_url(repo)
        response = self.rest.delete(url)

        if response.status_code is not 204:
            self.module.fail_json(msg=response.info)
        return response.info

    def exists(self, repo):
        """
        Fetch the specified repository.

        GET /api/v1/repository/{repository}

        Parameters:
            includeTags - True/False
            includeStats - True/False

        Response Messages:
            200 - Successful invocation
            400 - Bad Request	
            401 - Session required
            403 - Unauthorized access
            404 - Not found
        """
        url = self._repo_url(repo)
        response = self.rest.get(url)

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            self.module.fail_json(msg=response.info)

    def update_description(self, repo):
        """
        Update the description in the specified repository.

        PUT /api/v1/repository/{repository}

        Parameters:
            {
                "trust_enabled": true
            }

        Response Messages:
            200 - Successful invocation
        """
        url = self._repo_url(repo)
        response = self.rest.put(url)

        if response.status_code is not 200:
            self.module.fail_json(msg=response.info)
        return response.info
