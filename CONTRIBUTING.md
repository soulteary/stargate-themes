# Contributing

Keep each theme in `themes/<id>/`, with its `id` matching the directory name.
The source of truth for the format is Stargate's `docs/enUS/THEMES.md` and
`src/internal/theme`. Use the validator from the build the theme targets.

Version one accepts `theme.yml`, an optional PNG or JPEG declared by
`brand.image`, and `LICENSE.txt`. It does not accept templates, CSS, JavaScript,
SVG, fonts, links or undeclared files. Use the core layout and token interface
rather than copying authentication forms. Keep resources local.

A pull request should describe the visual change, increase the theme version
when its distributed content changes, and include desktop and mobile previews.
Do not include entered credentials, QR codes, enrollment secrets or recovery
codes in screenshots. Keep previews outside theme directories.

Before submitting:

1. Run `python3 tools/package.py --stargate /path/to/stargate`.
2. Repeat packaging into another directory and compare archive and index bytes.
3. Extract the archive and validate the extracted directory with `themecheck`.
4. Check desktop and mobile layouts, keyboard focus and reduced motion.
5. Test both login forms, available code channels, TOTP and recovery selection,
   account settings, enrollment, removal and additional verification.
6. Confirm that the browser makes no external resource requests and reports no
   script or Content-Security-Policy errors.
7. Include the rights and required notices for images and other resources.

Authentication behavior belongs to Stargate. Its backend and browser tests
must pass with the theme enabled; a screenshot alone does not establish that
login works.
