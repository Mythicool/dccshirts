# Redeploy Shirt Studio (static, previews only) to https://dccshirts-mythicool.netlify.app
# The same build runs on Netlify from the GitHub repo (netlify.toml); this is the manual CLI route.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
node tools/build-site.mjs
npx -y netlify-cli@latest deploy --site 6c1678f2-3865-4c35-a774-1f8195dd7730 --prod --dir dist
Pop-Location
