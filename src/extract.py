#!/usr/bin/python3
import yaml, os, re
import main
class Extractor():

    TITLE_FMT = '%(notion)s'

    def __init__(self, src, dst=None, file_format=None):
        self._src = src
        if dst is None:
            # Compute destination filepath automatically:
            # Each step below is explained with a generic path, and the part in
            # [brackets] represents what the current line is responnsible for.
            self._dst = os.path.join(
                os.path.dirname(src), # [folder]/learndata/file-name.yaml
                'learndata', # folder/[learndata]/file-name.yaml
                os.path.splitext(os.path.split(src)[1])[0] # folder/learndata/[file-name].yaml
                + '.yaml' # folder/learndata/file-name[.yaml]
            )
        else:
            self._dst = dst

        # Detect file format
        if file_format is None:
            # Get file extension
            ext = os.path.splitext(os.path.split(src)[1])[1]
            markdown = ext[1:] in ('md','markdown','mdown') # ext[:1] because the '.' is in the extension part
            asciidoc = ext[1:] in ('ad', 'asciidoc', 'adoc')

            if markdown:
                self.H1 = re.compile(r'^# (.+)$')
                self.DL = re.compile(r'''(?x)
                                    (?:
                                        (?://)|(?:<!--)learndata  # only matches dl's with the 'learndata' marker. 
                                            (?::(.+)(?:/(.+))?)?  # Optionals: learndata[:subject[/notion]]
                                        (?:-->)?\n                        
                                        (?:
                                            (.+)\n\s*:\s*(.+)     # matches key\n:value, with optional whitespace. Additionnal whitespace will be trimmed later.
                                        )+                        # matches multiple key-value pairs
                                    )+                            # matches multiple dictionnary lists
                                    ''', re.MULTILINE)

            elif asciidoc:
                self.H1 = re.compile(r'^= (.+) =?')
                # the dictionnary list regex expression has mutliple levels: we first search a match for a learndata-marked dl, then we look at each key-value pair
                self.DL = [
                    r'#learndata\n((?:.+::.+)+)'
                ]

            else:
                exit(f"File format '{ext}' is not supported.")


        with open(src, 'r') as f:
            self._raw = f.read()

    def get_infos(self):

        try:
            notion = self.H1.search(self._raw).group(1)
        except AttributeError:
            notion = os.path.splitext(os.path.split(self._src)[1])[0].replace('-', ' ')

        self.infos = {
            'subject': os.path.split(os.path.dirname(self._src))[1], # get subject from blah/foo/spam/subject/file-name.adoc
            'notion': notion
        }

    def compute_flags(self):
        # TITLE_FMT supports key, Key and KEY for each info. Compute them.
        ask_sentence_fmt_params = dict()
        for k,v in self.infos.items():
            ask_sentence_fmt_params[k] = v # Normal value, key
            ask_sentence_fmt_params[k.upper()] = k.upper() # Uppercase
            if len(v) > 1:
                ask_sentence_fmt_params[k[0].upper()+k[1:]] = v[0].upper() + v[1:] # First char uppercase
            else:
                ask_sentence_fmt_params[k[0].upper()+k[1:]] = v.upper()

        self._flags = {
            'whitelist': [],
            'metadata': {
                'subject': self.infos['subject'],
                'notion': self.infos['notion'],
                'runs-count': {
                    'testing': '0',
                    'training': '0',
                },
            },
            'ask-sentence': self.TITLE_FMT % ask_sentence_fmt_params,
        }

    def compute_data(self):
        # "dl" means dictionnary list, (<dl> html element)
        inside_valid_dl = False
        dl_count = 0
        data = dict()
        for line in self._raw.split('\n'):
            if re.match(r'^#learndata(:.+(/.+)?)?', line):
                inside_valid_dl = True
                dl_count += 1
                continue
            
            if inside_valid_dl:
                groups = re.search(r'(.+)::(.+)', line)
                if groups is None:
                    inside_valid_dl = False
                    continue
                q, a = groups.group(1), groups.group(2)
                q, a = [ v.strip() for v in [q,a] ]

                data[q] = a

        self._data = data
        self.list_count = dl_count

    def save_file(self):
        FLAGS_KEY_NAME = main.Learn_it.FLAGS_KEY_NAME
        complete_data = {
            **{FLAGS_KEY_NAME: self._flags}, 
            **self._data
        }
        serialized = yaml.dump(complete_data, Dumper=yaml.CDumper)
        if not os.path.isdir(os.path.dirname(self._dst)):
            os.mkdir(os.path.dirname(self._dst))
        with open(os.path.abspath(self._dst), 'w') as f:
            f.write(serialized)

    def extract(self):
        from termcolor import cprint, colored
        from os.path import dirname, join, split
        destination = join(split(split(self._dst)[0])[1], split(self._dst)[1])
        print(f"Extracting learndata to {destination}...")
        self.get_infos()
        self.compute_flags()
        self.compute_data()
        if self.list_count:
            print(f"Detected {colored(self.list_count, color='cyan')} learndata-marked list(s).")
        else:
            cprint('No learndata-marked lists.', color='red')
            print(f"Check out how to mark lists as learndata here: <{colored('https://mx3creations.com/schoolsyst/help/mark-as-learndata', color='blue')}>")
            exit('Aborted: no learndata-marked lists.')
        self.save_file()
        cprint(f"Done.", color='green')