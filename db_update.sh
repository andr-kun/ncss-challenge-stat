pushd "/Users/andri/Repositories/ncss-challenge-stat" > /dev/null
git pull
python database.py
git commit -a -m "Regular update for json files"
git push
popd > /dev/null
