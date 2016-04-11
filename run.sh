
if [ $# -lt 2 ]; then
    echo 'not enough parameters'
    echo 'usage:'
    echo 'run.sh <ai_1> <ai_2> [option]'
    echo 'options: --verbose --verbose2'
    echo 'verbosity effects ai_2'
    exit 1
fi

ai_1=$1 
ai_2=$2
verbose=$3

client_cmd='python3 cli.py'
ai_1_cmd="$client_cmd --ai=$ai_1 --name=$ai_1"
ai_2_cmd="$client_cmd --ai=$ai_2 --name=$ai_2"

platform=$(uname)
spectator_url=http://localhost:3000/


if [ $platform == 'Linux' ]; then
   browser_cmd='gnome-open'
elif [ $platform == 'Darwin' ]; then
   browser_cmd='open'
else
	echo 'could not recognize platform'
	exit 1
fi


cd server
node start-server.js 1>/dev/null &
sleep 0.5
$browser_cmd $spectator_url
sleep 3

cd ../clients/python
$ai_1_cmd &
$ai_2_cmd $verbose
sleep 0.1