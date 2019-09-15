import sys
import requests

def to_latex(equation):
    iformat = 'asciimath'
    """ Get MathML from MathMLCloud converter """
    #    resp = requests.post('https://api.mathmlcloud.org/equation',{'math': equation,'mathType':'TeX','mml':'true', 'svg':'true', 'png':'true', 'description':'true'})
    if iformat == 'asciimath':
        mathtype = 'AsciiMath'
    else:   # LaTeX
        mathtype = 'TeX'
    if iformat == 'mathml':
        sys.stderr.write('ERROR: unexpected mathml usage. Should not happen')
        sys.exit(3)
    # try x times to get MathML cloud result:
    for i in range(1, 5):
        # print "Attempt calling MathML Cloud Server: {}".format(i)
        mathml = _call_mathml_cloud(equation, mathtype)
        if mathml != 'null':
            break
    if mathml == 'null':
        sys.stderr.write('ERROR: MathML Cloud Server does not give a result.')
        sys.exit(2)
    return mathml

def _call_mathml_cloud(equation, mathtype):
    """ the HTTP POST to MathMLCloud server """
    try:
        resp = requests.post('https://api.mathmlcloud.org/equation',
                             {'math': equation, 'mathType': mathtype, 'mml': 'true', 'description': 'true'})
        data = resp.json()
        try:
            mathml = data['components'][0]['source']
            return mathml
        except IndexError:
            # bug in MathML Cloud. It sometimes returns 200 but no result
            # (bummer).
            return 'null'
    except Exception as err:
        sys.stderr.write('MathML Cloud ERROR: %sn' % str(err))
        sys.exit(2)