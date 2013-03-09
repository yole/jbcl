jbcl
====

Command-line tools for working with JetBrains services.

Supported commands:

 * yt grab <issue-id>

  Automatically downloads the attachments for the specified YouTrack issue.
  Skips image attachments. If some of the attachments are .zip archives, 
  unpacks them. If only a single file was attached, opens it with the
  associated application.
