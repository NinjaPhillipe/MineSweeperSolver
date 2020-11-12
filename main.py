import random
import copy

class Board:
    cases=[]
    size=None
    pBombs=None

    colKnow = '\033[1;36m'
    colUnKn = '\033[4m'
    reset = '\033[0;0m'
    colfringe = '\033[93m'
    colbomb = '\033[91m'

    # value of BOMB
    BOMB = -1

    def __init__(self,size,pBombs):
        self.size = size
        self.pBombs = pBombs
        if not (pBombs > 0.0 and pBombs < 1.0):
            print("ERROR : bombes propa invalid")
            exit(0)
        nBombs = int(size*size*pBombs)

        # init 
        for j in range(size):
            self.cases.append([])
            for _ in range(size):
                self.cases[j].append(0)

        # genere la liste des positions
        choosed = [ (x,y) for x in range(size) for y in range(size) ]
        random.shuffle(choosed)

        # pour chaque pose dans l interval        
        for (x,y) in choosed[:nBombs]:
            self.cases[y][x] = self.BOMB # -1 equals bombs

        # add numbers 
        for j in range(size):
            for i in range(size):
                if self.cases[j][i] != self.BOMB:
                    self.cases[j][i] = self.number_of_bombs(self.get_neight(j,i))

    def get_neight(self,_y,_x):
        """
            Retourne les voisins valide
        """
        return [(_y+i,_x+j) for i in [-1,0,1] for j in [-1,0,1] if not i==j==0 and 0<=_y+i and 0<=_x+j and _y+i<self.size and _x+j<self.size]

    def number_of_bombs(self,l):
        res = 0
        for (y,x) in l:
            if self.cases[y][x] == self.BOMB:
                res+=1
        return res 

    def click(self,_y,_x,knows):
        """
            Simule un click et rejoute dans knows ce qui a ete decouvert
        """

        if self.cases[_y][_x] == self.BOMB:
            print("BOOM YOU LOOSE")
            exit()

        # si n'est pas un zero
        if self.cases[_y][_x] != 0:
            knows[(_y,_x)] = self.cases[_y][_x]

        # si c'est un zero
        res = [(_y,_x)]
        a = [(_y,_x)]
        while len(a) > 0:
            (y,x) = a.pop()
            for (y2,x2) in self.get_neight(y,x):
                if not (y2,x2) in res :
                    res.append((y2,x2))
                    if self.cases[y2][x2] == 0:
                        a.append((y2,x2))


        for (j,i) in res:   
            knows[(j,i)] = self.cases[j][i]
        
           
    def is_valid_model(self,model,test,knows):
        # pour chaque case a tester 
        for (y,x) in test:
            nei = self.get_neight(y,x)
            # les vosins du model 
            res = 0
            for pos in nei:
                if model.get(pos) == True:
                    res+=1   
            # plus voisin deja connu
            if self.cases[y][x] != res+self.number_of_bombs([(j,i) for (j,i) in nei if knows.get( (j,i)) is not None ] ): 
                return False
        return True

    def enum_models(self,knows,test,unknow,model,models):
        if len(unknow) == 0:
            if self.is_valid_model(model,test,knows):
                models.append(copy.deepcopy(model))
        else:
            pos = unknow.pop()

            model[pos] = True
            self.enum_models(knows,test,unknow,model,models)
            model[pos] = False
            self.enum_models(knows,test,unknow,model,models)
            unknow.append(pos)

    def get_models(self,knows,test,unknow):
        model  = {}
        models = []

        self.enum_models(knows,test,unknow,model,models)
        return models

    def compute_proba(self,query,models,fringe):
        """
            /!\ query ne doit pas etre inclu a fringe
        """
        #  Bomb  NotBomb
        # [vrai ,  faux ]
        tmp = [0,0]
        # pour chaque model
        for model in models:
            tmp0 = 1
            tmp1 = 1
            for other in fringe:
                if query != other: # si different 
                    if model[query] == True:
                        if model[other] == True:
                            tmp0 *= self.pBombs
                        else:
                            tmp0 *= 1-self.pBombs
                    else:
                        if model[other] == True:
                            tmp1 *= self.pBombs
                        else:
                            tmp1 *= 1-self.pBombs
            tmp[0]+=tmp0
            tmp[1]+=tmp1
        tmp[0]*= self.pBombs
        tmp[1]*= 1-self.pBombs

        #normalize
        n = tmp[0]+tmp[1]
        # tmp[0] /=n
        # tmp[1] /=n

        return tmp[0]/n

    def get_fringe(self,knows):
        res = []
        for (j,i) in knows.keys():
            for p in self.get_neight(j,i):
                if knows.get(p) is None:
                    res.append(p)
        return res


    def logicaly(self,knows):
        """
            Applique un pretraitement des cases qui sont sure d'etre des bombes

            retourne vrai si qqch a changer et faux si rien a changer
            Notion de point fixe
        """
        res = False

        # find bombs
        toBomb = []
        for pos in knows.keys():
            if knows[pos] != 0:
                nbB = 0
                # pour chaque voisin
                for n in self.get_neight(pos[0],pos[1]):
                    if knows.get(n) == self.BOMB or knows.get(n) is None:
                        nbB+=1
                # si toutes les bombes sont decouvertes 
                if knows[pos] == nbB:
                    for n in self.get_neight(pos[0],pos[1]):
                        if knows.get(n) is None:
                            toBomb.append(n)
        for b in toBomb:        
            knows[b] = self.BOMB
            res = True

        # find safe 
        toFree = []
        for pos in knows.keys():
            if knows[pos] != 0:
                nbB = 0
                # pour chaque voisin
                for n in self.get_neight(pos[0],pos[1]):
                    if knows.get(n) == self.BOMB:
                        nbB+=1
                # si toutes les bombes sont decouvertes 
                if knows[pos] == nbB:
                    for n in self.get_neight(pos[0],pos[1]):
                        if knows.get(n) is None:
                            toFree.append(n)
        for (j,i) in toFree:
            self.click(j,i,knows)
            self.pretty_knows(knows)
            print()
            res = True
        return res 

    def proba_solve(self,knows,fringe):
        #Proba
        minPos = None
        minVal = None
        # pour chaque fringe
        for query in fringe:
            local_fringe = []
            local_test   = []
            # pour chaque voisin connu
            for p in self.get_neight(query[0],query[1]):
                # si n'est pas nul ni une bombe 
                if knows.get(p) is not None and knows[p] != self.BOMB :
                    local_test.append(p)
                    # pour chaque voisin dans le fringe
                    for n in self.get_neight(p[0],p[1]):
                        # ajoute au fringe local
                        if not n in local_fringe and n in fringe and n!=query: #empeche avoir fringe et query confondu
                            local_fringe.append(n)

            #generate model for the query
            local_fringe.append(query)
            models = self.get_models(knows,local_test,local_fringe)
            local_fringe.pop()

            # compute proba
            newProbVal = self.compute_proba(query,models,local_fringe)

            if minVal is None or newProbVal < minVal:
                minVal = newProbVal
                minPos = query

        self.click(minPos[0],minPos[1],knows)
        self.pretty_knows(knows)
        print()



    def resolve(self):
        y = random.randint(0,self.size-1)
        x = random.randint(0,self.size-1)

        # print("first (%d,%d) = %d" % (x,y,self.cases[y][x]) )

        knows = {}
        # init know
        self.click(y,x,knows)
        i = 0
        while True:
            i+=1
            print("it %d " % i)
            # tant qu on a pas atteint un point fixe
            res = self.logicaly(knows)
            while res:
                res = self.logicaly(knows)

            fringe = self.get_fringe(knows)

            # si plus de frontiere
            if len(fringe) == 0:
                break

            self.proba_solve(knows,fringe)

        self.pretty(knows,[])
        print()
        self.pretty_knows(knows)

    def pretty(self,knows,fringe):
        for j in range(self.size):
            for i in range(self.size):
                if knows.get( (j,i) ) is not None:
                    print(f"{self.colKnow}%3d {self.reset}" % self.cases[j][i],end=' ')
                elif (j,i) in fringe:
                    print(f"{self.colfringe}%3d {self.reset}" % self.cases[j][i],end=' ')
                else:
                    print(f"{self.colUnKn}%3d {self.reset}" % self.cases[j][i],end=' ')
            print()

    def pretty_knows(self,knows):
        for j in range(self.size):
            for i in range(self.size):
                r = knows.get((j,i))
                if r == None:
                    print(f"{self.colUnKn}%3s {self.reset}" % "",end=' ')
                else:
                    if r == self.BOMB:
                        print(f"{self.colbomb}%3s {self.reset}" % r,end=' ')
                    else:
                        print(f"{self.colKnow}%3s {self.reset}" % r,end=' ')

            print()
    def pretty_models(self,model):
        for j in range(self.size):
            for i in range(self.size):
                r = model.get((j,i))
                if r == None:
                    print(f"{self.colUnKn}%3s {self.reset}" % "",end=' ')
                elif r == True:
                    print(f"{self.colKnow}%3s {self.reset}" % "T",end=' ')
                elif r == False:
                    print(f"{self.colKnow}%3s {self.reset}" % "F",end=' ')

            print()



if __name__=="__main__":
    board = Board(15,0.2)
    board.resolve()