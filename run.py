import json
import sys
from src.etl import *
from src.embedding import *
from src.utils import evaluate
from src.models import *
import os
from joblib import Parallel, delayed
from tqdm import tqdm
import pandas as pd
from p_tqdm import p_map
TESTPARAMS = json.load(open('config/test-params.json'))
EDAPARAMS = json.load(open('config/eda-params.json'))
DATAPARAMS = json.load(open('config/data-params.json'))
TESTDIR = TESTPARAMS['META_ARGS']['filepath']
EDADIR = EDAPARAMS['META_ARGS']['filepath']
DATADIR = DATAPARAMS['META_ARGS']['filepath']
MODELDIR = 'config/nlp_model.zip'
DATA_NODE2VEC = json.load(open('config/embedding/node2vec.json'))
TEST_NODE2VEC = json.load(open('config/embedding/test-node2vec.json'))
DATA_INFOMAX = json.load(open('config/embedding/infomax.json'))

def env(fp):
    os.makedirs(os.path.join(fp, 'raw', 'posts'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'raw', 'posts_detail'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'raw', 'comments'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'interim', 'label', 'post'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'interim', 'label', 'comment'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'interim', 'graph'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'interim', 'graph'), exist_ok=True)
    os.makedirs(os.path.join(fp, 'processed'), exist_ok=True)
    return

def main(targets):
    if any(['test'in i for i in targets]):
        env(TESTDIR)
    else:
        env(DATADIR)
    # if 'test' in targets:
    #     fetch_submissions(**TESTPARAMS)
    #     submissions_detail(TESTDIR)
    #     comments_detail(TESTDIR)
    if 'data' in targets:
        fetch_submissions(**DATAPARAMS)
        submissions_detail(DATADIR)
        comments_detail(DATADIR)
    if 'sentimental' in targets:
        model, tokenizer = load_nlp('config/nlp_model.zip', DATADIR)
        label_comments(DATADIR, model, tokenizer)
        label_posts(DATADIR, model, tokenizer)
    if 'label' in targets:
        labeling(DATADIR)
    if 'graph' in targets:
        create_graph(DATADIR)
    if 'node2vec' in targets:
        node2vec(DATADIR, DATA_NODE2VEC)
    if 'infomax' in targets:
        infomax(DATADIR, DATA_INFOMAX)
#=================For test============================#
    # if 'data-test' in targets:
    #     fetch_submissions(**TESTPARAMS)
    #     submissions_detail(TESTDIR)
    #     comments_detail(TESTDIR)
    # if 'sentimental-test' in targets:
    #     model, tokenizer = load_nlp('config/nlp_model.zip', TESTDIR)
    #     label_comments(TESTDIR, model, tokenizer)
    #     label_posts(TESTDIR, model, tokenizer)
    # if 'label-test' in targets:
    #     labeling(TESTDIR)
    # if 'graph-test' in targets:
    #     create_graph(TESTDIR)
    # if 'node2vec-test' in targets:
    #     node2vec(TESTDIR, TEST_NODE2VEC)
    if 'test-project' in targets:
        ##
        fetch_submissions(**TESTPARAMS)
        submissions_detail(TESTDIR)
        comments_detail(TESTDIR)
        ##
        model, tokenizer = load_nlp('config/nlp_model.zip', TESTDIR)
        label_comments(TESTDIR, model, tokenizer)
        label_posts(TESTDIR, model, tokenizer)
        labeling(TESTDIR)
        ##
        create_graph(TESTDIR)
        ##
        node2vec(TESTDIR, TEST_NODE2VEC)




if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)