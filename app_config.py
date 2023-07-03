import os

# Application (client) ID of app registration
CLIENT_ID = 'd9079521-7634-4a43-af74-230589f9b3c6'
# Application's generated client secret: never check this into source control!
CLIENT_SECRET = 'LDg8Q~J5WZXGRrjM2nvm6~HncXHjRtN4pezeUcES'

# AUTHORITY = "https://login.microsoftonline.com/common"  # For multi-tenant app
# AUTHORITY = f"https://login.microsoftonline.com/{('85132005-8032-4d02-a401-9573a4e9a5c2', 'common')}"
AUTHORITY='https://testoutlookapp.azurewebsites.net/'

REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
# The absolute URL must match the redirect URI you set
# in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/me/mailFolders'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["Mail.ReadBasic", "Mail.Send", "User.Read"]

TENANT_ID= '85132005-8032-4d02-a401-9573a4e9a5c2'

# Tells the Flask-session extension to store sessions in the filesystem
SESSION_TYPE = "filesystem"
# Using the file system will not work in most production systems,
# it's better to use a database-backed session store instead.

