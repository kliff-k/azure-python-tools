# Azure AppCenter configuration
ac_config = {
  "host": "https://api.appcenter.ms",
  "api_version": "/v0.1",
  "apps_endpoint": "/apps",
  "versions_endpoint": "/apps/{{owner_name}}/{{app_name}}/errors/available_versions?start={{start_date}}&$top={{top}}",
  "groups_endpoint": "/apps/{{owner_name}}/{{app_name}}/errors/errorGroups",
  "group_endpoint": "/apps/{{owner_name}}/{{app_name}}/errors/errorGroups/{{error_group_id}}",
  "exceptions_endpoint": "/apps/{{owner_name}}/{{app_name}}/errors/errorGroups/{{error_group_id}}/stacktrace",
  "owner_name": ""
}
