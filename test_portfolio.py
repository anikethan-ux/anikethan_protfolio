"""
Playwright test suite for the data-driven portfolio (index.html + data.json).

Setup (run once):
    pip install pytest-playwright
    playwright install chromium

Run:
    # from the portfolio folder, serve it first (fetch() needs http, not file://)
    python -m http.server 8000 &
    pytest test_portfolio.py -v

The tests read data.json directly so they stay correct even after you edit
your content (projects, skills, etc.) — no hardcoded expected values that
would break every time you update your resume info.
"""

import json
import re
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8000"
DATA_PATH = Path(__file__).parent / "data" / "data.json"


@pytest.fixture(scope="session")
def data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture()
def loaded_page(page: Page):
    page.goto(BASE_URL)
    # Wait for JS to fetch data.json and render the DOM
    page.wait_for_selector("#about", timeout=10_000)
    return page


class TestDataFile:
    """Sanity checks on data.json itself, independent of the browser."""

    def test_json_is_valid(self, data):
        assert isinstance(data, dict)

    def test_required_top_level_keys(self, data):
        for key in ["profile", "about", "education", "experience", "projects",
                    "achievements", "skills", "contactForm"]:
            assert key in data, f"Missing top-level key: {key}"

    def test_experience_entries_have_required_fields(self, data):
        for i, exp in enumerate(data["experience"]):
            for field in ["company", "role", "duration", "summary"]:
                assert exp.get(field), f"experience[{i}].{field} is missing/empty"
            assert isinstance(exp.get("points"), list) and exp["points"], \
                f"experience[{i}] needs at least one point"

    def test_profile_has_required_fields(self, data):
        profile = data["profile"]
        for field in ["name", "title", "email", "linkedin", "phone", "phoneDisplay"]:
            assert profile.get(field), f"profile.{field} is missing/empty"

    def test_email_format(self, data):
        email = data["profile"]["email"]
        assert re.match(r"[^@]+@[^@]+\.[^@]+", email), f"Invalid email: {email}"

    def test_projects_have_required_fields(self, data):
        for i, proj in enumerate(data["projects"]):
            assert proj.get("title"), f"projects[{i}] missing title"
            assert proj.get("summary"), f"projects[{i}] missing summary"
            assert isinstance(proj.get("points"), list) and proj["points"], \
                f"projects[{i}] needs at least one point"

    def test_skills_groups_have_items(self, data):
        for group in data["skills"]:
            assert group.get("id")
            assert group.get("items")


class TestPageLoad:
    def test_page_loads_without_console_errors(self, page: Page):
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(BASE_URL)
        page.wait_for_selector("#about", timeout=10_000)
        assert not errors, f"Console errors: {errors}"

    def test_header_renders_from_data(self, loaded_page, data):
        expect(loaded_page.locator("h1")).to_contain_text(data["profile"]["name"])

    def test_data_json_is_fetched_not_hardcoded(self, page: Page):
        # Block data/data.json and confirm the page shows the graceful error state
        page.route("**/data/data.json", lambda route: route.abort())
        page.goto(BASE_URL)
        expect(page.locator("#main-content")).to_contain_text("Couldn't load data/data.json", timeout=10_000)


class TestSections:
    def test_all_sections_present(self, loaded_page):
        for section_id in ["about", "education", "experience", "projects",
                            "achievements", "skills", "contact"]:
            expect(loaded_page.locator(f"#{section_id}")).to_be_visible()

    def test_experience_table_rows_match_data(self, loaded_page, data):
        rows = loaded_page.locator("#experience .exp-table tbody tr.exp-row")
        expect(rows).to_have_count(len(data["experience"]))
        for exp in data["experience"]:
            expect(loaded_page.locator("#experience")).to_contain_text(exp["company"])
            expect(loaded_page.locator("#experience")).to_contain_text(exp["role"])

    def test_project_count_matches_data(self, loaded_page, data):
        cards = loaded_page.locator("#projects > div")
        expect(cards).to_have_count(len(data["projects"]))

    def test_project_titles_match_data(self, loaded_page, data):
        for proj in data["projects"]:
            expect(loaded_page.locator("#projects")).to_contain_text(proj["title"])

    def test_skill_groups_match_data(self, loaded_page, data):
        for group in data["skills"]:
            expect(loaded_page.locator("#skills")).to_contain_text(
                re.sub(r"[^\w\s]", "", group["label"]).strip()
            )

    def test_contact_links_correct(self, loaded_page, data):
        profile = data["profile"]
        expect(loaded_page.locator(f'a[href="mailto:{profile["email"]}"]').first).to_be_visible()
        expect(loaded_page.locator(f'a[href="tel:{profile["phone"]}"]').first).to_be_visible()


class TestInteractivity:
    def test_project_details_toggle(self, loaded_page):
        first_project = loaded_page.locator("#projects > div").first
        toggle_btn = first_project.locator(".toggle-btn").last  # last = "View Details" (first may be "Visit Project" link)
        details = first_project.locator(".details")

        expect(details).to_be_hidden()
        toggle_btn.click()
        expect(details).to_be_visible()
        toggle_btn.click()
        expect(details).to_be_hidden()

    def test_skill_group_toggle(self, loaded_page):
        first_group = loaded_page.locator("#skills > div").first
        toggle_btn = first_group.locator(".toggle-btn")
        details = first_group.locator(".details")

        expect(details).to_be_hidden()
        toggle_btn.click()
        expect(details).to_be_visible()

    def test_contact_form_success_flow(self, page: Page, data):
        # Mock Web3Forms so this test doesn't require a real network call
        page.route("**/api.web3forms.com/**", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"success": true, "message": "Email sent successfully!"}'
        ))
        page.goto(BASE_URL)
        page.wait_for_selector("#contact-form", timeout=10_000)

        page.fill("#cf-name", "Test User")
        page.fill("#cf-email", "test@example.com")
        page.fill("#cf-message", "Hello, this is a test message.")
        page.click("#contact-form button[type=submit]")

        expect(page.locator("#cf-status")).to_contain_text(
            data["contactForm"]["successMessage"], timeout=5_000
        )

    def test_contact_form_error_flow(self, page: Page, data):
        page.route("**/api.web3forms.com/**", lambda route: route.fulfill(
            status=400,
            content_type="application/json",
            body='{"success": false, "message": "Server error"}'
        ))
        page.goto(BASE_URL)
        page.wait_for_selector("#contact-form", timeout=10_000)

        page.fill("#cf-name", "Test User")
        page.fill("#cf-email", "test@example.com")
        page.fill("#cf-message", "Hello, this is a test message.")
        page.click("#contact-form button[type=submit]")

        expect(page.locator("#cf-status")).to_contain_text("Server error", timeout=5_000)

    def test_project_external_link_opens_correct_url(self, loaded_page, data):
        linked_projects = [p for p in data["projects"] if p.get("link")]
        if not linked_projects:
            pytest.skip("No projects with external links in data.json")
        proj = linked_projects[0]
        link = loaded_page.locator(f'a[href="{proj["link"]}"]').first
        expect(link).to_have_attribute("target", "_blank")


class TestResponsive:
    @pytest.mark.parametrize("width,height", [(375, 812), (768, 1024), (1440, 900)])
    def test_layout_no_horizontal_scroll(self, page: Page, width, height):
        page.set_viewport_size({"width": width, "height": height})
        page.goto(BASE_URL)
        page.wait_for_selector("#about", timeout=10_000)
        scroll_width = page.evaluate("document.documentElement.scrollWidth")
        client_width = page.evaluate("document.documentElement.clientWidth")
        assert scroll_width <= client_width + 5, (
            f"Horizontal overflow at {width}x{height}: "
            f"scrollWidth={scroll_width} clientWidth={client_width}"
        )


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
