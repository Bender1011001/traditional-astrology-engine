import re

def clean_tweet_text(text: str) -> str:
    """Removes extra whitespace and ensures text clean."""
    return re.sub(r'\s+', ' ', text).strip()

def split_into_thread(text: str, limit: int = 280) -> list[str]:
    """Splits a long text into a Twitter thread."""
    words = text.split()
    tweets = []
    current_tweet = ""

    for word in words:
        if len(current_tweet) + len(word) + 1 <= limit:
            current_tweet += (word + " ")
        else:
            tweets.append(current_tweet.strip())
            current_tweet = word + " "
    
    if current_tweet:
        tweets.append(current_tweet.strip())
    
    # Add numbering
    if len(tweets) > 1:
        return [f"{t} ({i+1}/{len(tweets)})" for i, t in enumerate(tweets)]
    
    return tweets
