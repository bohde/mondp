#!/bin/bash

sumo-netgen --random-net --plain-output rand --rand-iterations=20 --abs-rand
sumo-netconvert  -n rand.nod.xml -e rand.edg.xml -v -o rand.net.xml

sumo-jtrrouter --net=rand.net.xml -R 1000 --output-file=rand.rou.xml  -b 0 -e 1000
