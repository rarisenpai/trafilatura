import os
import re
try:
    from cchardet import detect
except ImportError:
    from charset_normalizer import detect
import time
from nero import NeroExtractLoader
from evaldata import EVAL_PAGES
from lxml import html
import html2text
import html_text
import justext
from boilerpy3 import extractors
from bs4 import BeautifulSoup
from goose3 import Goose
from inscriptis import get_text
from newspaper import fulltext
from newsplease import NewsPlease
from readabilipy import simple_json_from_html_string
from readability import Document
from trafilatura import extract


try:
    from trafilatura.core import baseline
except ImportError:
    baseline = None

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
boilerpipe_extractor = extractors.ArticleExtractor()
g = Goose()

def trim(string):
    '''Remove unnecessary spaces within a text string'''
    if string is not None:
        string = ' '.join(re.split(r'\s+', string.strip(' \t\n\r'), flags=re.UNICODE|re.MULTILINE))
        string = string.strip()
    return string


def load_document_binary(filename):
    '''load mock page from samples'''
    mypath = os.path.join(TEST_DIR, 'cache', filename)
    if not os.path.isfile(mypath):
        mypath = os.path.join(TEST_DIR, 'eval', filename)
    with open(mypath, 'rb') as inputf:
        htmlstring = inputf.read()
    return htmlstring


def load_document_string(filename):
    '''load mock page from samples'''
    mypath = os.path.join(TEST_DIR, 'cache', filename)
    if not os.path.isfile(mypath):
        mypath = os.path.join(TEST_DIR, 'eval', filename)
    try:
        with open(mypath, 'r') as inputf:
            htmlstring = inputf.read()
    except UnicodeDecodeError:
        with open(mypath, 'rb') as inputf:
            htmlbinary = inputf.read()
        guessed_encoding = detect(htmlbinary)['encoding']
        if guessed_encoding is not None:
            try:
                htmlstring = htmlbinary.decode(guessed_encoding)
            except UnicodeDecodeError:
                htmlstring = htmlbinary
        else:
            print('Encoding error')
    return htmlstring

def evaluate_result(result, item):
    '''evaluate result contents'''
    true_positives = 0
    false_negatives = 0
    false_positives = 0
    true_negatives = 0
    # report if problematic
    if len(item['with']) == 0 or len(item['with']) > 6:
        print('counter', item)
    if len(item['without']) == 0 or len(item['without']) > 6:
        print('counter', item)

    if result is not None and type(result) is str:
        # expected output
        for to_include in item['with']:
            if to_include in result:
                true_positives += 1
            else:
                false_negatives += 1
        # unwanted output
        for to_exclude in item['without']:
            if to_exclude in result:
                false_positives += 1
            else:
                true_negatives += 1
    # add up as bulk counts
    else:
        false_negatives += len(item['with'])
        true_negatives += len(item['without'])
    return true_positives, false_negatives, false_positives, true_negatives

def run_baseline_2(htmlstring):
    '''run bare text extraction within lxml'''
    # binary/string as input tweak
    try:
        tree = html.fromstring(htmlstring)
    except ValueError:
        tree = html.fromstring(htmlstring.encode('utf8'))
    result = None
    # try json-ld
    for elem in tree.xpath('//script[@type="application/ld+json"]'):
        if elem.text and '"articleBody":' in elem.text:
            mymatch = re.search(r'"articleBody":"(.+?)","', elem.text)
            if mymatch:
                result = mymatch.group(1)
                result = result.replace('\\"', '"')
                # result = trim(result)
                break
    if result is not None:
        return result
    #results = set()
    resultlist = []
    # iterate potentially relevant elements
    for element in tree.iter('blockquote', 'code', 'p', 'pre', 'q'): # 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        entry = element.text_content()
        resultlist.append(entry)
    result = '\n'.join(resultlist)
    return result

def run_baseline(htmlstring):
    '''run bare text extraction within lxml'''
    if baseline is not None:
        _, result, _ = baseline(htmlstring)
        return result
    result = run_baseline_2(htmlstring)
    return result

def calculate_scores(mydict):
    '''output weighted result score'''
    tp, fn, fp, tn = mydict['true positives'], mydict['false negatives'], mydict['false positives'], mydict['true negatives']
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    accuracy = (tp+tn)/(tp+tn+fp+fn)
    fscore = (2*tp)/(2*tp + fp + fn)  # 2*((precision*recall)/(precision+recall))
    return precision, recall, accuracy, fscore


def run_trafilatura(htmlstring):
    '''run trafilatura (without fallback) on content'''
    return extract(
        htmlstring,
        no_fallback=True,
        include_comments=False,
        include_tables=True,
        include_formatting=False,
    )


def run_justext(htmlstring):
    '''try with the generic algorithm justext'''
    paragraphs = justext.justext(htmlstring, justext.get_stoplist("German"), 50, 200, 0.1, 0.2, 0.2, 200, True)  # stop_words
    valid = [
        paragraph.text
        for paragraph in paragraphs
        if not paragraph.is_boilerplate
    ]

    return ' '.join(valid)   # sanitize(result)


def run_trafilatura_fallback(htmlstring):
    '''run trafilatura (with fallback) on content'''
    return extract(
        htmlstring,
        no_fallback=False,
        include_comments=False,
        include_tables=True,
        include_formatting=False,
    )


def run_trafilatura_precision(htmlstring):
    '''run trafilatura with preference for precision'''
    return extract(
        htmlstring,
        no_fallback=False,
        favor_precision=True,
        include_comments=False,
        include_tables=True,
        include_formatting=False,
    )


def run_trafilatura_recall(htmlstring):
    '''run trafilatura with preference for recall'''
    return extract(
        htmlstring,
        no_fallback=False,
        favor_recall=True,
        include_comments=False,
        include_tables=True,
        include_formatting=False,
    )


def run_goose(htmlstring):
    '''try with the goose algorithm'''
    try:
        article = g.extract(raw_html=htmlstring)
        return article.cleaned_text # sanitize(article.cleaned_text)
    except ValueError:
        return ''


def run_readability(htmlstring):
    '''try with the Python3 port of readability.js'''
    try:
        doc = Document(htmlstring)
        return doc.summary() # sanitize(doc.summary())
    except Exception as err:
        print('Exception:', err)
        return ''

def run_inscriptis(htmlstring):
    '''try with the inscriptis module'''
    try:
        text = get_text(htmlstring)
    except TypeError:
        text = ''
    return text # sanitize(text)


def run_html2text(htmlstring):
    '''try with the html2text module'''
    try:
        text = html2text.html2text(htmlstring)
        # sanitize(text)
    except TypeError:
        text = ''
    return text


def run_html_text(htmlstring):
    '''try with the html2text module'''
    try:
        text = html_text.extract_text(htmlstring, guess_layout=False)
    except TypeError:
        text = ''
    return text


def run_newspaper(htmlstring):
    '''try with the newspaper module'''
    try:
        text = fulltext(htmlstring) # sanitize(fulltext(htmlstring))
    except AttributeError:
        return ''
    return text


def run_boilerpipe(htmlstring):
    '''try with the boilerpipe algorithm'''
    try:
        content = boilerpipe_extractor.get_content(htmlstring)
        # sanitize(boilerpipe_extractor.get_content(htmlstring))
    except Exception:
        #print('Boilerpipe exception:', err)
        content = ''
    return content


def run_newsplease(htmlstring):
    '''try with newsplease'''
    try:
        article = NewsPlease.from_html(htmlstring, url=None)
        return article.maintext # sanitize(article.maintext)
    except Exception as err:
        return ''

def run_readabilipy(htmlstring):
    '''try with the readability.py module'''
    try:
        article = simple_json_from_html_string(htmlstring, use_readability=True)
        returnlist = [textelem['text'] for textelem in article['plain_text']]
        return '\n'.join(returnlist) # sanitize(content)
    except Exception as err:
        #print('Readabilipy exception:', err)
        return ''

def run_bs4(htmlstring):
    '''try with the BeautifulSoup module'''
    return BeautifulSoup(htmlstring, features='lxml').get_text(strip=True)


def evaluate_result(result, item):
    '''evaluate result contents'''
    true_positives = 0
    false_negatives = 0
    false_positives = 0
    true_negatives = 0
    # report if problematic
    if len(item['with']) == 0 or len(item['with']) > 6:
        print('counter', item)
    if len(item['without']) == 0 or len(item['without']) > 6:
        print('counter', item)
    if result is not None and type(result) is str:
        # expected output
        for to_include in item['with']:
            if to_include in result:
                true_positives += 1
            else:
                false_negatives += 1
        # unwanted output
        for to_exclude in item['without']:
            if to_exclude in result:
                false_positives += 1
            else:
                true_negatives += 1
    # add up as bulk counts
    else:
        false_negatives += len(item['with'])
        true_negatives += len(item['without'])
    return true_positives, false_negatives, false_positives, true_negatives


template_dict = {'true positives': 0, 'false positives': 0, 'true negatives': 0, 'false negatives': 0, 'time': 0}

def run_nero(plain_text, url):
    extractor = NeroExtractLoader(api_token="zpka_167f1c95519b44fdb76dbd1c47190971_6a819a29",org_uuid="39c4c3a2-6287-411b-b60f-ef34900d176f",url=url, plain_text=plain_text)
    data = extractor.extract()
    return data

i = 0
template_dict = {'true positives': 0, 'false positives': 0, 'true negatives': 0, 'false negatives': 0, 'time': 0}
nero, baseline_result, trafilatura_result, justext_result, trafilatura_fallback_result, trafilatura_precision, trafilatura_recall, goose_result, readability_result, inscriptis_result, newspaper_result, html2text_result, html_text_result, dragnet_result, boilerpipe_result, newsplease_result, jparser_result, readabilipy_result, resiliparse_result, bs4_result = {},{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
nero.update(template_dict)
baseline_result.update(template_dict)
trafilatura_result.update(template_dict)
justext_result.update(template_dict)
trafilatura_fallback_result.update(template_dict)
trafilatura_precision.update(template_dict)
trafilatura_recall.update(template_dict)
goose_result.update(template_dict)
readability_result.update(template_dict)
inscriptis_result.update(template_dict)
newspaper_result.update(template_dict)
html2text_result.update(template_dict)
html_text_result.update(template_dict)
boilerpipe_result.update(template_dict)
newsplease_result.update(template_dict)
readabilipy_result.update(template_dict)
resiliparse_result.update(template_dict)
bs4_result.update(template_dict)
for item in EVAL_PAGES:
    print(item)
    if len(EVAL_PAGES[item]['file']) == 0:
        continue
    htmlstring = load_document_string(EVAL_PAGES[item]['file'])
    url = item
    item_name = item[:25]
    if htmlstring is None:
        continue
    start = time.time()
    try:
        result = run_nero(htmlstring, url)['text']
    except Exception as e:
        result = ''
    # with open(f"results/nero_{re.sub(r'[:/]', '',item_name)}.txt", 'w') as f:
    #     f.write(result)
    nero['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    nero['true positives'] += tp
    nero['false positives'] += fp
    nero['true negatives'] += tn
    nero['false negatives'] += fn

    start = time.time()
    result = run_html2text(htmlstring)
    html2text_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    html2text_result['true positives'] += tp
    html2text_result['false positives'] += fp
    html2text_result['true negatives'] += tn
    html2text_result['false negatives'] += fn
    # html_text
    start = time.time()
    result = run_html_text(htmlstring)
    html_text_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    html_text_result['true positives'] += tp
    html_text_result['false positives'] += fp
    html_text_result['true negatives'] += tn
    html_text_result['false negatives'] += fn
    # inscriptis
    start = time.time()
    result = run_inscriptis(htmlstring)
    inscriptis_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    inscriptis_result['true positives'] += tp
    inscriptis_result['false positives'] += fp
    inscriptis_result['true negatives'] += tn
    inscriptis_result['false negatives'] += fn
    # bare lxml
    start = time.time()
    # result = run_baseline(htmlstring)
    # # with open(f"results/baseline_{re.sub(r'[:/]', '',item_name)}.txt", 'w') as f:
    #     f.write(result)
    baseline_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    baseline_result['true positives'] += tp
    baseline_result['false positives'] += fp
    baseline_result['true negatives'] += tn
    baseline_result['false negatives'] += fn
    # trafilatura
    start = time.time()
    result = run_trafilatura(htmlstring)
    trafilatura_result['time'] += time.time() - start
    # with open(f"results/trafilatura_{re.sub(r'[:/]', '',item_name)}.txt", 'w') as f:
    #     if not result:
    #         result = ''
    #     f.write(result)
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    trafilatura_result['true positives'] += tp
    trafilatura_result['false positives'] += fp
    trafilatura_result['true negatives'] += tn
    trafilatura_result['false negatives'] += fn
    # justext
    start = time.time()
    result = run_justext(htmlstring)
    justext_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    justext_result['true positives'] += tp
    justext_result['false positives'] += fp
    justext_result['true negatives'] += tn
    justext_result['false negatives'] += fn
    # trafilatura + X
    start = time.time()
    result = run_trafilatura_fallback(htmlstring)
    # with open(f"results/trafilatura_fallback_{re.sub(r'[:/]', '',item_name)}.txt", 'w') as f:
    #     f.write(result)
    trafilatura_fallback_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    trafilatura_fallback_result['true positives'] += tp
    trafilatura_fallback_result['false positives'] += fp
    trafilatura_fallback_result['true negatives'] += tn
    trafilatura_fallback_result['false negatives'] += fn
    # trafilatura + precision
    start = time.time()
    result = run_trafilatura_precision(htmlstring)
    # with open(f"results/trafilatura_precision_{re.sub(r'[:/]', '',item_name)}.txt", 'w') as f:
    #     f.write(result) 
    trafilatura_precision['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    trafilatura_precision['true positives'] += tp
    trafilatura_precision['false positives'] += fp
    trafilatura_precision['true negatives'] += tn
    trafilatura_precision['false negatives'] += fn
    # trafilatura + recall
    start = time.time()
    result = run_trafilatura_recall(htmlstring)
    # with open(f"results/trafilatura_recall_{re.sub(r'[:/]', '',item_name)}.txt", 'w') as f:
        # f.write(result)
    trafilatura_recall['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    trafilatura_recall['true positives'] += tp
    trafilatura_recall['false positives'] += fp
    trafilatura_recall['true negatives'] += tn
    trafilatura_recall['false negatives'] += fn
    # readability
    start = time.time()
    result = run_readability(htmlstring)
    readability_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    readability_result['true positives'] += tp
    readability_result['false positives'] += fp
    readability_result['true negatives'] += tn
    readability_result['false negatives'] += fn
    # goose
    start = time.time()
    result = run_goose(htmlstring)
    goose_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    goose_result['true positives'] += tp
    goose_result['false positives'] += fp
    goose_result['true negatives'] += tn
    goose_result['false negatives'] += fn
    # newspaper
    start = time.time()
    result = run_newspaper(htmlstring)
    newspaper_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    newspaper_result['true positives'] += tp
    newspaper_result['false positives'] += fp
    newspaper_result['true negatives'] += tn
    newspaper_result['false negatives'] += fn
    # boilerpipe
    start = time.time()
    result = run_boilerpipe(htmlstring)
    boilerpipe_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    boilerpipe_result['true positives'] += tp
    boilerpipe_result['false positives'] += fp
    boilerpipe_result['true negatives'] += tn
    boilerpipe_result['false negatives'] += fn
    # newsplease
    start = time.time()
    result = run_newsplease(htmlstring)
    newsplease_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    newsplease_result['true positives'] += tp
    newsplease_result['false positives'] += fp
    newsplease_result['true negatives'] += tn
    newsplease_result['false negatives'] += fn
    start = time.time()
    result = run_readabilipy(htmlstring)
    readabilipy_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    readabilipy_result['true positives'] += tp
    readabilipy_result['false positives'] += fp
    readabilipy_result['true negatives'] += tn
    readabilipy_result['false negatives'] += fn
    start = time.time()
    result = run_bs4(htmlstring)
    bs4_result['time'] += time.time() - start
    tp, fn, fp, tn = evaluate_result(result, EVAL_PAGES[item])
    bs4_result['true positives'] += tp
    bs4_result['false positives'] += fp
    bs4_result['true negatives'] += tn
    bs4_result['false negatives'] += fn
    # counter
    i += 1


print('number of documents:', i)

print('baseline')
print(baseline_result)
try:
    print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(baseline_result)))
except ZeroDivisionError:
    pass
print('nero')
print(nero)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(nero)))
print(f"time diff.: {nero['time'] / baseline_result['time']:.2f}")
print('html2text')
print(html2text_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(html2text_result)))
print(f"time diff.: {html2text_result['time'] / baseline_result['time']:.2f}")

print('html_text')
print(html_text_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(html_text_result)))
print(f"time diff.: {html_text_result['time'] / baseline_result['time']:.2f}")

print('inscriptis')
print(inscriptis_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(inscriptis_result)))
print(f"time diff.: {inscriptis_result['time'] / baseline_result['time']:.2f}")

print('justext')
print(justext_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(justext_result)))
print(f"time diff.: {justext_result['time'] / baseline_result['time']:.2f}")

print('goose')
print(goose_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(goose_result)))
print(f"time diff.: {goose_result['time'] / baseline_result['time']:.2f}")

print('newspaper')
print(newspaper_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(newspaper_result)))
print(f"time diff.: {newspaper_result['time'] / baseline_result['time']:.2f}")

print('boilerpipe')
print(boilerpipe_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(boilerpipe_result)))
print(f"time diff.: {boilerpipe_result['time'] / baseline_result['time']:.2f}")

print('newsplease')
print(newsplease_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(newsplease_result)))
print(f"time diff.: {newsplease_result['time'] / baseline_result['time']:.2f}")

print('readability')
print(readability_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(readability_result)))
print(f"time diff.: {readability_result['time'] / baseline_result['time']:.2f}")

print('readabilipy')
print(readabilipy_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(readabilipy_result)))
print(f"time diff.: {readabilipy_result['time'] / baseline_result['time']:.2f}")

print('bs4')
print(bs4_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(bs4_result)))
print(f"time diff.: {bs4_result['time'] / baseline_result['time']:.2f}")

print('trafilatura')
print(trafilatura_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(trafilatura_result)))
print(f"time diff.: {trafilatura_result['time'] / baseline_result['time']:.2f}")

print('trafilatura + X')
print(trafilatura_fallback_result)
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(trafilatura_fallback_result)))
print(f"time diff.: {trafilatura_fallback_result['time'] / baseline_result['time']:.2f}")

print('trafilatura precision')
print(trafilatura_precision)
print(f"time diff.: {trafilatura_precision['time'] / baseline_result['time']:.2f}")
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(trafilatura_precision)))

print('trafilatura recall')
print(trafilatura_recall)
print(f"time diff.: {trafilatura_recall['time'] / baseline_result['time']:.2f}")
print("precision: %.3f recall: %.3f accuracy: %.3f f-score: %.3f" % (calculate_scores(trafilatura_recall)))