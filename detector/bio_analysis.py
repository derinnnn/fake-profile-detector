# detector/bio_analysis.py
import re


def analyze_bio(bio):
    if not bio:
        return {
            "suspicious_categories": [],
            "keyword_matches": [],
            "emoji_count": 0,
            "is_flagged": False
        }

    suspicious_patterns = {
        "financial": r"(crypto|bitcoin|ether(eum)?|usdt|trading|invest|forex|pump|dump|wallet)",
        "scammy": r"(giveaway|free|reward|claim|airdrop|limited|offer|bonus)",
        "fake_engagement": r"(follow|like|retweet|comment|tag|share|dm|direct message)",
        "urgency": r"(quick|fast|now|today|immediately|hurry|limited time)"
    }

    results = {
        "suspicious_categories": [],
        "keyword_matches": [],
        "emoji_count": len(re.findall(r'[^\w\s,.]', bio)),
        "is_flagged": False
    }

    bio_lower = bio.lower()

    for category, pattern in suspicious_patterns.items():
        if re.search(pattern, bio_lower):
            results["suspicious_categories"].append(category)
            results["is_flagged"] = True

    return results