PROG=analyzeCsv.py

echo $(ls data/)
for i in $(ls -d data/*/); do
    echo $(pwd)/data/$i
    python3 $PROG $(pwd)/$i
done
