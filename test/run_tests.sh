PROG="simulate.py"

simulation_time=600
lambda_gen=('0.2')

for expt_count in {1..10}; do
    echo $expt_count

    number_of_peers=(10)
    lambda_sync=('0.6' '0.6' '0.6')

    for peer in ${number_of_peers[@]}; do
       for gen in ${lambda_gen[@]}; do
           for sync in ${lambda_sync[@]}; do
               echo "python3 $PROG $peer $sync $gen $simulation_time"
               python3 $PROG $peer $sync $gen $simulation_time
           done
       done
    done

    number_of_peers=(15)
    lambda_sync=('0.9' '1.06' '1.4')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

    number_of_peers=(20)
    lambda_sync=('1.2' '1.56' '2.53')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

    number_of_peers=(25)
    lambda_sync=('1.5' '2.1' '4.0')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

done
