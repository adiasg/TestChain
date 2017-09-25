PROG="simulate.py"

number_of_peers=8
simulation_time=600
inter_gen_time=(8)
inter_sync_time_per_peer=(20)

for gen in ${inter_gen_time[@]}; do
    for sync in ${inter_sync_time_per_peer[@]}; do
        echo "python3 $PROG $number_of_peers $sync $gen $simulation_time"
        python3 $PROG $number_of_peers $sync $gen $simulation_time
    done
done
