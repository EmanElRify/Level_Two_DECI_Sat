# Session 19: Adventure Game Project


### Randomness 
> Add randomness to the story events. For example, when the player go deep into the forest at first they find a strange creature.
 When they play again and go deep to the forest they find something else, maybe a wand stick
- add randomness using `random` module
- use `random.choice(items)` , where `items` is a list of possible events that could happen
For example:
```python
import random

# Example list
items = ['apple', 'banana', 'cherry', 'date', 'elderberry']

# Choose a random item from the list
random_item = random.choice(items)

print(f"The randomly selected item is: {random_item}")
```

### Test your code
1- install pycodestyle using pip in the terminal (vs/ workspace):
	```
	pip install pycodestyle
	```
2- Run unit tests
	```
	python unittest_adventure_game_deci-lvl2_v2.py adventure_game.py
	```
3- Run unit tests + pycodestyle
	```
	python unittest_adventure_game_deci-lvl2_v2.py adventure_game.py pycodestyle
	```
### To format your code automatically(VS code):
<h4><mark> 1- install "autopep8" extension </mark></h4>
<h4><mark> 2- From setting search for "default formatter"</mark></h4>
 <img src = "format_step_1.png" alt = "setting in VS code">
<h4><mark> 3- Choose autopep8</mark></h4>
 <img src = "autopep8.png" alt = "autopep8">

<h4><mark> 4- In the code file right click and choose "Format Document" or **Press ALT + Shift + F** </mark></h4>
 <img src = "format.png" alt = "format">

## <a href = "https://www.geeksforgeeks.org/how-to-get-weighted-random-choice-in-python/">How to get weighted random choice</a>





