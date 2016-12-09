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
Informational variables so that we can use the data as soon as a 
pattern starts
(these are somewhat optional)
"""
mem['last_pattern_start_ts'] = 0.  # @todo: might be able to get this from the end of the section_timestamps? 
mem['last_pattern_end_confirmed'] = False


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


"""
Position handling
"""
def get_last_position():
    pass
    
def get_last_position_ts():
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
    
    # Find the length of time that we expect to see a stripe at our given speed
    # width of stripe, speed -- how fast will we pass it? 
    # e.g. 4" stripe, 120"/s = 4/120ths of a second. 
    # Then multiply it by 5 or something to make sure we wait long enough before confirming a pattern is ended
    
"""
First pass filter
"""

# States: WAIT, PATTERN_DETECT, PATTERN_PROCESS

# @todo: handl stripe_min_risefall_diff
# @todo: handle speed estimation
# @todo: handle pattern_confirm_wait_time

if __name__ == "__main__":

    state = "WAIT"
    
    print "Started contrast sensor handler loop in {} state".format(state)
        
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
                    # @todo: what about if it's too long?
                    continue
                else: 
                    # We've detected a stripe! 
                    
                    # Append rising and falling timestamps to the active pattern
                    mem['active_pattern'].append(rising_ts)
                    mem['active_pattern'].append(falling_ts)

                    # Add a '10' to our sliding flight profile to indicate the start and finish of a stripe
                    mem['sliding_flight_profile'].appendleft(1)
                    mem['sliding_flight_profile'].appendleft(0)

                    # If the end of the previous pattern is marked as confirmed, then we're a new pattern.
                    if mem['last_pattern_end_confirmed']:  

                        # Update with the most current info for positioning
                        mem['last_pattern_start_ts'] = rising_ts
                        mem['last_pattern_end_confirmed'] = False  # We'll confirm this once the pattern is complete
                        
                        # Increment the section counter
                        mem['section_counter'] += 1

                        # Append the first rising_ts of the pattern (that's the start of a section)
                        mem['section_timestamps'].append(rising_ts)
                        
                        # @todo: should we also capture the time at which the timestamp was added so we can more accurately estimate position?
                        # (note: position at an older timestamp is less 
                        # useful but more accurate than an estimated position
                        # based on speed and time passed since the timestamp was entered)


                    # @todo: Maybe recalculate the speed estimate and risefall diff here? Or maybe in PATTERN_PROCESS...
            
            # @todo: note the if len(...) above -- is it ok if that if fails and we fall down to this? Note that active pattern might not have any values...
            
            # Check to see if enough time has passed for us to confirm that we're past a pattern
            # Note: not sure exactly what would happen if we stopped in the middle of a pattern, but I think it would actually work

            # Note: we may be in the middle of a stripe, so active_pattern may not have been established yet.
            #       This means that if we get a rising and no falling, we will get stuck in this state
            # @todo: maybe implement a timeout if no falling is detected within a some amount of time (e.g. no_falling_timeout)? 
            if len(mem['active_pattern']):
                # Read the last value of active_pattern -- it's a falling_ts since they're always added in rising/falling pairs
                last_falling_ts = mem['active_pattern'][-1]  
            
                if now() - last_falling_ts > mem['pattern_confirm_wait_time']:
                    # We have finished a pattern!
                
                    # Add a 0 to our sliding flight profile to indicate the end of a pattern
                    mem['sliding_flight_profile'].appendleft(0)
                
                    # Confirm that the pattern is finished
                    mem['last_pattern_end_confirmed'] = True

                    # Clear the active_pattern queue
                    mem['active_pattern'].clear()
                
                    # Change state to PATTERN_PROCESS so that we can figure out where we are
                    # Note: we will use sliding_flight_profile to figure out where we are with some certainty
                    state = "PATTERN_PROCESS"

                
        elif state == "PATTERN_PROCESS":
            # Use a sliding window to determine where we are with certainty
            # Note: the highest certainty will be at the 1000ft and 500ft rumble strips
            pass
            
            # Return to wait state after processing a pattern
            state = "WAIT"
            
            
            