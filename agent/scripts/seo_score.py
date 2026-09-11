from bs4 import BeautifulSoup
def score_page(html_file):
    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f, 'html.parser')
    score = 100
    if not soup.find("title"): score -= 20
    if not soup.find("meta", attrs={"name": "description"}): score -= 20
    if not soup.find("h1"): score -= 15
    return score
