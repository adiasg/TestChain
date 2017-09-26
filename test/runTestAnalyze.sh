echo $(ls data/)
for i in $(ls -d data/*/); do
    echo $(pwd)/data/$i
    python3 testAnalyze.py $(pwd)/$i
done
