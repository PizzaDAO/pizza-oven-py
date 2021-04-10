#!/bin/csh

set natronPath = "/Applications/Natron.app/Contents/MacOS/"
set projectPath = " /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron"
cd /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron

set frame = 9
echo frame $frame

echo box
time $natronPath/NatronRenderer -l $projectPath/box.py $projectPath/box.ntp $frame > stats.txt

echo waxpaper
time $natronPath/NatronRenderer -l $projectPath/waxpaper.py $projectPath/waxpaper.ntp $frame >> stats.txt

echo crust
time $natronPath/NatronRenderer -l $projectPath/crust.py $projectPath/crust.ntp $frame >> stats.txt

#echo sauce
time $natronPath/NatronRenderer -l $projectPath/sauce.py $projectPath/sauce.ntp $frame >> stats.txt