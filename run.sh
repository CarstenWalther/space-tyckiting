DUMMY="--ai=dummy --name=dummy"
RAND="--ai=rand --name=random"

ALBERT="--ai=albert --name=albert"
BERTA="--ai=berta --name=berta"
CECILLE="--ai=cecille --name=cecille"
DORIAN="--ai=dorian --name=dorian"

AI1_ARGS="$BERTA" 
AI2_ARGS="$DORIAN --verbose"


cd server
node start-server.js 1>/dev/null &
sleep 0.5
firefox http://localhost:3000/ &
sleep 3

cd ../clients/python
python3 cli.py $AI1_ARGS &
python3 cli.py $AI2_ARGS

sleep 0.1