PROG="simulate.py"

#number_of_peers=(10)
#simulation_time=600
#lambda_sync=('0.2' '0.4' '0.6')
#lambda_gen=('0.2' '0.4' '0.6')

#for peer in ${number_of_peers[@]}; do
#    for gen in ${lambda_gen[@]}; do
#        for sync in ${lambda_sync[@]}; do
#            echo "python3 $PROG $peer $sync $gen $simulation_time"
#            python3 $PROG $peer $sync $gen $simulation_time
#        done
#    done
#done

number_of_peers=(15)
simulation_time=600
lambda_sync=('0.47' '0.93' '1.4')
lambda_gen=('0.2' '0.4' '0.6')

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
lambda_sync=('0.84' '1.69' '2.53')
lambda_gen=('0.2' '0.4' '0.6')

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
lambda_sync=('1.33' '2.67' '4.0')
lambda_gen=('0.2' '0.4' '0.6')

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
lambda_sync=('0.47' '0.93' '1.4')
lambda_gen=('0.2' '0.4' '0.6')

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
lambda_sync=('0.84' '1.69' '2.53')
lambda_gen=('0.2' '0.4' '0.6')

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
lambda_sync=('1.33' '2.67' '4.0')
lambda_gen=('0.2' '0.4' '0.6')

for peer in ${number_of_peers[@]}; do
    for gen in ${lambda_gen[@]}; do
        for sync in ${lambda_sync[@]}; do
            echo "python3 $PROG $peer $sync $gen $simulation_time"
            python3 $PROG $peer $sync $gen $simulation_time
        done
    done
done

