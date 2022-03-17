from queue import PriorityQueue
import numpy as np
import pandas as pd
import math

class State(object): #generica classe rappresentante uno stato in un grafo, con gli attributi presenti in ogni applicazione
    #di un searching problem su grafo

    def __init__(self, value, parent,
                 start=0,
                 goal=0):

        self.children = []
        self.parent = parent
        self.value = value
        self.dist_to_goal = 0
        self.dist_from_start = 0


        if parent:
            self.start = parent.start
            self.goal = parent.goal
            self.path = parent.path[:]
            self.path.append(value)
        else:
            self.path = [value]
            self.start = start
            self.goal = goal

    def GetDistanceToGoal(self):
        pass

    def GetDistanceFromStart(self):
        pass

    def CreateChildren(self):
        pass


class State_Conti(State):
    def __init__(self, value, parent, threshold,
                 start = 0,
                 goal = 0):

        super().__init__(value, parent, start, goal)
        #costruzione degli attributi specifici del caso in cui la ricerca è fatta tra lotti di righe di una fattura
        self.threshold = threshold
        self.ammontari_predizioni = self.value.groupby('Conto').sum().PrezzoTotale.to_dict() #nel caso di State_Conti
        #il valore di un nodo è rappresentato dalla n-upla con i conti associati alle varie righe, perciò value è un pd.df.
        #Però il goal è un dictionary in cui le keys sono i conti in prima nota e i valori sono gli ammontari associaiti,
        #dunque per confrontare lo stato col gol va trasformato in un dictionary con gli ammontati per conto.
        self.dist_from_start = self.GetDistanceFromStart()
        self.dist_to_goal = self.GetDistanceToGoal() #2 distanze perchè A* considera la somma della distanza percorsa e quella residua

    def GetDistanceToGoal(self): #nel caso specifico trattato è così che si calcola la distanza di uno stato dal goal: è l'euristica
        #che (sotto)stima il numero di passi necessari per raggiundere il goal.
        dist = 0
        for key in self.goal:
            if (key not in self.ammontari_predizioni.keys()) or (np.abs(self.goal[key] - self.ammontari_predizioni[key]) > self.threshold):
                dist += 1
        dist = math.ceil(dist / 2)
        return dist

    def GetDistanceFromStart(self):
        return len(self.path) - 1

    def CreateChildren(self): #nel caso specifico trattato è così che si generano i nodi figlio
        if not self.children:
            for i in range(self.value.shape[0]):
                for key in self.goal.keys():
                    value_child = self.value.copy(deep=True)
                    value_child.loc[i, 'Conto'] = key
                    child = State_Conti(value_child, self, self.threshold)
                    self.children.append(child)


class AStar_Solver: #è un solver di A* assolutamente generico che può essere usato con State o una sua sottoclasse; l'unica
    #cosa da rimuovere è la threshold nel caso in cui si lavori con stati che non ne necessitano come State_Conti
    def __init__(self, start, goal, threshold):
        self.path = []
        self.visitedQueue = []
        self.priorityQueue = PriorityQueue()
        self.start = start
        self.goal = goal
        self.threshold = threshold

    def Solve(self):
        startState = State_Conti(self.start,
                                  0,
                                  self.threshold,
                                  self.start,
                                  self.goal)

        count = 0 #serve per evitare di far proseguire la ricerca per troppo tempo nel caso in cui lo spazio sia veramente
        #ampio e non si raggiunga un goal dopo un tot di interazioni
        self.priorityQueue.put((0, count, startState))
        if not startState.dist_to_goal:
            self.path = startState.path
        while (not self.path and self.priorityQueue.qsize() and count < 5000):
            closestChild = self.priorityQueue.get()[2]
            closestChild.CreateChildren()
            self.visitedQueue.append(list(closestChild.value.Conto))

            for child in closestChild.children:
                if list(child.value.Conto) not in self.visitedQueue:
                    count += 1
                    if not child.dist_to_goal:
                        self.path = child.path
                        break
                    self.priorityQueue.put((child.dist_to_goal + child.dist_from_start, count, child))

        if not self.path:
            print("Goal of %s is not possible!" % (self.goal))

        return self.path

if __name__ == "__main__": #main function che raccoglie i dati dalle righe fatture e dalla prima nota e applica A* nel caso
    #specifico in cui la ricerca sia fatta nello spazio delle righe fatture (State_Conti)

    righe_tot = pd.read_excel('../pseudo_labels.xlsx')
    righe_tot = righe_tot.drop('Unnamed: 0', axis=1)
    prima_nota_tot = pd.read_excel('../df_row.xlsx')
    numeri_fattura = list(np.unique(righe_tot.Numero))
    to_remove = []

    for threshold in (0.005, 0.01, 0.02): #loop con threshold via via più tolleranti per dare all'inizio priorità a matching esatti
        numeri_fattura = set(numeri_fattura) - set(to_remove)
        to_remove = []
        for numero_fattura in numeri_fattura:
            righe = righe_tot[righe_tot['Numero'] == numero_fattura]
            righe.reset_index(inplace=True)
            righe = righe.drop('index', axis=1)

            #grouped1 = righe.groupby('Conto').sum()
            #print(grouped1)

            prima_nota = prima_nota_tot[prima_nota_tot['ND ori.'] == numero_fattura]
            prima_nota.reset_index(inplace=True)
            ammontari_prima_nota = prima_nota.loc[2:, ('Conto', 'Importo')]
            ammontari_prima_nota.set_index('Conto', inplace=True)
            ammontari_prima_nota = ammontari_prima_nota.Importo.to_dict()

            print(f'Starting {numero_fattura}')
            a = AStar_Solver(righe, ammontari_prima_nota, threshold=threshold)
            a.Solve()
            if a.path:
                righe_tot.loc[righe_tot['Numero'] == numero_fattura, 'ContoEsatto'] = a.path[-1]['Conto'].values
                print(f'Validata {numero_fattura}')
                to_remove.append(numero_fattura)

            #for i in range(len(a.path)):
            #    print("{0}) {1}".format(i, a.path[i]))
            #grouped2 = a.path[-1].groupby('Conto').sum()
            #print(grouped2)
        print(righe_tot.head(50))
    #righe_tot.to_excel('/Users/bernardopanichi/Desktop/pseudo_labels_validated.xlsx')

#le pseudo-labels sono ora validate col confronto con gli ammontari in prima nota. Quindi, a meno di casi rarissimi in cui
#diverse combinazioni di righe diano lo stesso ammontare, possono essere ritenute affidabili per il training.
