# learn-it

A script that helps you learn stuff.

  

## "learndata" files

At the top of the script, there's a `DATA_FILE` variable.
Set it to the path (relative to the folder the script is executed in) of the learndata file you want to use, and run the script.
The file will be parsed, and the training (or testing, see [modes](#modes))

  

### The "learndata" text file format
#### Overview
	
	--flag-name value
	Thing to learn about
	Its correct answer

	Other thing you should know by heart
	Its correct answer


#### Flags
Flags are used to set options. Here are the available flags:
|Name (without the leading `--`)|Description|Values or value example|Default
|--|--|--|--|
|whitelist|Use this to filter the things scanned, useful if you have a huge file and already know most of the things in it, but don't know about some other things|[a,comma,separated,list]|[]|
|ask-sentence|Use this to change the sentence used to ask about an item. `<>` is replaced with the item asked about|How do you say <> in russian ?|<>
|case-sensitive|Take case into account when comparing answers|True, False|False
|ask-for|What to ask for: keys, values or both (starting with keys)|keys, values, both|values
|ask-order|Order according to which the items are asked about. Doesn't affect *training mode*|keep, alphabetical, random|keep
|ask-for-typos|Whether to ask if you made typo when you got an answer wrong. If you made a typo, you have another chance to find the word.|True, False|False

## Modes

