from detector.twitter_scraper import get_user_profile
from detector.profile_analyzer import ProfileAnalyzer
from colorama import Fore, Style
import sys

profile_analyzer = ProfileAnalyzer()


def calculate_credibility_score(profile):
    score = 0
    explanations = []

    # 1. Profile Picture Analysis
    if profile.get("picture_analysis"):
        analysis = profile["picture_analysis"]
        risk = analysis.get("credibility_risk", 0)

        if risk > 3:
            deduction = min(3, risk)
            score -= deduction
            reasons = ", ".join(analysis.get("red_flags", ["suspicious characteristics"]))
            explanations.append(f"Deducted {deduction} points: Profile picture - {reasons}")
        else:
            score += 2
            explanations.append("Added 2 points: Verified authentic profile picture")

    # 2. Profile Completeness
    bio = profile.get("bio", "")
    if not bio:
        score -= 2
        explanations.append("Deducted 2 points: Missing profile bio")
    else:
        score += 1
        explanations.append("Added 1 point: Profile bio exists")
        if len(bio) > 20:
            score += 1
            explanations.append("Added 1 point: Detailed bio (20+ chars)")

    # 3. Follower Analysis
    followers = profile.get("followers", 0)
    following = profile.get("following", 1)
    ratio = followers / following

    if ratio == 0:
        score -= 2
        explanations.append("Deducted 2 points: Zero followers")
    elif 0.5 <= ratio <= 2:
        score += 3
        explanations.append("Added 3 points: Healthy follower ratio (0.5-2.0)")
    elif ratio < 0.1:
        score -= 3
        explanations.append("Deducted 3 points: Extremely low follower ratio (<0.1)")
    elif ratio > 10:
        score -= 1
        explanations.append("Deducted 1 point: Very high follower ratio (>10)")

    # 4. Bio Content Analysis
    bio_flags = len(profile["bio_analysis"].get("suspicious_keywords", []))
    if bio_flags > 0:
        deduction = min(3, bio_flags)
        score -= deduction
        keywords = ", ".join(profile["bio_analysis"]["suspicious_keywords"])
        explanations.append(f"Deducted {deduction} points: Suspicious bio keywords - {keywords}")

    # Ensure score stays within bounds
    score = max(0, min(10, score))

    return score, explanations


def generate_recommendations(profile, score):
    recs = []

    if not profile.get("bio", ""):
        recs.append("Add a profile bio to gain 2-3 points")
    elif len(profile["bio"]) < 20:
        recs.append("Expand your bio to 20+ characters for +1 point")

    if profile.get("followers", 0) < 100:
        recs.append("Engage with similar accounts to grow followers")

    if score < 7:
        recs.append("Verify email/phone with Twitter for trust boost")

    return recs


def print_analysis_report(profile, score, explanations):
    # Determine credibility level
    if score >= 8:
        level = f"{Fore.GREEN}High{Style.RESET_ALL}"
    elif score >= 5:
        level = f"{Fore.YELLOW}Medium{Style.RESET_ALL}"
    else:
        level = f"{Fore.RED}Low{Style.RESET_ALL}"

    # Print header
    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}🐦 TWITTER CREDIBILITY ANALYSIS: @{profile['username']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

    # Profile overview
    print(f"\n{Fore.WHITE}🔍 PROFILE OVERVIEW{Style.RESET_ALL}")
    print(f"• Bio: {Fore.YELLOW}{profile.get('bio', '[No bio available]')[:100]}{Style.RESET_ALL}")
    print(f"• Followers: {Fore.CYAN}{profile.get('followers', 0):,}{Style.RESET_ALL}")
    print(f"• Following: {Fore.CYAN}{profile.get('following', 0):,}{Style.RESET_ALL}")

    # Profile picture analysis
    if profile.get("picture_analysis"):
        print(f"\n{Fore.WHITE}🖼️ PROFILE PICTURE ANALYSIS{Style.RESET_ALL}")
        analysis = profile["picture_analysis"]
        if analysis.get("is_ai", False):
            print(f"• {Fore.RED}⚠️ WARNING: AI-generated characteristics detected{Style.RESET_ALL}")
        else:
            print(f"• {Fore.GREEN}✓ Authentic human face verified{Style.RESET_ALL}")

        if analysis.get("red_flags"):
            print(f"• {Fore.YELLOW}🚩 Flags: {', '.join(analysis['red_flags'])}{Style.RESET_ALL}")

    # Score breakdown
    print(f"\n{Fore.WHITE}📊 CREDIBILITY SCORE: {Fore.CYAN}{score}/10 {Style.RESET_ALL}({level}{Style.RESET_ALL})")
    print(f"\n{Fore.WHITE}🔧 SCORE BREAKDOWN:{Style.RESET_ALL}")
    for item in explanations:
        if "Deducted" in item:
            print(f"• {Fore.RED}➖ {item}{Style.RESET_ALL}")
        else:
            print(f"• {Fore.GREEN}➕ {item}{Style.RESET_ALL}")

    # Recommendations
    recs = generate_recommendations(profile, score)
    if recs:
        print(f"\n{Fore.WHITE}💡 RECOMMENDATIONS TO IMPROVE:{Style.RESET_ALL}")
        for rec in recs:
            print(f"• {Fore.BLUE}✨ {rec}{Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")


def run_check(profile):
    if not profile:
        print(f"{Fore.RED}Error: Could not retrieve profile{Style.RESET_ALL}")
        return

    score, explanations = calculate_credibility_score(profile)
    print_analysis_report(profile, score, explanations)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter Twitter username (without @): ").strip()

    print(f"\n{Fore.YELLOW}🔍 Scanning @{username}...{Style.RESET_ALL}")
    profile = get_user_profile(username)
    run_check(profile)