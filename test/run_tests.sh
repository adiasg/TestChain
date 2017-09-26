PROG="simulate.py"

number_of_peers=(10 15 20)
simulation_time=600
# inter_* times are multiplied by 0.1
inter_gen_time=(25 50)
inter_sync_time=(2 3 6)

for gen in ${inter_gen_time[@]}; do
    for sync in ${inter_sync_time[@]}; do
        echo "python3 $PROG $number_of_peers $sync $gen $simulation_time"
        python3 $PROG $number_of_peers $sync $gen $simulation_time
    done
done
