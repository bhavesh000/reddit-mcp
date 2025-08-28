# Reddit MCP Server

A comprehensive Model Context Protocol (MCP) server for Reddit API integration, providing full access to Reddit's functionality through a standardized interface.

## Features

This MCP server provides complete Reddit API access including:

### Subreddit Operations
- Get subreddit information, posts, rules, and moderators
- Search subreddits
- Subscribe/unsubscribe to subreddits

### Post Operations
- Get post details and comments
- Submit text and link posts
- Delete posts (as author)
- Search across Reddit or within specific subreddits

### Comment Operations
- Reply to posts and comments
- Edit and delete comments (as author)
- Get comment threads with nested replies

### User Operations
- Get user information, posts, comments, and karma
- View saved, upvoted, and downvoted content
- Follow/unfollow users

### Interaction Operations
- Upvote/downvote posts and comments
- Save/unsave content
- Hide/unhide posts

### Messaging
- Get inbox messages
- Send private messages
- Mark messages as read/unread

### Additional Features
- Get trending subreddits
- Access front page
- Get random posts
- Manage multireddits

## Prerequisites

- Python 3.8 or higher
- Reddit account
- Reddit API credentials (client ID and secret)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/reddit-mcp.git
cd reddit-mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Reddit API credentials:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Note your client ID (under "personal use script") and secret

4. Set environment variables:
```bash
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export REDDIT_USERNAME="your_reddit_username"
export REDDIT_PASSWORD="your_reddit_password"
```

## Usage

### Running the Server

```bash
python reddit-mcp-server.py
```

The server runs using stdio transport for MCP communication.

### Example Configuration

To use with Claude or other MCP clients, add to your MCP configuration:

```json
{
  "mcpServers": {
    "reddit": {
      "command": "python",
      "args": ["/path/to/reddit-mcp-server.py"],
      "env": {
        "REDDIT_CLIENT_ID": "your_client_id",
        "REDDIT_CLIENT_SECRET": "your_client_secret",  
        "REDDIT_USERNAME": "your_username",
        "REDDIT_PASSWORD": "your_password"
      }
    }
  }
}
```

## Available Tools

The server provides 50+ tools for Reddit operations:

- **Subreddit**: `get_subreddit_info`, `get_subreddit_posts`, `search_subreddits`, etc.
- **Posts**: `get_post`, `submit_text_post`, `submit_link_post`, `delete_post`, etc.
- **Comments**: `reply_to_post`, `reply_to_comment`, `edit_comment`, `delete_comment`, etc.
- **Users**: `get_user_info`, `get_user_posts`, `get_user_comments`, `get_user_karma`, etc.
- **Voting**: `upvote`, `downvote`, `clear_vote`, `save_item`, `unsave_item`, etc.
- **Search**: `search_all_reddit`, `search_in_subreddit`, `search_users`
- **Messaging**: `get_inbox`, `send_message`, `mark_message_read`, etc.
- **Subscriptions**: `subscribe_subreddit`, `unsubscribe_subreddit`, `follow_user`, etc.

## Security Notes

- Never commit your Reddit API credentials to version control
- Use environment variables or secure credential storage
- The server requires authenticated access for all operations
- Rate limits apply based on Reddit's API guidelines

## Dependencies

- `praw` - Python Reddit API Wrapper
- `fastmcp` - Fast Model Context Protocol implementation

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.