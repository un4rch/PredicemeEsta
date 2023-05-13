# Precision: TP/(TP+FP)
           # De todas las instancias que ha predecido como positive, realmente cuantas son 
# Recall: TP/(TP+FN)
           # De todos los positivos en realidad, cuantos hemos detectado bien
# F-score: 2*(P*R)/(P+R)
           # Una combinacion de Precision y  Recall en un solo valor (una especie de media)
# Accuracy: (TP+TN)/(TP+TN+FP+FN)
           # Funciona mal si las clases estan desbalanceadas
           # Ejemplo: 1000 datos: 950 son 1 y 50 son 0
           #          Nuestro modelo dice siempre 1, entonces el accuracy es 0.95. Pero el modelo es malo, porque no predice nada bien, simplemente dice 1
# Macro-average:
           # Se tiene en cuenta en clases balanceadas
# Micro-average:
           # Se tiene en cuenta en clases desbalanceadas

import signal
import csv
import getopt
import sys
import os
import pandas as pd
import csv
import time
import json
#import datetime
#import ciso8601
# ciso8601.parse_datetime(ml_dataset[columna])
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
from imblearn.over_sampling import SMOTE
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
#from sklearn.linear_model import LinearRegression
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
#from sklearn.metrics import precision_score
#from sklearn.metrics import recall_score
#from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
import pickle
from preprocessor import Preprocessor
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB, BernoulliNB, ComplementNB
from mixed_naive_bayes import MixedNB
#LDA GENSIM
import gensim
from gensim import corpora
from gensim import models
from gensim.models import LdaModel
from sklearn.decomposition import LatentDirichletAllocation
import chardet
from gensim.matutils import Sparse2Corpus
from scipy import sparse
from gensim.models import CoherenceModel


inputFile = None
excludedColumns = None
NLcolumns = None
NLtechnique = "tfidf"
targetColumn = None
imputeOption = 'MODE'
imputeOptions = ['MEAN', 'MEDIAN', 'MODE', 'CONSTANT']
algorithm = None
printStats = False
algorithms = ['knn', 'decision tree', 'naive bayes', 'logistic regression', 'random forest']
rescaleOption = None
rescaleOptions = ['MAX', 'MINMAX', 'Z-SCALE']
testSize = 0.2
randomState = None
kValues = None
wValues = None
dValues = None
max_depths = None
min_samples_splits = None
min_samples_leafs = None
outputModelName = None
evaluation = None
esMixedNB = None
switch = True
clustering = False
airline = None
sentiment = None

def signal_handler(sig_num, frame):
    print("[!] Saliendo del programa...")
    sys.exit(1)

def helpPanel():
    #python crearModelo.py -a 0 1,5 1,2 uniform,distance -f iris.csv -i mode -t Especie -s -o modelo.pkl
    #python crearModelo.py -a 1 -f iris.csv -i mode -t Especie -s
    #-i CONSTANT 10 --> imputeValue = 10
    #-i <file> --> por cada columna
    #Defaults: testSize=0.2
    print()
    print("\tHelp")
    print("\t----")
    print("\tUsage: python crearModelo.py -f <input-dataset> -t <target-column> -a <algorithm-num>  --impute-method <mehtod> [optional-args]")
    print()
    print("\tArguments")
    print("\t---------")
    print('\t-o|--ouput <outputFile>\t\t\tOutput name for the model (ex: model --> modelAlgorithm.pkl modelClustering.pkl)')
    print('\t-f|--file <inputFile>\t\t\tInput csv dataset file')
    print('\t-e|--exclude <excludeHeaders>\t\tcoma separated list to exclude columns')
    print('\t-t|--target <target column header>\tTarget column header name')
    print('\t-s|--stats \t\t\t\tPrint trained model stats')
    print('\t-a|--algorithm <number>\t\t\tSelect the algorithm to use')
    print('\t\t\t\t\t\t\t0: knn (-a 0 <k> <d> <w>)')
    print('\t\t\t\t\t\t\t\tk=[k1,k2,k3,...|kmin:kmax] odd numbers') 
    print('\t\t\t\t\t\t\t\td=[1,2]')
    print('\t\t\t\t\t\t\t\tw=[unform,distance]')
    print('\t\t\t\t\t\t\t1: decision tree (-a 1 <max_depth> <min_samples_split> <min_samples_leaf>)')
    print('\t\t\t\t\t\t\t\tmax_depth=[d1,d2,d3...|dmin:dmax] any numbers')
    print('\t\t\t\t\t\t\t\tmin_samples_split=[1,2]')
    print('\t\t\t\t\t\t\t\tmin_samples_leaf=[1,2]')
    #print('\t\t\t\t\t\t\t2: random forest')
    print('\t\t\t\t\t\t\t2: Naibe Bayes (-a 2)')
    print('\t\t\t\t\t\t\t3: Logistic Regression (-a 3)')
    print('\t-h|--help \t\t\t\tPrint this help panel')
    print('\t-i|--impute <name>\t\t\tChoose impute method (filename,MEAN,MEDIAN,MODE,CONSTANT <n>)')
    print('\t\t\t\t\t\t\tfilename: file containing impute method for each column splicitly')
    print('\t\t\t\t\t\t\tOTHER: one same impute method for all columns')
    print('\t-r|--rescale <name>\t\t\tChoose rescale method (filename,MAX,MINMAX,Z-SCALE)')
    print('\t\t\t\t\t\t\tfilename: file containing rescale method for each column splicitly')
    print('\t\t\t\t\t\t\tOTHER: one same rescale method for all columns')
    print('\t-m|--measure <name>\t\t\tChoose measure method (macro,micro,weghted)')
    print('\t-v|--vectorize <name>\t\t\tChoose NL vectorize method (tfidf,bow)')
    print('\t-n|--natural-language <colnames>\t\t\tSpecify columns that contains natural language')
    print('\t--random-state <int>\t\t\tSeed to separate train and test dataset the same way')
    print('\t--test-size <float>\t\t\tChoose the test size')
    print('\t-c|--clustering <T/F>\t\t\tDo clustering')
    print()
    print('\tDefaults')
    print('\t--------')
    print('\toutput model: False')
    print('\tprint stats: False')
    print('\ttest size: 0.2')
    print('\timpute method: MODE (if needed)')
    print('\trescale method: None (do not rescale the dataset)')
    print('\tMeasure method: weighted')
    print()
    print('\tExamples')
    print('\t--------')
    print('\t$ python crearModelo.py -f iris.csv -a 0 1,3,5 1,2 uniform,distance -i MODE -t Especie -s -o model.pkl')
    print('\t\t12 combinations of hyperparameters for knn')
    print('\t\timpute MODE for all columns')
    print('\t\ttarget column "Especie"')
    print('\t\tprint model stats')
    print('\t\toutput model "model.pkl"')
    print('\t$ python crearModelo.py -f iris.csv -a 0 1,7 2 distance -e -i impute.csv -r rescale.csv -t Especie -e Ancho de sepalo,Largo de petalo -o model.pkl')
    print('\t\t2 combinations of hyperparameters for knn')
    print('\t\timpute with file for all columns')
    print('\t\trescale with file for all columns')
    print('\t\ttarget column "Especie"')
    print('\t\tdo not take into account columns "Ancho de sepalo" and "Largo de petalo" to train the model')
    print('\t\tdo not print model stats')
    print('\t\toutput model "model.pkl"')
    print()
    print('\tImpute file:')
    print('\t\tcol1,MODE')
    print('\t\tcol2,MEAN')
    print('\t\tcol3,CONSTANT,3')
    print()
    print('\tRescale file:')
    print('\t\tcol1,MINMAX')
    print('\t\tcol2,Z-SCALE')
    print('\t\tcol3,MAX')
    print()

def comprobarArgumentosEntradaObligatorios():
    global imputeOption
    global kValues
    global dValues
    global wValues
    global max_depths
    global min_samples_splits
    global min_samples_leafs
    global airline
    global sentiment
    error = False
    if inputFile == None or not os.path.exists(inputFile):
        print("[!] Error: Especifica cual es el fichero que contiene los datos.")
        error = True
    if targetColumn == None:
        print("[!] Error: Especifica cual es la columna objetivo.")
        error = True
    if algorithm == None:
        print("[!] Error: Especifica cual es el algoritmo que quieres usar para hacer el modelo")
        error = True
    if clustering:
        shift = 2
        for i,value in enumerate(sys.argv[1:]):
            if value == '-c' or value == '--clustering':
                values = sys.argv[1:][i+shift:i+shift+2]
                airline = values[0]
                sentiment = values[1]
        if airline == None or sentiment == None:
            print("[!] Debes especificar una aerolinea y un sentimiento")
            sys.exit(1)
    if imputeOption == 'CONSTANT':
        shift = 1
        for i,value in enumerate(sys.argv[1:]):
            if value.upper() == 'CONSTANT':
                const = sys.argv[1:][i+shift]
                try:
                    if not const in remainder:
                        int('Throw error')
                    const = float(sys.argv[1:][i+shift])
                    imputeOption = f'{str(value.upper())},{str(const)}'
                except:
                    print('[!] CONSTANT only supports integer values')
                    sys.exit(1)
    shift = 2
    error = False
    for i,value in enumerate(sys.argv[1:]):
        if value in ['-a', '--algorithm']:
            values = sys.argv[1:][i+shift:i+shift+3]
            if int(sys.argv[1:][i+1]) != 2 and int(sys.argv[1:][i+1]) != 3:
                for value in values:
                    if value not in remainder:
                        error = True
            if not error:
                if algorithms[algorithm] == 'knn':
                    kValues = []
                    try:
                        if values[0].find(':') != -1:
                            maxMinValues = values[0].split(':')
                            kValues = [i for i in range(int(maxMinValues[0]),int(maxMinValues[1])+2,2)]
                        else:
                            kValues = [int(i) for i in values[0].split(',')]
                    except:
                        print('[!] Rango mal especificado para el barrido de hyperparametros k del knn')
                        sys.exit(1)
                    dValues = [int(i) for i in values[1].split(',')]
                    wValues = [str(i) for i in values[2].split(',')]
                elif algorithms[algorithm] == 'decision tree':
                    max_depths = []
                    try:
                        if values[0].find(':') != -1:
                            maxMinValues = values[0].split(':')
                            max_depths = [i for i in range(int(maxMinValues[0]),int(maxMinValues[1])+1,1)]
                        else:
                            max_depths = [int(i) for i in values[0].split(',')]
                    except:
                        print('[!] Rango mal especificado para el barrido de hyperparametros max_depth del decision tree')
                        sys.exit(1)
                    min_samples_splits = [int(i) for i in values[1].split(',')]
                    min_samples_leafs = [int(i) for i in values[2].split(',')]
            else:
                if algorithms[algorithm] == 'knn':
                    print('[!] Indica bien los argumentos del algoritmo knn')
                    sys.exit(1)
                elif algorithms[algorithm] == 'decision tree':
                    print('[!] Indica bien los argumentos del algoritmo decision tree')
                    sys.exit(1)
    if error:
        helpPanel()
        sys.exit(1)

def cargarDataset(pInputFile):
    ml_dataset = None
    with open(pInputFile, 'r', encoding='utf-8') as csvFile:
        primerosDatos = pd.read_csv(pInputFile) # Leer el fichero
        csvFile.seek(0) # Regresa al inicio del archivo
        lector = csv.reader(csvFile, primerosDatos, delimiter=',')
        tiene_header = csv.Sniffer().has_header(csvFile.read()) # Detecta si el archivo tiene encabezado
        if tiene_header: #Si tiene header se carga directamente
            ml_dataset = pd.read_csv(pInputFile, low_memory=False)
        else: #Si no tiene header se añade uno por defecto
            csvFile.seek(0)
            num_cols = len(csvFile.readline().split(','))
            headers = []
            for i in range(1,num_cols+1):
                headers.append("col"+str(i))
            ml_dataset = pd.read_csv(pInputFile, names=headers, header=None, low_memory=False)
    return ml_dataset

def crearModelo(pml_dataset, palgorithm, ptarget_map):
    global evaluation
    global randomState
    global esMixedNB
    if evaluation != None:
        fScoreAverage = evaluation
    else:
        fScoreAverage = 'weighted'

    if len(ptarget_map) == 2:
        if len(pml_dataset) >= 10000:
            sampler = RandomUnderSampler(sampling_strategy=0.5) #Coge el 50% de las muestras de la clase mayoritaria para balancear ambas clases
        else:
            sampler = RandomOverSampler(sampling_strategy='minority')
        #TODO: oversample
    elif len(ptarget_map) >= 3:
        if len(pml_dataset) >= 10000:
            sampler = RandomUnderSampler() #Coge el 50% de las muestras de la clase mayoritaria para balancear ambas clases
        else:
            sampler = SMOTE()
    if randomState != None:
        train, test = train_test_split(pml_dataset,test_size=testSize,random_state=randomState,stratify=pml_dataset[targetColumn])
    else:
        train, test = train_test_split(pml_dataset,test_size=testSize,random_state=42,stratify=pml_dataset[targetColumn])
    
    trainX = train.drop(targetColumn, axis=1) #train dataset de datos sin target
    testX = test.drop(targetColumn, axis=1) #test dataset sin target
    trainY = np.array(train[targetColumn]) #train columna target
    testY = np.array(test[targetColumn]) #test columna target
    
    trainX, trainY = sampler.fit_resample(trainX,trainY)
    testX, testY = sampler.fit_resample(testX, testY)

    modelos = []
    if algorithms[palgorithm] == 'knn':
        for k in kValues:
            for d in dValues:
                for w in wValues:
                    clf = KNeighborsClassifier(n_neighbors=k,
                        weights=w,
                        algorithm='auto',
                        leaf_size=30,
                        p=d)
                    clf.class_weight = "balanced"
                    clf.fit(trainX, trainY)
                    predictions = clf.predict(testX)
                    fScore = f1_score(testY, predictions, average=fScoreAverage)
                    reporte = classification_report(testY,predictions)
                    matriz_confusion = confusion_matrix(testY, predictions, labels=[1,0])
                    probas = clf.predict_proba(testX)
                    predictions = pd.Series(data=predictions, index=testX.index, name='predicted_value')
                    cols = [
                        u'probability_of_value_%s' % label
                        for (_, label) in sorted([(int(ptarget_map[label]), label) for label in ptarget_map])
                    ]
                    probabilities = pd.DataFrame(data=probas, index=testX.index, columns=cols)
                    modelos.append([clf,fScore,reporte,{'k': k, 'w': w, 'd': d}])
    elif algorithms[palgorithm] == 'decision tree':
        for max_depth in max_depths:
            for min_samples_split in min_samples_splits:
                for min_samples_leaf in min_samples_leafs:
                    clf = DecisionTreeClassifier(
                        max_depth = max_depth,
                        min_samples_split = min_samples_split,
                        min_samples_leaf = min_samples_leaf
                    )
                    clf.class_weight = "balanced"
                    clf.fit(trainX, trainY)
                    predictions = clf.predict(testX)        
                    fScore = f1_score(testY, predictions, average=fScoreAverage)
                    reporte = classification_report(testY,predictions)
                    #matriz_confusion = confusion_matrix(testY, predictions, labels=[1,0])
                    modelos.append([clf,fScore,reporte,{'max_depth': max_depth, 'min_samples_split': min_samples_split, 'min_samples_leaf': min_samples_leaf}])
    elif algorithms[palgorithm] == 'naive bayes':
        usedNaiveBayes = None
        models = [GaussianNB(), MixedNB(), MultinomialNB(), BernoulliNB(), ComplementNB()]
        fscores = []
        for clf in models:
            clf.class_weight = "balanced"
            if isinstance(clf, GaussianNB):
                ## GAUSSIAN NAIVE BAYES ##
                discretizer = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')  #Se utiliza comunmente con GaussianNB, ya que GaussianNB asume distribución normal, por lo que la discretización de las continuas puede mejorar su desempeño
                trainX_aux = discretizer.fit_transform(trainX)
                clf.fit(trainX_aux, trainY)
            else:
                clf.fit(trainX, trainY)
            predictions = clf.predict(testX)
            fScore = f1_score(testY, predictions, average=fScoreAverage)
            fscores.append(fScore)

            #scores = cross_val_score(model, X, y, cv=5, scoring='f1_macro')
            #fscores.append(scores.mean())

        best_model_index = fscores.index(max(fscores))
        best_model = models[best_model_index]

        clf = best_model
        if isinstance(best_model, GaussianNB):
            usedNaiveBayes = "GaussianNB"
        elif isinstance(best_model, MixedNB):
            usedNaiveBayes = "MixedNB"
        elif isinstance(best_model, MultinomialNB):
            usedNaiveBayes = "MultinomialNB"
        elif isinstance(best_model, BernoulliNB):
            usedNaiveBayes = "BernoulliNB"
        elif isinstance(best_model, ComplementNB):
            usedNaiveBayes = "ComplementNB"
        reporte = classification_report(testY,predictions)
        #print("fscore: " + str(fScore))
        #recall = recall_score(testY, predictions, average=fScoreAverage)
        #print("recall: " + str(recall))
        #precision = precision_score(testY, predictions, average=fScoreAverage)
        #print("precision: " + str(precision))
        modelos.append([clf,fScore,reporte,{'Naive type': usedNaiveBayes}])
    elif algorithms[palgorithm] == 'logistic regression':
        clf = LogisticRegression(penalty="l2",random_state=randomState, max_iter=1000)
        clf.class_weight = "balanced"
        clf.fit(trainX, trainY)
        preditctionsLR = clf.predict(testX)
        fScoreLR = f1_score(testY, preditctionsLR, average=fScoreAverage)
        #print("fscore: " + str(fScoreLR))
        #recall = recall_score(testY, preditctionsLR, average=fScoreAverage)
        #print("recall: " + str(recall))
        #precision = precision_score(testY, preditctionsLR, average=fScoreAverage)
        #print("precision: " + str(precision))
        reporteLR = classification_report(testY, preditctionsLR)
        #print(reporteLR)
        modelos.append([clf,fScoreLR,reporteLR,{'penalty': 'l2', 'max_iter':1000}])

        ##EDER
        #parameters = {'penalty': ['l1', 'l2'], 'C': [0.1, 1, 10], 'solver': ['liblinear', 'saga']}
        #clf = LogisticRegression()

        #grid_search = GridSearchCV(clf, parameters, cv=5)     # Búsqueda de la mejor combinación de parámetros
        ##grid_search.class_weight = "balanced"
        #grid_search.fit(trainX, trainY) #No es un estimador, es un objeto que ayuda a encontrar el mejor estimador

        #print("Mejor combinación de parámetros:", grid_search.best_params_)
        #print("Mejor puntuación de la validación cruzada:", grid_search.best_score_)
        #clf = grid_search.best_estimator_
        #preditctionsLR = clf.predict(testX)
        #fScoreLR = f1_score(testY, preditctionsLR, average=fScoreAverage)
        #reporteLR = classification_report(testY, preditctionsLR)
        #print(reporteLR)
        #modelos.append([clf,fScoreLR,reporteLR])
        ##EDER

    ml_model = None
    fScoreBest = 0
    #modelargs = 
    for modelo in modelos:
        if modelo[1] >= fScoreBest:
            ml_model = modelo
            fScoreBest = modelo[1]
    return ml_model
# TODO elegir el pico de coherencia mejor -> Esto lo razonamos viendo el gráfico ya que nos aparece uno muy bueni
# TODO fusionar clasificacion y clustering en crearModelo
# TODO predecir tanto clasificacion como clustering (de los negativos) en probarModelo
# TODO modificar preprocesado para tweet_cord de Ruben
def predecirRazones(pml_dataset):   #Clustering con LDA
    # Coger solo las columnas con texto (lenguaje natural)
    pml_dataset = pml_dataset[NLcolumns]
    #TODO:que pasa si el df tiene más de 1 columna? que pasa con el tolist?
    docs = pml_dataset.values.tolist()
    texts = [[word for word in document[0].lower().split()] for document in docs]
    diccionario= corpora.Dictionary(texts)
    corpus = [diccionario.doc2bow(text) for text in texts]
    modelos = []
    #array_coherencias = []
    for num_topics in range(1,21,1):
          #Un tópico (o tema) es un cjto de palabras que tienden a aparecer juntas
        lda_model = LdaModel(corpus=corpus,
                     id2word=diccionario,
                     num_topics=num_topics, 
                     random_state=42,
                     update_every=1,
                     chunksize=100,
                     passes=10,
                     alpha='auto',
                     per_word_topics=True)
        coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=diccionario, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        #array_coherencias.append(coherence_lda)
        modelos.append([lda_model, coherence_lda])
    mejorModelo = None
    mejorCoherencia = 0
    for modelo in modelos:
        lda_model = modelo[0]
        coherencia = modelo[1]
        # TODO calcular el mejor modelo con las coherencias
        if(mejorCoherencia < coherencia):
            mejorCoherencia = coherencia
            mejorModelo = lda_model
    lda_model = mejorModelo
    # Imprimir todos los topicos que tiene el modelo después de entrenarse con las 15 palabras más representativas
    topics_dict = {}
    for idx, topic in lda_model.print_topics(num_topics=num_topics, num_words=15):
        topics_dict[idx] = {}
        for prob_word in topic.split(" + "):
            prob = prob_word.split("*")[0]
            word = prob_word.split("*")[1].strip("\"")
            topics_dict[idx][word] = prob
    with open(airline+"_"+sentiment+"_topics_probs.json", "w") as outfile:
        json.dump(topics_dict, outfile)
        #print('Tópico: {} \nPalabras clave: {}\n'.format(idx, topic))
    """plt.rcParams["figure.figsize"] = [20, 1]
    plt.rcParams["figure.autolayout"] = True
    y = np.array(array_coherencias)
    x = np.sort(range(1,21,1))
    plt.xlabel("num_topics", size=12)
    plt.ylabel("coherence", size=12)
    plt.title("Line graph")
    plt.plot(x, y, color="red")
    plt.show()
    sys.exit(0)"""
    predicciones = []
    for doc in corpus:
        topic_probs = lda_model.get_document_topics(doc)
        predicciones.append(max(topic_probs, key=lambda x: x[1])[0])
    return lda_model, predicciones
    
if __name__ == '__main__':
    # Gestionar las senales de teclado durante la ejecucion
    signal.signal(signal.SIGINT, signal_handler)

    # Definir argumentos de entrada
    input_args = sys.argv[1:]
    short_opts = "f:e:t:hi:a:sr:o:m:n:v:x:c:"
    long_opts = ['file=', 'exclude=', 'target=', 'help', 'impute=', 'algorithm=', 'stats', 'rescale=', 'test-size=', 'random-state=', 'output=', 'natural-language=', 'vectorize=', 'switch=' 'clustering=']
    
    # Parsear los argumentos y sus valores
    try:
        # En options se guarda [opt,arg] por cada argumento
        # En reminder se guardan los argumentos sobrantes: -o 1 2 (options=['-o',1],reminder=[2])
        options,remainder = getopt.gnu_getopt(input_args,short_opts,long_opts)
    except getopt.GetoptError as err:
        print('[!] ERROR: The arguments given does not meet the requirements')
        helpPanel()
        sys.exit(1)
    
    # Cargar los valores de los argumentos de entrada
    for opt,arg in options:
        if opt in ('-f', '--file'):
            inputFile = arg
            if not os.path.exists(inputFile):
                print("[!] Error: El fichero de los datos de entrada no existe.")
                sys.exit(1)
        elif opt in ('-e', '--exclude'):
            excludedColumns = arg
        elif opt in ('-t', '--target'):
            targetColumn = arg
        elif opt in ('-h','--help'):
            helpPanel()
            exit(0)
        elif opt in ('-i', '--impute'):
            if arg.upper() in imputeOptions: # Comprobar que es MEAN, MEDIAN, MODE o CONSTANT
                imputeOption = arg.upper()
            elif not os.path.exists(arg): # Si es un fichero, comprobar que existe
                print("[!] Error: El metodo de imputacion no es correcto o el fichero no existe.")
                sys.exit(1)
        elif opt in ('-a', '--algorithm'):
            try:
                algorithm = int(arg)
            except:
                print('[!] The algorithm selection must be an integer')
                sys.exit(1)
                
            if algorithm >= len(algorithms) or algorithm < 0:
                print('[!] The algorithm selection is out of range, choose a valid one')
                sys.exit(1)
        elif opt in ('-v', '--vectorize'):
            NLtechnique = arg.lower()
            if NLtechnique != "bow" and NLtechnique != "tfidf":
                print('[!] The natural language tecnique must be "bow" or "tfidf", choose one of theese two options')
                sys.exit(1)
        elif opt in ('-s', '--stats'):
            printStats = True
        elif opt in ('-r', '--rescale'):
            if arg.upper() in rescaleOptions:
                rescaleOption = arg.upper()
            elif not os.path.exists(arg):
                print("[!] Error: El metodo de rescalado no es correcto o el fichero no existe.")
                sys.exit(1)
        elif opt == '--test-size':
            arg = str(arg)
            try:
                testSize = float(arg)
                if testSize <= 0 or testSize >= 1:
                    int('throw error')
            except:
                print('[!] The test size must be a float between 0.0 and 1.0')
                sys.exit(1)
        elif opt == '--random-state': #Random state se usa como semilla para separar train y test de la misma forma, sirve para que un experimento sea reproducible, si no se le da ningun valor, sera aleatorio
            arg = str(arg) #Convertirlo a string para comprobar correctamente si es un float o int
            try:
                #int(2) --> 2
                #int(str(2)) --> 2
                #int(1.2) --> 1
                #int(str(1.2)) --> error
                randomState = int(arg)
            except:
                print('[!] Random state must be an integer')
                sys.exit(1)
        elif opt in ('-o', '--output'):
            outputModelName = arg
        elif opt in ('-m', '--measure'):
            evaluation = arg
        elif opt in ('-x', '--switch'):
            switch = arg
            if switch == "on":
                switch = True
            elif switch == "off":
                switch = False
            else:
                print('[!] Switch must be "on" (translate emojis to natural language) or "off" (delete emojis)')
                sys.exit(0)
        elif opt in ('-n', '--natural-language'):
            NLcolumns = arg.split(",")
        elif opt in ('-c', '--clustering'):
            arg = str(arg).upper()
            if NLcolumns == None:
                print("[!] Debes especificar las columnas que tienen texto con el parametro -n")
                sys.exit(1)
            if arg == "T":
                clustering = True
            elif arg == "F":
                clustering == False
    
    # Comprobar que los argumentos de entrada requeridos se han especificado en la llamada
    comprobarArgumentosEntradaObligatorios()
    
    print("[*] Cargando el dataset...")
    # Cargar el fichero de datos en un dataset de pandas
    ml_dataset = cargarDataset(inputFile)
    print("[*] Preprocesando dataframe...")
    #print(f'{targetColumn}, {algorithms[algorithm]}, {excludedColumns}, {imputeOption}, {rescaleOption}')
    preprocessor = Preprocessor()
    ml_dataset_classification = ml_dataset[[targetColumn]+NLcolumns]
    ml_dataset_classification = preprocessor.preprocessDataset(ml_dataset_classification, targetColumn, algorithms[algorithm], excludedColumns, imputeOption, rescaleOption, NLcolumns, NLtechnique, "train", switch)
    ml_dataset_classification, target_map = preprocessor.convertTargetToClassifyInt(ml_dataset_classification, targetColumn)
    ml_dataset_clustering = preprocessor.preprocessEvolved(ml_dataset, targetColumn, excludedColumns, imputeOption, NLcolumns, NLtechnique, "train", switch, airline, sentiment)
    print("[*] Creando el modelo...")
    ml_model = crearModelo(ml_dataset_classification, algorithm, target_map)
    lda_model, topic_column = predecirRazones(ml_dataset_clustering)
    ml_dataset_clustering['topic'] = topic_column
    print()
    if printStats: #clf,fScore,reporte,{k: k, w: w, d: d}
        if len(ml_model) == 4:
            print('\n\tEstadisticas para el mejor modelo entrenado')
            print('\t-------------------------------------------')
            print()
            print(f'\tAlgotitmo = {algorithms[algorithm]}')
            for hyperparam in ml_model[3]:
                print(f'\t{hyperparam} = {ml_model[3][hyperparam]}')
            print()
            print(ml_model[2])
            print()
            print(f"\tClustering: {len(lda_model.print_topics())} topicos")
            print()
        
    if outputModelName != None:
        pickle.dump(ml_model[0], open(outputModelName+"_clf.pkl", 'wb'))
        pickle.dump(lda_model, open(outputModelName+"_lda.pkl", 'wb'))