git add .
git push origin $(git rev-parse --abbrev-ref HEAD)
git commit -m "$(date +'%b %d')"
