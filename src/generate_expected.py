
# Generate the expected pattern of tape in the tube
# @see https://drive.google.com/drive/u/0/folders/0B5Sx7gOkYaCTfnlBeHpselJmR2IyRE9iR2I0LXdJY1IxM1RTVl9Nejl2UE91NFU2b3hld1U

# All measurements are start-to-start

tube_length_ft = 4150   # 4150 to 5000 feet
initial_marker_spacing_in = 100   # 100 feet, start to start (don't add 4 in for each one)
marker_width_in = 4
spacer_width_in = 4
thousand_ft_remain_markers = 10

tube_length_in = tube_length_ft * 12
sections_total = tube_length_in / 3  # number of 4-inch sections
sections_per_100_ft = 100 * 3  # number of 4-inch sections per 100 feet

# end 001 001 001 001 0101010101 001 001 001 001 01010101010101010101 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001 001  001 001 001 001 001 [4000] 001 001 001 001 001 

"""

001001001001010101010100100100100101010101010101010101001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001001
001001001001001001001001
00101010101010101010101001
Procedure would be:
1. Set speed estimate to something close to the speed we expect to be going when we hit the first marker
2. Enter a 1 once we have once we have detected both a rising and a falling edge, and the time difference between them is large enough to be a stripe (use the speed estimate to determine what's "large enough")
3. Enter a 0 as soon as we have a falling edge (so basically, enter a 1 and 0 after the falling edge)
4. If no new stripe is detected after the last falling edge (say, 5x the time between the rising and falling edges of the last stripe), enter another 0

So, for each lone stripe, you get a '100', but for the rumble strips you get a 101010 type pattern. 

Note: do the search only after the second 0 is entered. This keeps us from trying to search when we are in a rumble strip

"""

edward6chan@gmail.com 
edwardchan.net
linkedin.com/in/edward6chan 
github.com/edward6chan
19162 Parsons Ave, 
Castro Valley, CA 94546 
484.758.7032
