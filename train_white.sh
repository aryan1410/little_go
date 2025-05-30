#!/bin/bash
rm -rf *.so
echo "Programming language..."
command=$(ls|grep my_player)
py=$([[ $command =~ (^|[[:space:]])"my_player.py"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
py3=$([[ $command =~ (^|[[:space:]])"my_player3.py"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
cpp=$([[ $command =~ (^|[[:space:]])"my_player.cpp"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
c11=$([[ $command =~ (^|[[:space:]])"my_player11.cpp"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
java=$([[ $command =~ (^|[[:space:]])"my_player.java"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
if [ "$py" == "yes" ]; then
	cmd="python my_player.py"
	echo "PY"
elif [ "$py3" == "yes" ]; then
    cmd="python3 my_player3.py"
	echo "PY3"
elif [ "$cpp" == "yes" ]; then
	g++ -O2 *.cpp -o exe
	cmd="./exe"
	echo "CPP"
elif [ "$java" == "yes" ]; then
	javac my_player.java
	cmd="java my_player"
	echo "JAVA"
elif [ "$c11" == "yes" ]; then
	g++ -std=c++0x -O2 *.cpp -o exe
	cmd="./exe"
	echo "11"
else
    echo "ERROR: INVALID FILENAME"
	exit 1
fi

echo ""

prefix="./"
ta_agent=("random_player" "greedy_player" "alpha_beta_player" "aggressive_player") # All agents
surfix=".py"

# play function
play()
{    
    echo Clean up... >&2
    if [ -f "input.txt" ]; then
        rm input.txt
    fi
    if [ -f "output.txt" ]; then
        rm output.txt
    fi
    cp $prefix/init/input.txt ./input.txt

    echo Start Playing... >&2

	moves=0
	while true
	do
        if [ -f "output.txt" ]; then
	        rm output.txt
	    fi

        echo "Black makes move..." >&2
		eval "$1" >&2
		let moves+=1

		python3 $prefix/host.py -m $moves -v True >&2
		rst=$?

		if [[ "$rst" != "0" ]]; then
			break
		fi

        if [ -f "output.txt" ]; then
	        rm output.txt
	    fi

		echo "White makes move..." >&2
		eval "$2" >&2
		let moves+=1

		python3 $prefix/host.py -m $moves -v True >&2
		rst=$?

		if [[ "$rst" != "0" ]]; then
			break
		fi
	done

	echo $rst
}

play_time=1500  # Number of games to play

### start playing ###

echo ""
echo $(date)

# Initialize win/lose/tie counters for each agent
declare -A wins
declare -A ties
declare -A losses
for agent in "${ta_agent[@]}"; do
    wins[$agent]=0
    ties[$agent]=0
    losses[$agent]=0
done

# Initialize total counters
total_wins=0
total_ties=0
total_losses=0

for (( round=1; round<=$play_time; round++ )) 
do
    # Randomly select an opponent
    opponent=${ta_agent[$RANDOM % ${#ta_agent[@]}]}
    ta_cmd="python3 $prefix${opponent}$surfix"

    # # Alternate starting player (Black or White)
    # if (( round % 2 == 0 )); then
        # TA takes Black
    echo "=====Round $round====="
    echo Black:${opponent} White:You 
    winner=$(play "$ta_cmd" "$cmd")
    if [[ "$winner" = "2" ]]; then
        echo 'White(You) win!'
        let wins[$opponent]+=1
        let total_wins+=1
    elif [[ "$winner" = "0" ]]; then
        echo Tie.
        let ties[$opponent]+=1
        let total_ties+=1
    else
        echo 'White(You) lose.'
        let losses[$opponent]+=1
        let total_losses+=1
    fi
    # else
        # You take Black
    # echo "=====Round $round====="
    # echo Black:You White:${opponent}
    # winner=$(play "$cmd" "$ta_cmd")
    # if [[ "$winner" = "1" ]]; then
    #     echo 'Black(You) win!'
    #     let wins[$opponent]+=1
    #     let total_wins+=1
    # elif [[ "$winner" = "0" ]]; then
    #     echo Tie.
    #     let ties[$opponent]+=1
    #     let total_ties+=1
    # else
    #     echo 'Black(You) lose.'
    #     let losses[$opponent]+=1
    #     let total_losses+=1
    # fi
    # fi
done

# Print win rate against each agent
echo ""
echo =====Win Rate Against Each Agent=====
for agent in "${ta_agent[@]}"; do
    total_games=$((wins[$agent] + ties[$agent] + losses[$agent]))
    win_rate=$(echo "scale=2; ${wins[$agent]} * 100 / $total_games" | bc)
    tie_rate=$(echo "scale=2; ${ties[$agent]} * 100 / $total_games" | bc)
    echo "Against $agent:"
    echo "  Wins: ${wins[$agent]} (Win Rate: $win_rate%)"
    echo "  Ties: ${ties[$agent]} (Tie Rate: $tie_rate%)"
    echo "  Losses: ${losses[$agent]}"
done

# Print total win rate
total_games=$((total_wins + total_ties + total_losses))
win_rate=$(echo "scale=2; $total_wins * 100 / $total_games" | bc)
tie_rate=$(echo "scale=2; $total_ties * 100 / $total_games" | bc)
echo ""
echo =====Total Summary=====
echo "Total Games Played: $total_games"
echo "Total Wins: $total_wins (Win Rate: $win_rate%)"
echo "Total Ties: $total_ties (Tie Rate: $tie_rate%)"
echo "Total Losses: $total_losses"

if [ -f "input.txt" ]; then
    rm input.txt
fi
if [ -f "output.txt" ]; then
    rm output.txt
fi

if [ -e "my_player.class" ]; then
    rm *.class
fi
if [ -e "exe" ]; then
    rm exe
fi
if [ -e "__pycache__" ]; then
    rm -rf __pycache__
fi
        
echo ""
echo Mission Completed.
echo $(date)