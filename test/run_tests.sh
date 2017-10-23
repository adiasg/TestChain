PROG="simulate.py"

simulation_time=600
lambda_gen=('0.4')

for expt_count in {1..10}; do

    number_of_peers=(15)
    lambda_sync=('1.14' '1.23' '1.32')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

    number_of_peers=(20)
    lambda_sync=('1.8' '2.04' '2.29')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

    number_of_peers=(25)
    lambda_sync=('2.58' '3.05' '3.52')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

done
