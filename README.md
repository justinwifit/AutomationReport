# AutomationReport
This script pulls issues from iFit Github and converts them to a CSV file

# Prerequisites
- Python 2.7+
- Requests python library

# Usage
- python AutomationReport.py "Date" "Token"(if local env variable isn't saved)
- From->To: "YYYY-MM-DD..YYYY-MM-DD"
- Greater Than: ">=YYYY-MM-DD"
- Less Than: "<=YYYY-MM-DD"
- Example: python AutomationReport.py "2016-01-01..2017-01-01" "a3jfdkh3jhfaksdkj"
- Example(with local env variable already saved): python AutomationReport.py ">=2016-01-01"

# Token
You may save a local env variable named "GIT_API_KEY" to automatically pull your Git token.

# Errors
- This script only catches date formatting errors
- Refer to JSON file generated for more specific errors from Github (invalid token or date range etc.)

# References
- [Install Requests](http://docs.python-requests.org/en/master/user/install/)
- [Git API Syntax](https://stackoverflow.com/questions/50745658/get-issues-on-a-date-range-from-github-enterprise-api/50749472#50749472)


