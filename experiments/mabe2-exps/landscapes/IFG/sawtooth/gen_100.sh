#! /bin/bash

for benefit in 1.5
do
    for step in -0.05
    do
        #echo "$benefit $step"
        python3 gen_graph.py ${benefit} 6 ${step} 100
    done
done
