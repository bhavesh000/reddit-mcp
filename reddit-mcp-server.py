#!/usr/bin/env python3
"""
Reddit MCP Server - Complete Reddit API access via FastMCP
Single file implementation with all possible Reddit operations
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
import praw
from praw.models import Submission, Comment, Redditor, Subreddit

# Configure logging to stderr to avoid interfering with stdio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp = FastMCP("reddit-mcp-server")

# Global Reddit instance
reddit = None

def init_reddit():
    """Initialize Reddit instance with environment variables"""
    global reddit
    if reddit is None:
        reddit = praw.Reddit(
            client_id=os.environ['REDDIT_CLIENT_ID'],
            client_secret=os.environ['REDDIT_CLIENT_SECRET'],
            username=os.environ['REDDIT_USERNAME'],
            password=os.environ['REDDIT_PASSWORD'],
            user_agent=f"MCP:reddit-server:v1.0 (by /u/{os.environ['REDDIT_USERNAME']})"
        )
        logger.info("Reddit initialized in authenticated mode")
    return reddit

def serialize_reddit_object(obj):
    """Convert Reddit objects to JSON-serializable format"""
    if obj is None:
        return None
    
    # Handle lists
    if isinstance(obj, list):
        return [serialize_reddit_object(item) for item in obj]
    
    # Handle PRAW models
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in vars(obj).items():
            if not key.startswith('_'):
                try:
                    # Try to serialize the value
                    if hasattr(value, '__dict__'):
                        result[key] = str(value)  # Convert complex objects to string
                    else:
                        result[key] = value
                except:
                    result[key] = str(value)
        return result
    
    return obj

# ============================================================================
# SUBREDDIT OPERATIONS
# ============================================================================

@mcp.tool()
def get_subreddit_info(subreddit_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
    
    Returns:
        Subreddit information including description, subscribers, rules, etc.
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        return {
            "name": subreddit.display_name,
            "title": subreddit.title,
            "description": subreddit.public_description,
            "subscribers": subreddit.subscribers,
            "created_utc": subreddit.created_utc,
            "over_18": subreddit.over18,
            "subreddit_type": subreddit.subreddit_type,
            "url": f"https://reddit.com{subreddit.url}",
            "active_user_count": subreddit.active_user_count,
            "accounts_active": subreddit.accounts_active,
            "icon_img": subreddit.icon_img,
            "banner_img": subreddit.banner_img,
            "header_img": subreddit.header_img,
            "allow_images": subreddit.allow_images,
            "allow_videos": subreddit.allow_videos,
            "spoilers_enabled": subreddit.spoilers_enabled,
            "submission_type": subreddit.submission_type,
            "user_is_banned": subreddit.user_is_banned,
            "user_is_moderator": subreddit.user_is_moderator,
            "user_is_subscriber": subreddit.user_is_subscriber
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_subreddit_posts(
    subreddit_name: str,
    sort: str = "hot",
    time_filter: str = "all",
    limit: int = 25
) -> List[Dict[str, Any]]:
    """
    Get posts from a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
        sort: Sort method (hot, new, top, rising, controversial)
        time_filter: Time filter for top/controversial (hour, day, week, month, year, all)
        limit: Number of posts to retrieve (max 100)
    
    Returns:
        List of posts from the subreddit
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        
        if sort == "hot":
            posts = subreddit.hot(limit=limit)
        elif sort == "new":
            posts = subreddit.new(limit=limit)
        elif sort == "top":
            posts = subreddit.top(time_filter=time_filter, limit=limit)
        elif sort == "rising":
            posts = subreddit.rising(limit=limit)
        elif sort == "controversial":
            posts = subreddit.controversial(time_filter=time_filter, limit=limit)
        else:
            return {"error": "Invalid sort method"}
        
        result = []
        for post in posts:
            result.append({
                "id": post.id,
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "created_utc": post.created_utc,
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "url": post.url,
                "selftext": post.selftext,
                "permalink": f"https://reddit.com{post.permalink}",
                "is_video": post.is_video,
                "is_self": post.is_self,
                "stickied": post.stickied,
                "locked": post.locked,
                "nsfw": post.over_18,
                "spoiler": post.spoiler,
                "distinguished": post.distinguished,
                "link_flair_text": post.link_flair_text,
                "author_flair_text": post.author_flair_text,
                "gilded": post.gilded,
                "total_awards_received": post.total_awards_received
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def search_subreddits(query: str, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Search for subreddits
    
    Args:
        query: Search query
        limit: Number of results to return
    
    Returns:
        List of matching subreddits
    """
    reddit = init_reddit()
    try:
        subreddits = reddit.subreddits.search(query, limit=limit)
        result = []
        for sub in subreddits:
            result.append({
                "name": sub.display_name,
                "title": sub.title,
                "description": sub.public_description,
                "subscribers": sub.subscribers,
                "over_18": sub.over18,
                "url": f"https://reddit.com{sub.url}"
            })
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_subreddit_rules(subreddit_name: str) -> List[Dict[str, Any]]:
    """
    Get rules of a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
    
    Returns:
        List of subreddit rules
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        rules = subreddit.rules()
        result = []
        for rule in rules:
            result.append({
                "short_name": rule.get("short_name"),
                "description": rule.get("description"),
                "kind": rule.get("kind"),
                "violation_reason": rule.get("violation_reason"),
                "created_utc": rule.get("created_utc")
            })
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_subreddit_moderators(subreddit_name: str) -> List[Dict[str, Any]]:
    """
    Get moderators of a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
    
    Returns:
        List of subreddit moderators
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        moderators = subreddit.moderator()
        result = []
        for mod in moderators:
            result.append({
                "name": str(mod),
                "mod_permissions": mod.mod_permissions,
                "added_date": mod.date
            })
        return result
    except Exception as e:
        return [{"error": str(e)}]

# ============================================================================
# POST OPERATIONS
# ============================================================================

@mcp.tool()
def get_post(post_id: str) -> Dict[str, Any]:
    """
    Get details of a specific post
    
    Args:
        post_id: Reddit post ID or full URL
    
    Returns:
        Post details
    """
    reddit = init_reddit()
    try:
        if post_id.startswith("http"):
            submission = reddit.submission(url=post_id)
        else:
            submission = reddit.submission(id=post_id)
        
        return {
            "id": submission.id,
            "title": submission.title,
            "author": str(submission.author) if submission.author else "[deleted]",
            "subreddit": str(submission.subreddit),
            "created_utc": submission.created_utc,
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "num_comments": submission.num_comments,
            "url": submission.url,
            "selftext": submission.selftext,
            "permalink": f"https://reddit.com{submission.permalink}",
            "is_video": submission.is_video,
            "is_self": submission.is_self,
            "stickied": submission.stickied,
            "locked": submission.locked,
            "nsfw": submission.over_18,
            "spoiler": submission.spoiler,
            "distinguished": submission.distinguished,
            "link_flair_text": submission.link_flair_text,
            "author_flair_text": submission.author_flair_text,
            "gilded": submission.gilded,
            "total_awards_received": submission.total_awards_received,
            "edited": submission.edited,
            "num_crossposts": submission.num_crossposts,
            "view_count": submission.view_count
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_post_comments(post_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get all comments from a post
    
    Args:
        post_id: Reddit post ID or full URL
        limit: Maximum number of comments to retrieve (None for all)
    
    Returns:
        List of comments with nested replies
    """
    reddit = init_reddit()
    try:
        if post_id.startswith("http"):
            submission = reddit.submission(url=post_id)
        else:
            submission = reddit.submission(id=post_id)
        
        submission.comments.replace_more(limit=limit)
        
        def parse_comment(comment):
            if isinstance(comment, praw.models.MoreComments):
                return None
            
            return {
                "id": comment.id,
                "author": str(comment.author) if comment.author else "[deleted]",
                "body": comment.body,
                "score": comment.score,
                "created_utc": comment.created_utc,
                "edited": comment.edited,
                "is_submitter": comment.is_submitter,
                "stickied": comment.stickied,
                "distinguished": comment.distinguished,
                "gilded": comment.gilded,
                "replies": [parse_comment(reply) for reply in comment.replies if parse_comment(reply)]
            }
        
        comments = []
        for top_level_comment in submission.comments:
            parsed = parse_comment(top_level_comment)
            if parsed:
                comments.append(parsed)
        
        return comments
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def submit_text_post(
    subreddit_name: str,
    title: str,
    text: str,
    flair_id: Optional[str] = None,
    nsfw: bool = False,
    spoiler: bool = False
) -> Dict[str, Any]:
    """
    Submit a text post to a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
        title: Post title
        text: Post text content
        flair_id: Optional flair ID
        nsfw: Mark as NSFW
        spoiler: Mark as spoiler
    
    Returns:
        Submission details
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(
            title=title,
            selftext=text,
            flair_id=flair_id,
            nsfw=nsfw,
            spoiler=spoiler
        )
        
        return {
            "id": submission.id,
            "title": submission.title,
            "url": f"https://reddit.com{submission.permalink}",
            "created_utc": submission.created_utc
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def submit_link_post(
    subreddit_name: str,
    title: str,
    url: str,
    flair_id: Optional[str] = None,
    nsfw: bool = False,
    spoiler: bool = False
) -> Dict[str, Any]:
    """
    Submit a link post to a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
        title: Post title
        url: Link URL
        flair_id: Optional flair ID
        nsfw: Mark as NSFW
        spoiler: Mark as spoiler
    
    Returns:
        Submission details
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        submission = subreddit.submit(
            title=title,
            url=url,
            flair_id=flair_id,
            nsfw=nsfw,
            spoiler=spoiler
        )
        
        return {
            "id": submission.id,
            "title": submission.title,
            "url": f"https://reddit.com{submission.permalink}",
            "created_utc": submission.created_utc
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_post(post_id: str) -> Dict[str, Any]:
    """
    Delete a post (must be author)
    
    Args:
        post_id: Reddit post ID
    
    Returns:
        Deletion status
    """
    reddit = init_reddit()
    try:
        submission = reddit.submission(id=post_id)
        submission.delete()
        return {"success": True, "message": f"Post {post_id} deleted"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# COMMENT OPERATIONS
# ============================================================================

@mcp.tool()
def reply_to_post(post_id: str, text: str) -> Dict[str, Any]:
    """
    Reply to a post with a comment
    
    Args:
        post_id: Reddit post ID
        text: Comment text
    
    Returns:
        Comment details
    """
    reddit = init_reddit()
    try:
        submission = reddit.submission(id=post_id)
        comment = submission.reply(text)
        return {
            "id": comment.id,
            "body": comment.body,
            "permalink": f"https://reddit.com{comment.permalink}",
            "created_utc": comment.created_utc
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def reply_to_comment(comment_id: str, text: str) -> Dict[str, Any]:
    """
    Reply to a comment
    
    Args:
        comment_id: Reddit comment ID
        text: Reply text
    
    Returns:
        Reply details
    """
    reddit = init_reddit()
    try:
        comment = reddit.comment(id=comment_id)
        reply = comment.reply(text)
        return {
            "id": reply.id,
            "body": reply.body,
            "permalink": f"https://reddit.com{reply.permalink}",
            "created_utc": reply.created_utc
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def edit_comment(comment_id: str, text: str) -> Dict[str, Any]:
    """
    Edit a comment (must be author)
    
    Args:
        comment_id: Reddit comment ID
        text: New comment text
    
    Returns:
        Edit status
    """
    reddit = init_reddit()
    try:
        comment = reddit.comment(id=comment_id)
        comment.edit(text)
        return {"success": True, "message": f"Comment {comment_id} edited"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_comment(comment_id: str) -> Dict[str, Any]:
    """
    Delete a comment (must be author)
    
    Args:
        comment_id: Reddit comment ID
    
    Returns:
        Deletion status
    """
    reddit = init_reddit()
    try:
        comment = reddit.comment(id=comment_id)
        comment.delete()
        return {"success": True, "message": f"Comment {comment_id} deleted"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# USER OPERATIONS
# ============================================================================

@mcp.tool()
def get_user_info(username: str) -> Dict[str, Any]:
    """
    Get information about a Reddit user
    
    Args:
        username: Reddit username
    
    Returns:
        User profile information
    """
    reddit = init_reddit()
    try:
        user = reddit.redditor(username)
        return {
            "name": user.name,
            "id": user.id,
            "created_utc": user.created_utc,
            "link_karma": user.link_karma,
            "comment_karma": user.comment_karma,
            "total_karma": user.total_karma,
            "is_gold": user.is_gold,
            "is_mod": user.is_mod,
            "is_employee": user.is_employee,
            "has_verified_email": user.has_verified_email,
            "icon_img": user.icon_img,
            "subreddit": {
                "display_name": user.subreddit.display_name,
                "title": user.subreddit.title,
                "description": user.subreddit.public_description,
                "subscribers": user.subreddit.subscribers
            }
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_user_posts(username: str, sort: str = "new", limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get posts by a user
    
    Args:
        username: Reddit username
        sort: Sort method (new, top, hot)
        limit: Number of posts to retrieve
    
    Returns:
        List of user's posts
    """
    reddit = init_reddit()
    try:
        user = reddit.redditor(username)
        
        if sort == "new":
            submissions = user.submissions.new(limit=limit)
        elif sort == "top":
            submissions = user.submissions.top(limit=limit)
        elif sort == "hot":
            submissions = user.submissions.hot(limit=limit)
        else:
            return [{"error": "Invalid sort method"}]
        
        result = []
        for post in submissions:
            result.append({
                "id": post.id,
                "title": post.title,
                "subreddit": str(post.subreddit),
                "created_utc": post.created_utc,
                "score": post.score,
                "num_comments": post.num_comments,
                "url": post.url,
                "selftext": post.selftext[:200] if post.selftext else None,
                "permalink": f"https://reddit.com{post.permalink}"
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_user_comments(username: str, sort: str = "new", limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get comments by a user
    
    Args:
        username: Reddit username
        sort: Sort method (new, top, hot)
        limit: Number of comments to retrieve
    
    Returns:
        List of user's comments
    """
    reddit = init_reddit()
    try:
        user = reddit.redditor(username)
        
        if sort == "new":
            comments = user.comments.new(limit=limit)
        elif sort == "top":
            comments = user.comments.top(limit=limit)
        elif sort == "hot":
            comments = user.comments.hot(limit=limit)
        else:
            return [{"error": "Invalid sort method"}]
        
        result = []
        for comment in comments:
            result.append({
                "id": comment.id,
                "body": comment.body[:200],
                "subreddit": str(comment.subreddit),
                "created_utc": comment.created_utc,
                "score": comment.score,
                "permalink": f"https://reddit.com{comment.permalink}",
                "submission_title": comment.submission.title if hasattr(comment, 'submission') else None
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_user_karma(username: str) -> Dict[str, Any]:
    """
    Get karma breakdown by subreddit for a user
    
    Args:
        username: Reddit username
    
    Returns:
        Karma breakdown by subreddit
    """
    reddit = init_reddit()
    try:
        user = reddit.redditor(username)
        karma = user.karma()
        
        result = {
            "total_karma": user.total_karma,
            "link_karma": user.link_karma,
            "comment_karma": user.comment_karma,
            "subreddit_karma": {}
        }
        
        for subreddit, karma_dict in karma.items():
            result["subreddit_karma"][str(subreddit)] = {
                "link_karma": karma_dict['link_karma'],
                "comment_karma": karma_dict['comment_karma']
            }
        
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_my_saved(limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get saved posts and comments for authenticated user
    
    Args:
        limit: Number of items to retrieve
    
    Returns:
        List of saved items
    """
    reddit = init_reddit()
    try:
        saved = reddit.user.me().saved(limit=limit)
        result = []
        
        for item in saved:
            if isinstance(item, Submission):
                result.append({
                    "type": "post",
                    "id": item.id,
                    "title": item.title,
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc,
                    "permalink": f"https://reddit.com{item.permalink}"
                })
            elif isinstance(item, Comment):
                result.append({
                    "type": "comment",
                    "id": item.id,
                    "body": item.body[:200],
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc,
                    "permalink": f"https://reddit.com{item.permalink}"
                })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_my_upvoted(limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get upvoted posts and comments for authenticated user
    
    Args:
        limit: Number of items to retrieve
    
    Returns:
        List of upvoted items
    """
    reddit = init_reddit()
    try:
        upvoted = reddit.user.me().upvoted(limit=limit)
        result = []
        
        for item in upvoted:
            if isinstance(item, Submission):
                result.append({
                    "type": "post",
                    "id": item.id,
                    "title": item.title,
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc,
                    "permalink": f"https://reddit.com{item.permalink}"
                })
            elif isinstance(item, Comment):
                result.append({
                    "type": "comment",
                    "id": item.id,
                    "body": item.body[:200],
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc,
                    "permalink": f"https://reddit.com{item.permalink}"
                })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_my_downvoted(limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get downvoted posts and comments for authenticated user
    
    Args:
        limit: Number of items to retrieve
    
    Returns:
        List of downvoted items
    """
    reddit = init_reddit()
    try:
        downvoted = reddit.user.me().downvoted(limit=limit)
        result = []
        
        for item in downvoted:
            if isinstance(item, Submission):
                result.append({
                    "type": "post",
                    "id": item.id,
                    "title": item.title,
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc,
                    "permalink": f"https://reddit.com{item.permalink}"
                })
            elif isinstance(item, Comment):
                result.append({
                    "type": "comment",
                    "id": item.id,
                    "body": item.body[:200],
                    "subreddit": str(item.subreddit),
                    "score": item.score,
                    "created_utc": item.created_utc,
                    "permalink": f"https://reddit.com{item.permalink}"
                })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

# ============================================================================
# VOTING AND INTERACTION OPERATIONS
# ============================================================================

@mcp.tool()
def upvote(item_id: str, item_type: str = "post") -> Dict[str, Any]:
    """
    Upvote a post or comment
    
    Args:
        item_id: Reddit post or comment ID
        item_type: Type of item ("post" or "comment")
    
    Returns:
        Vote status
    """
    reddit = init_reddit()
    try:
        if item_type == "post":
            item = reddit.submission(id=item_id)
        elif item_type == "comment":
            item = reddit.comment(id=item_id)
        else:
            return {"error": "Invalid item_type. Use 'post' or 'comment'"}
        
        item.upvote()
        return {"success": True, "message": f"{item_type} {item_id} upvoted"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def downvote(item_id: str, item_type: str = "post") -> Dict[str, Any]:
    """
    Downvote a post or comment
    
    Args:
        item_id: Reddit post or comment ID
        item_type: Type of item ("post" or "comment")
    
    Returns:
        Vote status
    """
    reddit = init_reddit()
    try:
        if item_type == "post":
            item = reddit.submission(id=item_id)
        elif item_type == "comment":
            item = reddit.comment(id=item_id)
        else:
            return {"error": "Invalid item_type. Use 'post' or 'comment'"}
        
        item.downvote()
        return {"success": True, "message": f"{item_type} {item_id} downvoted"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def clear_vote(item_id: str, item_type: str = "post") -> Dict[str, Any]:
    """
    Clear vote on a post or comment
    
    Args:
        item_id: Reddit post or comment ID
        item_type: Type of item ("post" or "comment")
    
    Returns:
        Vote status
    """
    reddit = init_reddit()
    try:
        if item_type == "post":
            item = reddit.submission(id=item_id)
        elif item_type == "comment":
            item = reddit.comment(id=item_id)
        else:
            return {"error": "Invalid item_type. Use 'post' or 'comment'"}
        
        item.clear_vote()
        return {"success": True, "message": f"Vote cleared on {item_type} {item_id}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def save_item(item_id: str, item_type: str = "post") -> Dict[str, Any]:
    """
    Save a post or comment
    
    Args:
        item_id: Reddit post or comment ID
        item_type: Type of item ("post" or "comment")
    
    Returns:
        Save status
    """
    reddit = init_reddit()
    try:
        if item_type == "post":
            item = reddit.submission(id=item_id)
        elif item_type == "comment":
            item = reddit.comment(id=item_id)
        else:
            return {"error": "Invalid item_type. Use 'post' or 'comment'"}
        
        item.save()
        return {"success": True, "message": f"{item_type} {item_id} saved"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def unsave_item(item_id: str, item_type: str = "post") -> Dict[str, Any]:
    """
    Unsave a post or comment
    
    Args:
        item_id: Reddit post or comment ID
        item_type: Type of item ("post" or "comment")
    
    Returns:
        Unsave status
    """
    reddit = init_reddit()
    try:
        if item_type == "post":
            item = reddit.submission(id=item_id)
        elif item_type == "comment":
            item = reddit.comment(id=item_id)
        else:
            return {"error": "Invalid item_type. Use 'post' or 'comment'"}
        
        item.unsave()
        return {"success": True, "message": f"{item_type} {item_id} unsaved"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def hide_post(post_id: str) -> Dict[str, Any]:
    """
    Hide a post from feed
    
    Args:
        post_id: Reddit post ID
    
    Returns:
        Hide status
    """
    reddit = init_reddit()
    try:
        submission = reddit.submission(id=post_id)
        submission.hide()
        return {"success": True, "message": f"Post {post_id} hidden"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def unhide_post(post_id: str) -> Dict[str, Any]:
    """
    Unhide a post
    
    Args:
        post_id: Reddit post ID
    
    Returns:
        Unhide status
    """
    reddit = init_reddit()
    try:
        submission = reddit.submission(id=post_id)
        submission.unhide()
        return {"success": True, "message": f"Post {post_id} unhidden"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# SEARCH OPERATIONS
# ============================================================================

@mcp.tool()
def search_all_reddit(
    query: str,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 25
) -> List[Dict[str, Any]]:
    """
    Search across all of Reddit
    
    Args:
        query: Search query
        sort: Sort method (relevance, hot, top, new, comments)
        time_filter: Time filter (hour, day, week, month, year, all)
        limit: Number of results to return
    
    Returns:
        List of search results
    """
    reddit = init_reddit()
    try:
        results = reddit.subreddit("all").search(
            query, 
            sort=sort, 
            time_filter=time_filter, 
            limit=limit
        )
        
        result = []
        for post in results:
            result.append({
                "id": post.id,
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "subreddit": str(post.subreddit),
                "created_utc": post.created_utc,
                "score": post.score,
                "num_comments": post.num_comments,
                "url": post.url,
                "selftext": post.selftext[:200] if post.selftext else None,
                "permalink": f"https://reddit.com{post.permalink}"
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def search_in_subreddit(
    subreddit_name: str,
    query: str,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 25
) -> List[Dict[str, Any]]:
    """
    Search within a specific subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
        query: Search query
        sort: Sort method (relevance, hot, top, new, comments)
        time_filter: Time filter (hour, day, week, month, year, all)
        limit: Number of results to return
    
    Returns:
        List of search results
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        results = subreddit.search(
            query, 
            sort=sort, 
            time_filter=time_filter, 
            limit=limit
        )
        
        result = []
        for post in results:
            result.append({
                "id": post.id,
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "created_utc": post.created_utc,
                "score": post.score,
                "num_comments": post.num_comments,
                "url": post.url,
                "selftext": post.selftext[:200] if post.selftext else None,
                "permalink": f"https://reddit.com{post.permalink}"
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def search_users(query: str, limit: int = 25) -> List[Dict[str, Any]]:
    """
    Search for Reddit users
    
    Args:
        query: Search query for username
        limit: Number of results to return
    
    Returns:
        List of matching users
    """
    reddit = init_reddit()
    try:
        # PRAW doesn't have direct user search, so we search in r/all for the user
        # This is a workaround - for exact user match, use get_user_info
        results = reddit.subreddits.search_by_name(query, include_nsfw=True)
        
        result = []
        for item in results:
            result.append({
                "name": item,
                "url": f"https://reddit.com/u/{item}"
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

# ============================================================================
# MESSAGING OPERATIONS
# ============================================================================

@mcp.tool()
def get_inbox(filter_type: str = "all", limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get inbox messages
    
    Args:
        filter_type: Filter type (all, unread, messages, comments, mentions)
        limit: Number of messages to retrieve
    
    Returns:
        List of inbox messages
    """
    reddit = init_reddit()
    try:
        if filter_type == "all":
            messages = reddit.inbox.all(limit=limit)
        elif filter_type == "unread":
            messages = reddit.inbox.unread(limit=limit)
        elif filter_type == "messages":
            messages = reddit.inbox.messages(limit=limit)
        elif filter_type == "comments":
            messages = reddit.inbox.comment_replies(limit=limit)
        elif filter_type == "mentions":
            messages = reddit.inbox.mentions(limit=limit)
        else:
            return [{"error": "Invalid filter_type"}]
        
        result = []
        for message in messages:
            result.append({
                "id": message.id,
                "subject": getattr(message, 'subject', None),
                "body": message.body,
                "author": str(message.author) if message.author else None,
                "created_utc": message.created_utc,
                "was_comment": message.was_comment,
                "new": message.new,
                "type": message.type,
                "parent_id": message.parent_id if hasattr(message, 'parent_id') else None
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def send_message(username: str, subject: str, message: str) -> Dict[str, Any]:
    """
    Send a private message to a user
    
    Args:
        username: Recipient username
        subject: Message subject
        message: Message body
    
    Returns:
        Send status
    """
    reddit = init_reddit()
    try:
        reddit.redditor(username).message(subject, message)
        return {"success": True, "message": f"Message sent to {username}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def mark_message_read(message_id: str) -> Dict[str, Any]:
    """
    Mark a message as read
    
    Args:
        message_id: Message ID
    
    Returns:
        Status
    """
    reddit = init_reddit()
    try:
        message = reddit.inbox.message(message_id)
        message.mark_read()
        return {"success": True, "message": f"Message {message_id} marked as read"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def mark_message_unread(message_id: str) -> Dict[str, Any]:
    """
    Mark a message as unread
    
    Args:
        message_id: Message ID
    
    Returns:
        Status
    """
    reddit = init_reddit()
    try:
        message = reddit.inbox.message(message_id)
        message.mark_unread()
        return {"success": True, "message": f"Message {message_id} marked as unread"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# SUBSCRIPTION AND FOLLOWING OPERATIONS
# ============================================================================

@mcp.tool()
def subscribe_subreddit(subreddit_name: str) -> Dict[str, Any]:
    """
    Subscribe to a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
    
    Returns:
        Subscription status
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        subreddit.subscribe()
        return {"success": True, "message": f"Subscribed to r/{subreddit_name}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def unsubscribe_subreddit(subreddit_name: str) -> Dict[str, Any]:
    """
    Unsubscribe from a subreddit
    
    Args:
        subreddit_name: Name of the subreddit (without r/)
    
    Returns:
        Unsubscription status
    """
    reddit = init_reddit()
    try:
        subreddit = reddit.subreddit(subreddit_name)
        subreddit.unsubscribe()
        return {"success": True, "message": f"Unsubscribed from r/{subreddit_name}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_my_subscriptions(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get list of subscribed subreddits
    
    Args:
        limit: Number of subscriptions to retrieve
    
    Returns:
        List of subscribed subreddits
    """
    reddit = init_reddit()
    try:
        subscriptions = reddit.user.subreddits(limit=limit)
        result = []
        
        for sub in subscriptions:
            result.append({
                "name": sub.display_name,
                "title": sub.title,
                "description": sub.public_description,
                "subscribers": sub.subscribers,
                "url": f"https://reddit.com{sub.url}"
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def follow_user(username: str) -> Dict[str, Any]:
    """
    Follow a Reddit user
    
    Args:
        username: Username to follow
    
    Returns:
        Follow status
    """
    reddit = init_reddit()
    try:
        # Follow user by subscribing to their profile subreddit
        user = reddit.redditor(username)
        user.subreddit.subscribe()
        return {"success": True, "message": f"Now following u/{username}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def unfollow_user(username: str) -> Dict[str, Any]:
    """
    Unfollow a Reddit user
    
    Args:
        username: Username to unfollow
    
    Returns:
        Unfollow status
    """
    reddit = init_reddit()
    try:
        # Unfollow user by unsubscribing from their profile subreddit
        user = reddit.redditor(username)
        user.subreddit.unsubscribe()
        return {"success": True, "message": f"Unfollowed u/{username}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# ADDITIONAL REDDIT OPERATIONS
# ============================================================================

@mcp.tool()
def get_trending_subreddits() -> List[Dict[str, Any]]:
    """
    Get trending subreddits
    
    Returns:
        List of trending subreddits
    """
    reddit = init_reddit()
    try:
        # Get popular subreddits as trending
        trending = reddit.subreddits.popular(limit=10)
        result = []
        
        for sub in trending:
            result.append({
                "name": sub.display_name,
                "title": sub.title,
                "description": sub.public_description,
                "subscribers": sub.subscribers,
                "active_users": sub.active_user_count,
                "url": f"https://reddit.com{sub.url}"
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_front_page(sort: str = "hot", limit: int = 25) -> List[Dict[str, Any]]:
    """
    Get posts from authenticated user's front page
    
    Args:
        sort: Sort method (hot, new, top, rising, controversial)
        limit: Number of posts to retrieve
    
    Returns:
        List of front page posts
    """
    reddit = init_reddit()
    try:
        if sort == "hot":
            posts = reddit.front.hot(limit=limit)
        elif sort == "new":
            posts = reddit.front.new(limit=limit)
        elif sort == "top":
            posts = reddit.front.top(limit=limit)
        elif sort == "rising":
            posts = reddit.front.rising(limit=limit)
        elif sort == "controversial":
            posts = reddit.front.controversial(limit=limit)
        else:
            return [{"error": "Invalid sort method"}]
        
        result = []
        for post in posts:
            result.append({
                "id": post.id,
                "title": post.title,
                "author": str(post.author) if post.author else "[deleted]",
                "subreddit": str(post.subreddit),
                "created_utc": post.created_utc,
                "score": post.score,
                "upvote_ratio": post.upvote_ratio,
                "num_comments": post.num_comments,
                "url": post.url,
                "selftext": post.selftext[:200] if post.selftext else None,
                "permalink": f"https://reddit.com{post.permalink}",
                "nsfw": post.over_18,
                "spoiler": post.spoiler
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_my_multireddits() -> List[Dict[str, Any]]:
    """
    Get authenticated user's multireddits (custom feeds)
    
    Returns:
        List of multireddits
    """
    reddit = init_reddit()
    try:
        multireddits = reddit.user.me().multireddits()
        result = []
        
        for multi in multireddits:
            result.append({
                "name": multi.name,
                "display_name": multi.display_name,
                "description": multi.description_md,
                "subreddits": [str(sub) for sub in multi.subreddits],
                "visibility": multi.visibility,
                "path": multi.path,
                "created_utc": multi.created_utc
            })
        
        return result
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def get_random_post(subreddit_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get a random post from Reddit or a specific subreddit
    
    Args:
        subreddit_name: Optional subreddit name (without r/). If None, gets random from all
    
    Returns:
        Random post details
    """
    reddit = init_reddit()
    try:
        if subreddit_name:
            submission = reddit.subreddit(subreddit_name).random()
        else:
            submission = reddit.random_subreddit().random()
        
        if submission is None:
            return {"error": "No random post available"}
        
        return {
            "id": submission.id,
            "title": submission.title,
            "author": str(submission.author) if submission.author else "[deleted]",
            "subreddit": str(submission.subreddit),
            "created_utc": submission.created_utc,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "url": submission.url,
            "selftext": submission.selftext,
            "permalink": f"https://reddit.com{submission.permalink}",
            "nsfw": submission.over_18,
            "spoiler": submission.spoiler
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    # The transport will be determined by fastmcp based on how it's invoked
    # - Local: python reddit-mcp-server.py (uses stdio)
    # - Cloud: fastmcp run reddit-mcp-server.py --host 0.0.0.0 (uses SSE)
    mcp.run()