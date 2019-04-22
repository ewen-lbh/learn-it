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
  
    
  
## The "learndata" text file format  
### Overview  
    --flag-name value  
    #comment 
    // another comment 
    Thing to learn about (the "key") 
    Its correct answer (the "value")  
    
    Other thing you should know by heart 
    Its correct answer  
    
    #The empty line is mandatory, it separates each item
    #See how the files are parsed in Core/main.py's parse() function
  
## Flags  
Flags are used to set options.   
Available flags:  
*strikedthrough flag names indicate not-implemented-yet flags*  
  
|Name (without the leading `--`)|Description|Values or value example|Default  
|--|--|--|--|  
|always-show-grade|In testing mode, show the grade everytime you answer something, and not only at the end|True, False|False  
|ask-for-typos|Whether to ask if you made typo when you got an answer wrong. If you made a typo, you have another chance to find the word.|True, False|False    
|ask-for|What to ask for: keys, values or both (starting with keys)|keys, values, both|values    
|ask-order|Order according to which the items are asked about. Doesn't affect *training mode*|keep, alphabetical, random|keep    
|ask-sentence|Use this to change the sentence used to ask about an item. `<>` is replaced with the item asked about|How do you say <> in russian ?|<>
|auto-blacklist|Use this to automatically add known words to the learndata file's `--blacklist`.|True, False|False
|blacklist|Like whitelist, except it prevents specified items from being asked. Useful if you already know some items in the learndata|[spam, eggs]|[]    
|case-sensitive|Take case into account when comparing answers|True, False|False
|debug|Sets the debug mode. |True, False|False    
|good-grade|Grades greater or equal to this will be shown green, while others will be shown red. The good-grade value is calculated by multiplying it by the max-grade value.|0.75|0.5    
|grade-max|Indicate the divisor (maximum grade) used in *testing mode*.|20|100    
|grade-precision|Specify the precision used to round the grade value|1|2  
|header-color|The header's color. Avaible colors: grey, red, green, yellow, blue, magenta, cyan, white|red|cyan  
|header|Text shown at the beginning of the script. `<>` is replaced with `--title`'s value|<>|\-\-\- <> \-\-\-|  
|preset|Use a [flags preset](#presets).|languages||
|show-answer-in-testing-mode|In testing mode, show the correct answer when the provided answer was wrong. (This behavior is always active in training mode)|True, False|True  
|show-items-count|Shows a message at the start that says: "Loaded *N* items from *FILE*"|True, False|True
|show-remaining-items-count|After each question, shows the number of remaining items|True, False|False
|strict-learn-about|This only affects files with `--ask-for` set to `both`. Alters the way the list of elements shown in the recap (those you need to learn) is calculated. If this option is True, elements will be added to the test if you fail at least one time. If set to False, you need to fail in both tests in order to add the element.|True,False|True  
|title|Will be used to display a header at the start of the script. If set to `untitled`, the header will not be displayed.|Chemistry test|untitled    
|warn-unknown-flags|Shows a warning if some flags are declared but unknown|True, False|True  
|whitelist|Use this to filter the things scanned, useful if you have a huge file and already know most of the things in it, but don't know about some other things|[a,comma,separated,list]|[]|    
|~~and-syntax~~|What symbol to use when you want to specify that the correct answer has to be *this* **and** *that*, in no particular order. [More explanation](#logical-operators)|&|&&    
|~~no-colors~~|Deactivate all colors, useful for terminals that don't support [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code#Platform_support)|True, False|False  
|~~or-syntax~~|Same as `and-syntax`, but used to specify a logical "or": *this* **or** *that*|, |\|\||    
  
  
>`True` and `False` values aren't case sensitive, so you can also write `true` and `false`.  
Lists are defined with square brackets and separated by commas. Example:  
`[a, list]`  
You can add spaces after or before commas, they're ignored because list items are stripped (trailing & leading spaces are removed)
  
### Logical operators  
Two logical operators are supported: *AND* and *OR*  
Their default syntax is respectively `&&` and `||` (you can change that with the `--and-syntax` and `--or-syntax` flags.)  
#### Example  
Context: a french vocabulary test with synonyms  
  
    Bus
    Bus || Car
    
    Hello
    Bonjour && Salut 

> Note the spaces around the operators: you could remove those,but since individuals items are *stripped* (spaces preceding 
> and following words are removed),  additional spaces don't 
> affect words

*Yes, I know that bonjour and salut are not the same thing, calm down*  
  
#### Escaping the operators symbols  
You would think that putting `\&&` would consider the first ampersand as a literal ampersand, and would therefore not consider this as a special symbol. This feature is on the roadmap, but does not work for now. That's the main reason why`--<operator>-syntax` flags exist.  
     
### Presets
The `src/presets.json` file contains a single preset named *languages*. Obviously, you can add more presets.
The file in itself is an object that contains presets, using their names as the property (the key), and the value being another object, that associates flags with their values :
    
```json    
{
    "preset_name": {
        "flag":"value",
        "other_flag":"other_value"
        ...
    },
    "other_preset_name":{
        ...
    }
}
```

Adding the leading double dash in the flag names is optional.
#### Overriding
If you specify a preset that declares a flag, and that you also specify a value for that flag, the value defined in the learndata file will override the preset's.
*Example*
		

presets.json:
```json
"thingy":{"whitelist":"[stuff, things]"}
```

learndata.txt:
```
--whitelist [spam, eggs]
--preset thingy
```

In this example, `--whitelist` will take the value `[spam, eggs]`, even if `--preset` is declared 
after `--whitelist`.
  

### File example  
Take a look at `learndata_example.txt` to get an idea of what a learndata text file looks like, and how the flags are used and defined.  
  
# Modes  
This script uses 2 different modes: *testing mode* and *training mode*.  
## Training mode  
In this mode, the script cycles through the items (key-value pairs) and ask you to give your answer. If you fail, the script will ask you about it later, until you answered right to all the items.  
## Test mode  
In this mode, the script will ask you for each item *once* (except if you have the [`--ask-for-typos`](#flags) flag set to `True`).  
At the end, it will tell you your grade and the list of items you did not find.

# Logging levels
You can change the logging level with  `LOG_LEVEL` (in `src/consts.py`)

