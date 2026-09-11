# Dad's Plans Dashboard (`dad.html`)

A personal, read-only dashboard that connects to Dad's Dropbox and shows **every plan set in the same card format**: cover thumbnail, address/client, status pill, sheet/Revit/CAD/photo counts, last update, file list, and an Open-in-Dropbox link.

Live at: `https://<your-netlify-site>/dad.html`

## One-time setup (Jubie, ~5 min)

1. Go to https://www.dropbox.com/developers/apps → **Create app** → Scoped access → **Full Dropbox** → name it `Dad Plans`.
2. **Permissions** tab → check `files.metadata.read` and `files.content.read` → Submit.
3. **Settings** tab → OAuth 2 → Redirect URIs → add exactly `https://<your-netlify-site>/dad.html` (and `http://localhost:8888/dad.html` if you test locally).
4. Copy the **App key** and paste it into `DEFAULT_APP_KEY` at the top of the script in `dad.html`, so Dad never sees the setup screen. (Or leave it blank and paste it once in the setup screen on his phone.)
5. Open the page on Dad's phone → **Connect Dropbox** → log in with **his** Dropbox → Settings → pick the plans folder → Save. Add to Home Screen for an app icon.

Login uses OAuth PKCE in the browser, so there is no secret to store and nothing goes through the Netlify function. Tokens live in his browser's localStorage only.

## How plans are detected

- Each **sub-folder** of the chosen folder is one plan. Files sitting loose in the root show as "Unsorted files".
- Folder name → card: `1234 Main St – Smith ADU [PERMIT]` gives title `1234 Main St`, subtitle `Smith ADU`, status Permit.
- Status tags (anywhere in the folder name): `[DONE]`, `[PERMIT]`, `[REVIEW]`, `[HOLD]`. No tag = Active. Status can be overridden per card (saved on that device).
- Thumbnail: first photo in the folder, else page 1 of the cover/first PDF (rendered with pdf.js).
- Counts: Sheets = PDFs · Revit = .rvt/.rfa · CAD = .dwg/.dxf/.skp · Photos = images.

## Notes

- Read-only: the page never writes to Dropbox.
- The listing is cached in the browser so the page opens instantly, then re-syncs.
- If PDF thumbnails stay blank, Dropbox temporary links blocked the cross-origin fetch; the card still works (counts, files, open links).
