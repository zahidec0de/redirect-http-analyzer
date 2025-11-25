import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def analyze_website(url, max_redirects=5, timeout=8):
    result = {
        "target_url": url,
        "redirect_chain": [],
        "redirect_chain_contains_http": False,
        "static_insecure_links": [],
        "errors": []
    }

    # -------------------------------
    # 1) Follow Redirect Chain
    # -------------------------------
    session = requests.Session()
    current_url = url

    try:
        for _ in range(max_redirects):
            response = session.get(current_url, allow_redirects=False, timeout=timeout)

            result["redirect_chain"].append({
                "url": current_url,
                "status": response.status_code
            })

            # Check if redirect
            if response.is_redirect or response.is_permanent_redirect:
                loc = response.headers.get("Location", "")
                new_url = urljoin(current_url, loc)

                if new_url.startswith("http://"):
                    result["redirect_chain_contains_http"] = True

                current_url = new_url
            else:
                break

    except Exception as e:
        result["errors"].append(f"Redirect error: {str(e)}")
        return result

    final_page_url = current_url

    # -------------------------------
    # 2) Fetch Final Page HTML
    # -------------------------------
    try:
        final_response = session.get(final_page_url, timeout=timeout)
        html = final_response.text
    except Exception as e:
        result["errors"].append(f"Failed to fetch final page: {str(e)}")
        return result

    # -------------------------------
    # 3) Parse Static HTML for <a href>
    # -------------------------------
    try:
        soup = BeautifulSoup(html, "html.parser")

        # All <a href=""> links
        for tag in soup.find_all("a", href=True):
            link = tag["href"]
            absolute = urljoin(final_page_url, link)

            if absolute.startswith("http://"):
                result["static_insecure_links"].append(absolute)

        # meta refresh
        for tag in soup.find_all("meta", attrs={"http-equiv": "refresh"}):
            content = tag.get("content", "")
            if "url=" in content.lower():
                refresh_url = content.split("url=")[-1].strip()
                absolute = urljoin(final_page_url, refresh_url)
                if absolute.startswith("http://"):
                    result["static_insecure_links"].append(absolute)

    except Exception as e:
        result["errors"].append(f"HTML parse error: {str(e)}")

    return result


# ---------------------------
# Usage
# ---------------------------
if __name__ == "__main__":
    test_url = "https://example.com"
    result = analyze_website(test_url)

    print(f"\nTarget: {result['target_url']}")
    print(f"Redirect Chain:")
    for step in result["redirect_chain"]:
        print(f"  - {step['status']} → {step['url']}")

    print(f"\nRedirect Chain Contains HTTP? {result['redirect_chain_contains_http']}")

    print("\nStatic Insecure Links Found:")
    for link in result["static_insecure_links"]:
        print(f"  - {link}")

    print("\nErrors:")
    for err in result["errors"]:
        print(f"  - {err}")

    print("\n--- JSON OUTPUT ---")
    import json
    print(json.dumps(result, indent=4))
