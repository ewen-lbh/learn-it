# LEARN_IT!
A script that helps you learn stuff.  

# Installation
## Windows
 - Install [python](https://python.org/download) (version 3.6 or higher)
 - Download this repository ("Clone or download" button > "Download ZIP")
 - Extract `learn-it-master` to a folder, go in that folder
 - Open a command prompt: Right-Click while holding `Shift`, and select "Open terminal here".
 - Check if pip is installed: `py -m pip3 --version`
 - Install required packages with `py -m pip3 install -r requirements.txt`
 - Finally, run the program with `py run.py`
 - The program will open a file selection dialog, select your learndata file and click `Open`

## Linux
 - (1) Install required programs: `sudo apt install python python3 python3-pip git`
 - (2) Clone the repo: `git clone https://github.com/ewen-lbh/learn-it`
 - (3) Navigate to the repo: `cd learn-it`
 - (4) Install dependencies: `pip3 install -r requirements.txt`
 - (5) Run the script: `python3 run.py`

## macOS
 - Install [python](https://python.org/download) (version 3.6 or higher)
 - Open your terminal (press the launchpad button, type "terminal" & press enter)
 - Install git (Type `git`, press Enter and accept)
 - Do Linux's instructions from step 2 through 5

## Android
 - Install [Termux](https://play.google.com/store/apps/details?id=com.termux)
 - Open the app
 - Install required programs: `apt install git` (python and pip are pre-installed with Termux)
 - Do Linux's instructions from step 2 trough 4
 - Give Termux access to your downloads folder: `termux-setup-storage`
 - Put your learndata file in `Download` (on your phone's internal storage, not on your SD Card)
 - Run `python3 run.py Downloads/file.txt` (where `file.txt` is the name of your learndata file)

## iOS
 - Ahaha no. Get a real phone

> If you've set `LEARNDATA_ROOT` and that your file is located here, you can specify the path directly: `py run.py russian/vocabulary` (if you have a file "vocabulary.txt" situated in LEARNDATA_ROOT/russian)

# "learndata" files  
  
At the top of the script, there's a `DATA_FILE` variable.  
Set it to the path (relative to the folder the script is executed in) of the learndata file you want to use, and run the script.  
The file will be parsed, and the training (or testing, see [modes](#modes)) will begin.  
  
## The file format
Learn_it! used to use its own learndata file format, but—as it seemed unecessary—Learn_it! now relies on YAML. To convert your old learndata files to YAML, you can use the command `python3 run.py convert path/to/old/learndata/file.txt`, and `file.txt` will be converted into a file called `file.yaml`.

### Overview 
```yaml
flags:
    flag-name: value
    other-flag: value
    blacklist:
        - blacklisted key
        - other blacklisted key
# Comment
Thing to learn about (the "key"): Its correct answer (the "value") 
Other thing you should know by heart: Its correct answer  
```
  
## Flags  
Flags are used to set options.   
Available flags:  
*strikedthrough flag names indicate not-implemented-yet flags*  
  
|Name|Description|Values or value example|Default  
|--|--|--|--|  
|always-show-grade|In testing mode, show the grade everytime you answer something, and not only at the end|true, false|false  
|allow-typos|Whether to ask if you made typo when you got an answer wrong. If you made a typo, you have another chance to find the word.|true, false|false    
|ask-for|What to ask for: keys, values or both (starting with keys)|keys, values, both|values    
|ask-order|Order according to which the items are asked about. Doesn't affect *training mode*|keep, alphabetical, random|keep    
|ask-sentence|Use this to change the sentence used to ask about an item. `<>` is replaced with the item asked about|How do you say <> in russian ?|<>
|auto-blacklist|Use this to automatically add known words to the learndata file's `blacklist`.|true, false|false
|blacklist|Like whitelist, except it prevents specified items from being asked. Useful if you already know some items in the learndata|[spam, eggs]|[]    
|case-sensitive|Take case into account when comparing answers|true, false|false
|clear-mode|Either `confirm`: Press `Enter` to move to next word, or `delay`: Automatically move to next word after some time.|confirm, delay|confirm
|clear-screen|Clears the screen after each response. If set to `false`, each answer will be separated by newlines.|on, delay, off|true
|debug|Sets the debug mode. |true, false|false    
|good-grade|Grades greater or equal to this will be shown green, while others will be shown red. The good-grade value is calculated by multiplying it by the max-grade value.|0.75|0.5    
|grade-max|Indicate the divisor (maximum grade) used in *testing mode*.|20|100    
|grade-precision|Specify the precision used to round the grade value|1|2  
|header-color|The header's color. Avaible colors: grey, red, green, yellow, blue, magenta, cyan, white|red|cyan  
|header|Text shown at the beginning of the script. `<>` is replaced with `title`'s value|<>|\-\-\- <> \-\-\-|  
|preset|Use a [flags preset](#presets).|languages||
|read-time|Time to read a letter, in seconds. Used to determinate delay before clearing the screen when the answer was wrong.|0.5|0.25
|show-answer-in-testing-mode|In testing mode, show the correct answer when the provided answer was wrong. (This behavior is always active in training mode)|true, false|true  
|show-items-count|Shows a message at the start that says: "Loaded *N* items from *FILE*"|true, false|true
|show-remaining-items-count|After each question, shows the number of remaining items|true, false|false
|strict-learn-about|This only affects files with `ask-for` set to `both`. Alters the way the list of elements shown in the recap (those you need to learn) is calculated. If this option is true, elements will be added to the test if you fail at least one time. If set to false, you need to fail in both tests in order to add the element.|true,false|true  
|title|Will be used to display a header at the start of the script. If set to `untitled`, the header will not be displayed.|Chemistry test|untitled    
|warn-unknown-flags|Shows a warning if some flags are declared but unknown|true, false|true  
|whitelist|Use this to filter the things scanned, useful if you have a huge file and already know most of the things in it, but don't know about some other things|- blacklisted key<br>- another blacklisted key|[]|    
|~~no-colors~~|Deactivate all colors, useful for terminals that don't support [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code#Platform_support)|true, false|false   
 
   
### Presets
The `src/presets.yaml` file contains a single preset named *languages*. Obviously, you can add more presets.
The file in itself is an object that contains presets, using their names as the property (the key), and the value being another object, that associates flags with their values :
    
```yaml
preset-name:
    flag: value
    other-flag: other value
other-preset-name:
    ...
```

#### Overriding
If you specify a preset that declares a flag, and that you also specify a value for that flag, the value defined in the learndata file will override the preset's.
*Example*
		

presets.yaml:
```yaml
thingy:
    whitelist:
        - stuff
        - things
```

learndata.yaml:
```yaml
flags:
    whitelist:
        - spam
        - eggs
    preset: thingy
```

In this example, `whitelist` will take the value `[spam, eggs]`, even if `preset` is declared 
after `whitelist`.
  

### File example  
Take a look at `learndata-example.yaml` to get an idea of what a learndata text file looks like, and how the flags are used and defined.  
  
# Modes  
This script uses 2 different modes: *testing mode* and *training mode*.  
## Training mode  
In this mode, the script cycles through the items (key-value pairs) and ask you to give your answer. If you fail, the script will ask you about it later, until you answered right to all the items.  
## Test mode  
In this mode, the script will ask you for each item *once* (except if you have the [`allow-typos`](#flags) flag set to `true`).  
At the end, it will tell you your grade and the list of items you did not find.

# Logging levels
You can change the logging level with  `LOG_LEVEL` (in `src/consts.py`)

