from ansible.module_utils.quay.repository import QuayRepository  # pylint: disable=import-error, no-name-in-module


class QuayMirror(QuayRepository):
    def create_mirror(self, repo, body):
        """
        Create repo mirror.

        POST /api/v1/repository/{repository}/mirror

        Parameters:
            body: {
                is_enabled: true
                external_registry_config: {
                    proxy: {
                        https_proxy: "string",
                        http_proxy: "string",
                        no_proxy: "string"
                    }
                },
                external_registry_username: "string",
                external_registry_password: "string",
                location: "string",
                sync_start_date: "iso8601",
                root_rule: {
                    rule_type: "TAG_GLOB_CSV",
                    rule_value:"string"
                },
                sync_interval: integer
                robot_username: "string"
            }

        Response Messages:
            201 - Successful creation
        """
        url = self._repo_url(repo, other='/mirror')
        response = self.rest.post(url)

        if response.status_code is not 201:
            self.module.fail_json(msg=response.info)
        return response.info

    def fetch_mirror(self, repo, body):
        """
        Fetch mirror configuration.

        GET /api/v1/repository/{repository}/mirror

        Parameters:
            None
        Response Messages:
            200 - Successful invocation
        """
        url = self._repo_url(repo, other='/mirror')
        response = self.rest.get(url)

        if response.status_code is not 200:
            self.module.fail_json(msg=response.info)
        return response.info

    def update_mirror(self, repo, body):
        """
        Create repo mirror.

        PUT /api/v1/repository/{repository}/mirror

        Parameters:
            body: {
                is_enabled: true
                external_registry_config: {
                    proxy: {
                        https_proxy: "string",
                        http_proxy: "string",
                        no_proxy: "string"
                    }
                },
                external_registry_username: "string",
                external_registry_password: "string",
                external_reference: "string",
                sync_start_date: "iso8601",
                root_rule: {
                    rule_type: "TAG_GLOB_CSV",
                    rule_value:"string"
                },
                sync_interval: integer
                robot_username: "string"
            }

        Response Messages:
            200 - Successful invocation
        """
        url = self._repo_url(repo, other='/mirror')
        response = self.rest.put(url)

        if response.status_code is not 200:
            self.module.fail_json(msg=response.info)
        return response.info
