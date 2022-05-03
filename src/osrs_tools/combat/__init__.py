"""The combat sub-module builds off of character and does nerd calculations.

This is an interesting one for me, I used to have ***everything*** character,
player, monster, and coxmonster related in one giant file called character.py.
Once I started implementing better coding strategies and properly using
inheritance, I realized the grand folly of my ways. And as I separated things
I came to realize that Monster and Player, while obviously important and
different enough to warrant their own file, were dependent upon each other. I
realized that there should be a sort of lad that's one level higher in the
implementation tree, that can use both of these and make combat simple! Then I
realized I still had a bunch of static methods and modifiers built into player
that necessitated another level up. I think what I've done is valid, and I
will come to find out eventually.

###############################################################################
# email:    noahgill409@gmail.com                                             #
# created:  2022-04-29                                                        #
###############################################################################
"""
