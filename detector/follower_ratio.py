def is_ratio_suspicious(followers, following):
    try:
        followers = int(followers)
        following = int(following)
        if following == 0:  # Prevent division by zero
            return False
        ratio = followers / following
        return ratio < 0.5 or ratio > 10  # Example: Very low or very high ratio
    except ValueError:
        return False
