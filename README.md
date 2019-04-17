
# learn_it!  
  
A script that helps you learn stuff.  
**IMPORTANT NOTICE**: This is still an early work-in-progress project, and the only working version is contained in the `main.old.py` file. Most of the features shown here will not work, though the basics (modes and learndata files) will work.    
  
## "learndata" files  
  
At the top of the script, there's a `DATA_FILE` variable.  
Set it to the path (relative to the folder the script is executed in) of the learndata file you want to use, and run the script.  
The file will be parsed, and the training (or testing, see [modes](#modes)) will begin.  
  
    
  
### The "learndata" text file format  
#### Overview  
    --flag-name value  
    # comment // another comment Thing to learn about (the "key") 
    Its correct answer (the "value")  
    
    Other thing you should know by heart 
    Its correct answer  
    
    # The empty line is mandatory, it separates each item
    # See how the files are parsed in Core/main.py's parse() function
  
#### Flags  
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
|case-sensitive|Take case into account when comparing answers|True, False|False    
|good-grade|Grades greater or equal to this will be shown green, while others will be shown red. The good-grade value is calculated by multiplying it by the max-grade value.|0.75|0.5    
|grade-max|Indicate the divisor (maximum grade) used in *testing mode*.|20|100    
|grade-precision|Specify the precision used to round the grade value|1|2  
|header-color|The header's color. Avaible colors: grey, red, green, yellow, blue, magenta, cyan, white|red|cyan  
|header|Text shown at the beginning of the script. `<>` is replaced with `--title`'s value|<>|\-\-\- <> \-\-\-|  
|show-answer-in-testing-mode|In testing mode, show the correct answer when the provided answer was wrong. (This behavior is always active in training mode)|True, False|True  
|show-items-count|Shows a message at the start that says: "Loaded *N* items from *FILE*"|True, False|True  
|show-unknown-flags|Shows a warning if some flags are declared but unknown|True, False|True  
|title|Will be used to display a header at the start of the script. If set to `untitled`, the header will not be displayed.|Chemistry test|untitled    
|whitelist|Use this to filter the things scanned, useful if you have a huge file and already know most of the things in it, but don't know about some other things|[a,comma,separated,list]|[]|    
|~~and-syntax~~|What symbol to use when you want to specify that the correct answer has to be *this* **and** *that*, in no particular order. [More explanation](#logical-operators)|&|&&    
|~~no-colors~~|Deactivate all colors, useful for terminals that don't support [ANSI escape sequences](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors)|True, False|False  
|~~or-syntax~~|Same as `and-syntax`, but used to specify a logical "or": *this* **or** *that*|, |\|\||    
  
  
NOTE: `True` and `False` values aren't case sensitive, so you can also write `true` and `false`.  
Lists are defined with square brackets and separated by commas **without spaces**. Example:  
`[a,list]`  
  
#### Logical operators  
Two logical operators are supported: *AND* and *OR*  
Their default syntax is respectively `&&` and `||` (you can change that with the `--and-syntax` and `--or-syntax` flags.)  
##### Example  
Context: a french vocabulary test with synonyms  
  
 Bus Bus || Car    Hello  
 Bonjour && Salut  
Note the spaces around the operators: you could remove those, but since individuals items are *stripped* (spaces preceding and following words are removed),  additional spaces don't affect words  
  
##### Escaping the operators symbols  
You would think that putting `\&&` would consider the first ampersand as a literal ampersand, and would therefore not consider this as a special symbol. This feature is on the roadmap, but does not work for now. That's the main reason why`--<operator>-syntax` flags exist.  
     
  
#### File example  
Take a look at `learndata/russian.txt` to get an idea of what a learndata text file looks like, and how the flags are used and defined.  
  
## Modes  
This script uses 2 different modes: *testing mode* and *training mode*.  
### Training mode  
In this mode, the script cycles through the items (key-value pairs) and ask you to give your answer. If you fail, the script will ask you about it later, until you answered right to all the items.  
### Test mode  
In this mode, the script will ask you for each item *once* (except if you have the [`--ask-for-typos`](#flags) flag set to `True`).  
At the end, it will tell you your grade and the list of items you did not find.
