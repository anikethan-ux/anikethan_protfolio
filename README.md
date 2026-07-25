# Portfolio — data-driven setup

## Folder structure
```
portfolio/
├── index.html          ← layout, styling, JS. Rarely needs editing.
├── contact.php          ← saves contact-form submissions (needs PHP hosting)
├── data/
│   └── data.json         ← ALL your content lives here. Edit this to update the site.
├── messages/
│   ├── .htaccess          ← blocks public access to saved messages
│   └── messages.txt        ← created automatically once someone submits the form
├── test_portfolio.py
├── README.md
├── Screenshot (31).png              ← your photo
└── Nalla_Anikethan_Reddy_Resume_graduated_resume.pdf
```

## To change content
Open `data/data.json` and edit the relevant field. Examples:
- Change job title → `profile.title`
- Add/edit a job → add an object to the `experience` array (`company`, `role`, `duration`, `current`, `summary`, `points`) — renders as a row in the Experience table
- Add a new project → add an object to the `projects` array (`icon`, `title`, `summary`, `points`, optional `link`, optional `tech`)
- Add a skill → add to the right group's `items` array in `skills`

No HTML/JS editing needed — the page re-renders whatever is in the JSON.

## Contact form — how it works
The "Get In Touch" section has a real form (Name / Email / Message) powered by **Web3Forms** — a free service that emails you every submission directly. No backend/server of your own needed, and it works on GitHub Pages as-is.

### One-time setup
1. Go to **web3forms.com** and enter your email to get a free **Access Key** (no account needed).
2. Open `data/data.json` and paste your key into:
   ```json
   "contactForm": {
     "accessKey": "YOUR_ACTUAL_ACCESS_KEY_HERE"
   }
   ```
3. That's it — submissions get emailed to the address you registered with Web3Forms.

**Note:** Web3Forms emails you the message; it does not save anything into a local `messages/` folder or text file. If you specifically want submissions saved to a text file on your own server instead of emailed, that requires PHP-capable hosting — `contact.php` and the `messages/` folder from the earlier version are still included in case you want to switch back to that approach later (see "Alternative: self-hosted PHP" below).

### Alternative: self-hosted PHP (saves to messages/messages.txt instead of email)
If you'd rather keep messages in a local text file:
1. Change `data/data.json`'s `contactForm` back to:
   ```json
   "contactForm": {
     "provider": "php",
     "endpoint": "contact.php",
     "successMessage": "Thanks! Your message has been sent.",
     "errorMessage": "Something went wrong sending your message. Please try again or email me directly."
   }
   ```
2. Host on PHP-capable hosting (GitHub Pages can't run PHP) — e.g. shared hosting, or test locally with `php -S localhost:8000`.
3. Let me know and I'll swap the form's JS submit handler back to the PHP-compatible version.

## Running locally
`fetch()` needs a real server (not double-clicking the HTML file):

```bash
cd portfolio
python -m http.server 8000
# open http://localhost:8000
```
(Use `php -S localhost:8000` instead if you want to actually test the contact form end-to-end.)

## Running the tests
```bash
pip install pytest-playwright
playwright install chromium

# in one terminal
python -m http.server 8000

# in another terminal
pytest test_portfolio.py -v
```

The tests read `data/data.json` at runtime rather than hardcoding your content, so they keep passing as you add real projects — they check *structure and behavior* (sections render, project/experience counts match the JSON, toggles open/close, links point to the right URL, no horizontal scroll on mobile), not specific text.

## Notes
- `profile.photo` and `profile.resumeFile` in `data/data.json` must exactly match your actual filenames (case-sensitive once deployed to GitHub Pages, even though Windows locally isn't).
- Send me your real Playwright/SQL/Python projects whenever you're ready and I'll drop them straight into the `projects` array in `data/data.json`.
