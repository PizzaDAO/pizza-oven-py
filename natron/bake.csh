#!/bin/csh

cd /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron

set frame = 1

time /Applications/Natron.app/Contents/MacOS/NatronRenderer -l /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron/box.py  /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron/box.ntp $frame > stats.txt

time /Applications/Natron.app/Contents/MacOS/NatronRenderer -l /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron/waxpaper.py  /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron/waxpaper.ntp $frame >> stats.txt

time /Applications/Natron.app/Contents/MacOS/NatronRenderer -l /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron/crust.py  /Users/anthonyshafer/Dropbox/RarePizzas/rarepizzas-repo/pizza-oven-py/natron/crust.ntp $frame >> stats.txt