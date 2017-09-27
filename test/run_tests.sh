PROG="simulate.py"

number_of_peers=(10 15 20)
simulation_time=600
lambda_sync=('0.4' '0.6')
lambda_gen=('0.2' '0.4')

for peer in ${number_of_peers[@]}; do
    for gen in ${lambda_gen[@]}; do
        for sync in ${lambda_sync[@]}; do
            echo "python3 $PROG $peer $sync $gen $simulation_time"
            python3 $PROG $peer $sync $gen $simulation_time
        done
    done
done
