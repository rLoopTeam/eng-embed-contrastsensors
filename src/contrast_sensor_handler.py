#!/usr/bin/env python
"""
Purpose: Prototype of position decection for a single contrast sensor
Author:  Ryan Adams
Date:    2016-Dec-09
"""

import time
from bitarray import bitarray
from collections import deque

"""
Questions:
- Any chance that we would receive a rising edge with no corresponding falling edge (etc.)?
"""

endian = 'big'  # Used for bitarrays

""" Memory (struct) """
mem = {}

# Track representation
mem['track'] = bitarray("00100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100100101010101010101010101001001001001010101010100100100100", endian=endian)
mem['strip_width_mm'] = 101.6   # Maybe we should use inches? Stripes are 4 inches wide


"""
Search window. 32 bits, similar format to the track
We'll use deque.append() and a maxlen to simulate pushing the window
"""
mem['sliding_flight_profile'] = deque(maxlen=32)

"""
Estimated speed at next stripe. Doesn't have to be that accurate. 
- Initialize to how fast we think we'll be going at the first stripe,
  then update estimate as we go along. Used to weed out false hits 
  from things like the tube joints.
"""
mem['estimated_speed_mps'] = 0.5  # @todo: rename to avoid confusion?
mem['stripe_min_risefall_diff'] = 0.  # Set based on estimated speed?
mem['pattern_confirm_wait_time'] = 0.  # Will be set after 1st stripe


"""
Number of 100 foot sections we've passed. Note that this is not a 
count of stripes (remember the rumble strips)
"""
mem['section_count'] = 0
mem['section_timestamps'] = []

"""
FIFO Queues for rising and falling edge signal timestamps. 
These are to be used to buffer received data until we can process it.
Pop from both when a falling edge is detected, compare the speed, and
compute the wait time until section passed entry (another 0)
"""
mem['q_rising'] = deque()
mem['q_falling'] = deque()

""" 
A currently 'active' pattern -- always has matching rising and falling
pushed at the same time. 
"""
mem['active_pattern'] = deque() 


"""
Communications
"""
def now():
    return time.clock()

def recv_rising_edge(ts):
    """ Receive a rising edge signal at timestamp ts """
    mem['q_rising'].appendleft(ts)
    
def recv_falling_edge(ts):
    """ Receive a falling edge signal at timestamp ts """
    mem['q_falling'].appendleft(ts)

"""
Bit array handling
"""
def push_left(ba, value):
    pass


def calculate_pattern_confirm_wait_time(rising_ts, falling_ts):
    """ 
    Calculate the time after a falling edge detection that we should
    wait before confirming (by entering another 0) that we've passed 
    all strips in a section. This will use the estimated speed and
    difference between the time stamps, multiplied by some factor
    to make sure we're clear of the last stripe.
    """
    pass
    
    
"""
First pass filter
"""

# States: WAIT, PATTERN_DETECT, PATTERN_PROCESS

if __name__ == "__main__":
    # @todo: set the stripe_min_risefall_diff and pattern_confirm_wait_time
    # @todo: Find a way to separately put in values using recv_* functions

    state = "WAIT"
    
    while(True):
        # State machine. Note that python has no switch/case
        if state == "WAIT":
            # Wait until we have a rising edge signal
            if len(mem['q_rising']) > 0:
                state = "PATTERN_DETECT"
                continue
        elif state == "PATTERN_DETECT":
            # Weed out bad data and fill the active_pattern queue until we can confirm that the pattern is ended
            if len(mem['q_falling']):
                rising_ts = mem['q_rising'].pop()
                falling_ts = mem['q_falling'].pop()
                
                if falling_ts - rising_ts < mem['stripe_min_risefall_diff']:
                    # Difference is too short -- throw it out
                    continue
                else: 
                    # Append rising and falling timestamps to the active pattern
                    mem['active_pattern'].append(rising_ts)
                    mem['active_pattern'].append(falling_ts)
                    
            now = time.clock()   # What should this actually be? 
            if now - last_falling_ts > mem['pattern_confirm_wait_time']:
                # We have finished a pattern!
                # Append the first rising_ts of the pattern (that's the start of a section)
                mem['section_timestamps'].append(mem['active_pattern'][0])

        elif state == "PATTERN_PROCESS":
            
            

            if len(mem['q_falling']) > 0:
                # We have a falling edge
                rising_ts = mem['q_rising'].pop()
                falling_ts = mem['q_falling'].pop()
            
                diff = falling_ts - rising_ts
                if diff < mem['stripe_min_risefall_diff']:
                    # Too quick -- throw it out
                    continue   # is this right? 
                else: 
                    # We've got a live one -- use the rising timestamp (beginning of the stripe pattern)
                    mem['section_timestamps'].append(rising_ts)
            
        
        
