PROG="simulate.py"

number_of_peers=(50)
simulation_time=600
lambda_sync=('2.2' '2.0' '1.8')
lambda_gen=('1.4' '1.2' '1.0')

for peer in ${number_of_peers[@]}; do
    for gen in ${lambda_gen[@]}; do
        for sync in ${lambda_sync[@]}; do
            echo "python3 $PROG $peer $sync $gen $simulation_time"
            python3 $PROG $peer $sync $gen $simulation_time
        done
    done
done

