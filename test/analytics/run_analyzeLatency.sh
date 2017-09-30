PROG='analyzeLatency.py'
DATA_DIR='../data/'
echo $(ls $DATA_DIR)
for i in $(ls -d $DATA_DIR/*); do
    echo python3 $PROG $(pwd)/$i
    python3 $PROG $(pwd)/$i
done
