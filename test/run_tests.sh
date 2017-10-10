PROG="simulate.py"

for expt_count in {1..10}; do
    echo $expt_count

    number_of_peers=(10)
    simulation_time=600
    lambda_sync=('0.2' '0.2' '0.2')
    lambda_gen=('0.4')

    for peer in ${number_of_peers[@]}; do
       for gen in ${lambda_gen[@]}; do
           for sync in ${lambda_sync[@]}; do
               echo "python3 $PROG $peer $sync $gen $simulation_time"
               python3 $PROG $peer $sync $gen $simulation_time
           done
       done
    done

    number_of_peers=(15)
    simulation_time=600
    lambda_sync=('0.3' '0.35' '0.47')
    lambda_gen=('0.4')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

    number_of_peers=(20)
    simulation_time=600
    lambda_sync=('0.4' '0.52' '0.84')
    lambda_gen=('0.4')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

    number_of_peers=(25)
    simulation_time=600
    lambda_sync=('0.8' '0.7' '1.33')
    lambda_gen=('0.4')

    for peer in ${number_of_peers[@]}; do
        for gen in ${lambda_gen[@]}; do
            for sync in ${lambda_sync[@]}; do
                echo "python3 $PROG $peer $sync $gen $simulation_time"
                python3 $PROG $peer $sync $gen $simulation_time
            done
        done
    done

done
