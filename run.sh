DUMMY="--ai=dummy --name=dummy"
RAND="--ai=rand --name=random"
LUDWIG="--ai=ludwig --name=ludwig" 

AI1_ARGS="$DUMMY" 
AI2_ARGS="$LUDWIG --verbose"


cd server
node start-server.js 1>/dev/null &
sleep 0.5
firefox http://localhost:3000/ &
sleep 3

cd ../clients/python
python3 cli.py $AI1_ARGS &
python3 cli.py $AI2_ARGS

sleep 0.1