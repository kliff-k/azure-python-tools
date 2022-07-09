# Jazz RTC configuration
rtc_config = {
  "host": "",
  "login_endpoint": "/ccm/authenticated/j_security_check",
  "project_endpoint": "/ccm/web/projects/",
  "get_endpoint": "/ccm/oslc/workitems/",
  "users_endpoint": "/jts/users/",
  "post_endpoint": "/ccm/oslc/contexts/{{context_id}}/workitems",
  "project_areas_endpoint": "/ccm/rpt/repository/foundation?"
                      "fields=projectArea/projectArea[archived=false]/(name|contextId)&size=1000",
  "timeline_endpoint": "/ccm/rpt/repository/foundation?"
                       "fields=developmentLine/"
                       "developmentLine[archived=false%20and%20contextId={{context_id}}]/"
                       "(name|iterations[archived=false]/(name|contextId))",
  "teams_endpoint": "/ccm/rpt/repository/foundation?"
                    "fields=teamArea/teamArea[archived=false%20and%20contextId={{context_id}}]/(name)",
  "search_member_endpoint": "/ccm/service/com.ibm.team.process.internal.service.web.IProcessWebUIService/membersPaged"
                            "?processAreaItemId={{context_id}}&pageNum=0&pageSize=25&searchTerm={{search_term}}"
}
