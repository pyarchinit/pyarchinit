import requests

# Replace with your actual repo details
owner = 'pyarchinit'
repo = 'pyarchinit'
since_date = '2018-01-01T00:00:00Z'  # ISO8601 format

# Optional: Use a token for authentication
headers = {
    'Authorization': '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'
}

# Fetch commits since 2018
response = requests.get(
    f'https://api.github.com/repos/{owner}/{repo}/commits?since={since_date}',
    headers=headers
)

# Check if the request was successful
if response.status_code == 200:
    commits = response.json()
    for commit in commits:
        print(commit['commit']['message'])
else:
    print('Failed to fetch commits:', response.content)