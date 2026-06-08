from pathlib import Path
from bs4 import BeautifulSoup

HTML_DIR = Path("documents/raw_html")
RAW_DIR = Path("documents/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "Best apartments for students off campus_ _ wsu.html": "reddit_best_apartments_off_campus.txt",
    "Least terrible apartment complex _ wsu.html": "reddit_least_terrible_apartment_complex.txt",
    "Housing _ wsu.html": "reddit_housing.txt",
    "Anyone know reputable one bedroom apartments in Pullman_ _ wsu.html": "reddit_reputable_one_bedroom_apartments.txt",
    "Best One Bedroom Apartments _ wsu.html": "reddit_best_one_bedroom_apartments.txt",
    "Apartment Recommendations _ wsu.html": "reddit_apartment_recommendations.txt",
    "Help me evalaute living and rental cost aroud WSU _ wsu.html": "reddit_living_rental_cost_wsu.txt",
    "Is DABCO really that bad..__ (looking at churchill downs) _ wsu.html": "reddit_dabco_churchill_downs.txt",
    "Moving off campus before entering housing contract _ wsu.html": "reddit_moving_off_campus_housing_contract.txt",
    "Looking into Apartments _ wsu.html": "reddit_looking_into_apartments.txt",
    "Housing Questions _ wsu.html": "reddit_housing_questions.txt",
}


def extract_old_reddit_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    output = []

    title = soup.find("a", class_="title")
    if title:
        output.append("Title:")
        output.append(title.get_text(" ", strip=True))
        output.append("")

    # Old Reddit post body and comments usually appear in div.usertext-body
    bodies = soup.find_all("div", class_="usertext-body")

    output.append("Post and Comments:")
    for i, body in enumerate(bodies, start=1):
        text = body.get_text("\n", strip=True)

        if not text:
            continue

        boilerplate_phrases = [
            "A place to post anything about WSU",
            "Use of flair highly encouraged",
            "FLAIR GUIDELINES",
            "CONTACT THE MODS",
            "Message the moderators",
            "Apply to be a mod",
        ]

        if any(phrase in text for phrase in boilerplate_phrases):
            continue

        # Skip common empty/removed artifacts
        if text.lower() in {"[deleted]", "[removed]"}:
            continue

        output.append("")
        output.append(f"Entry {i}:")
        output.append(text)

    return "\n".join(output).strip()


def main():
    for html_name, txt_name in FILES.items():
        html_path = HTML_DIR / html_name
        txt_path = RAW_DIR / txt_name

        if not html_path.exists():
            print(f"Missing: {html_path}")
            continue

        html = html_path.read_text(encoding="utf-8", errors="ignore")
        text = extract_old_reddit_text(html)

        if not text:
            print(f"No text extracted from {html_path}")
            continue

        txt_path.write_text(text, encoding="utf-8")
        print(f"Saved {txt_path}")


if __name__ == "__main__":
    main()