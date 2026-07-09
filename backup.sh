git add .
git commit -m "$(date +'%b %d')"
git push origin $(git rev-parse --abbrev-ref HEAD)
