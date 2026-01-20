import os
import sys
import time

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Constantes -----------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Só vão ser alteradas dentro do desenvolvimento

SYMBOLS = ("X","O")
X = SYMBOLS[0]
O = SYMBOLS[1]

ALTER_ONLY_NONE = True # Flag que indica que só pode preencher uma célula que está vazia (Padrão = True)

FREE_PLAYER = False # Flag que indica que o símbolo da rodada é automático e troca a vez do jogador (False = automática, True = manual, Padrão = False)

# Constante do Reset
RESET_LIMIT = 7 # Desaparece no quinto round depois de ser colocado (Padrão = 4)

# Cores
PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

# Possíveis respostas
POSITIVE = ("s","y","yes","sim")
NEGATIVE = ("n","não","no")

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Exceções -------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

class SymbolException(Exception):
    def __init__(self, message=("Erro de Símbolo")):
        # Call the base class constructor with the parameters it needs
        super(SymbolException, self).__init__(message)

class NoVictoryException(Exception): # Exceção usada para detectar se não houve vitória
    def __init__(self, message=("Não venceu!")):
        # Call the base class constructor with the parameters it needs
        super(NoVictoryException, self).__init__(message)

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Funções auxiliares ---------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def typewriterPrint(message): # Um print lento com efeito de "máquina de escrever"
    for x in message:
        print(x, end='')
        sys.stdout.flush()
        time.sleep(0.1)
    print('\n', end='') # Pulando linha

def clear(): # Limpa o terminal
    os.system('cls' if os.name == 'nt' else 'clear')

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Outros ---------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def doNothing():
    pass

def doNothingForApproximately(seconds): # Um time.sleep() bem piorado
    # 1 ciclo quase é 1 segundo exato
    for i in range(seconds):
        i = 0
        while i < 16706910:
            pass
            i += 1

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Classes principais ---------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

class cell():
    # Atributos: symbol e duration
    def __init__(self): # def __init__(self,symbol = None):, usada quando podia informar de início qual símbolo iniciava, com symbol sendo opcional
        self.symbol = None
        self.duration = RESET_LIMIT # Rounds antes de voltar a None (Padrão = 4)

    # ---------------------------------------

    def print(self):
        if (self.symbol) == None:
            return("   ")
        else:
            return(" "+str(self.symbol)+" ")
        
    # ---------------------------------------
        
    def alter(self, symbol):
        if symbol in SYMBOLS:
            if ALTER_ONLY_NONE and self.symbol == None: # Só dá para marcar as células que estiverem vazias
                self.symbol = str(symbol)
                self.duration = RESET_LIMIT
            else:
                print(YELLOW+"Casa já marcada... selecione outra casa"+END)
        else:
            raise SymbolException()
        
    # ---------------------------------------
        
    def reset(self): # Não será chamada se RESET = False
        if self.symbol != None:
            self.duration -= 1 # Diminui 1
            #print(self.duration)
            if self.duration <= 0:
                self.symbol = None
                self.duration = RESET_LIMIT

    # ---------------------------------------

    def checkVictory(self, symbol):
        if self.symbol != symbol:
            #print("Sem vitória")
            raise NoVictoryException()

# ----------------------------------------------------------------------------------------------------------------------------------------------------

class line():
    # Atributos: cells e number (número da linha)
    def __init__(self, number):
        number = int(number)
        if number > 0 and number < 4: # De 1 a 3
            self.lineNumber = number
            self.cells = {}
            for i in range(0,3): # Três células, 0 a 2
                #print(str(i))
                self.cells[str(i)] = cell()

    # ---------------------------------------

    def print(self):
        #OBS: Os prints das células retornam strings
        return(f"{self.cells['0'].print()}/{self.cells['1'].print()}/{self.cells['2'].print()}")
    
    # ---------------------------------------
    
    def alter(self,cell,symbol):
        try:
            self.cells[str(cell)].alter(symbol)
        except KeyError:
            print(RED+"Célula informada incorreta - Por favor, informe um número inteiro entre 1 e 3"+END)
        except SymbolException:
            print(RED+"Símbolo informado incorreto"+END)

    # ---------------------------------------

    def reset(self):
        for cell in self.cells.values(): # Chama o Reset de todas as células
            cell.reset()

    # ---------------------------------------

    def checkLineVictory(self,symbol): # Checa vitória na horizontal, conferindo todas as células (volta exceção se der errada)
        for cell in self.cells.values():
            try:
                #print(cell.symbol)
                cell.checkVictory(symbol)
            except NoVictoryException:
                raise NoVictoryException()
            
    # ---------------------------------------
            
    def checkOtherVictories(self,symbol,position): # Checa vitória na vertical ou horizontal, de acordo com a posição informada como argumento
        try: 
            self.cells[str(position)].checkVictory(symbol) # Três células, 0 a 2
        except NoVictoryException:
            raise NoVictoryException()

# ----------------------------------------------------------------------------------------------------------------------------------------------------
    
class table():
    # Atributos: lines
    def __init__(self):
        self.lines = {}
        for i in range(1,4): # Três linhas, 1 a 3
            #print(str(i))
            self.lines[str(i)] = line(i)

    # ---------------------------------------

    def print(self):
        #OBS: Os prints das linhas retornam strings
        for line in self.lines.values():
            print('\t'+line.print())

    # ---------------------------------------

    def endGamePrint(self):
        #OBS: Os prints das linhas retornam strings
        finalPrint = ""
        for line in self.lines.values():
            finalPrint += ('\t'+line.print()+'\n')
        return finalPrint # Retorna a string invés de printa aqui mesmo porque é o game que sabe quem venceu
    
    # ---------------------------------------

    def alter(self,line,cell,symbol):
        try:
            self.lines[str(line)].alter(cell,symbol)
        except KeyError:
            print(RED+"Linha informada incorreta - Por favor, informe um número inteiro entre 1 e 3"+END)

    # ---------------------------------------

    def reset(self): # Chama o Reset de todas as linhas
        for line in self.lines.values():
            line.reset()

    # ---------------------------------------

    # Métodos que detectam a vitória
    def checkLineVictory(self,symbol): # Checa vitória na horizontal (As 3 linhas precisam retornar a exceção para dizer que não venceu)
        try:
            self.lines["1"].checkLineVictory(symbol)
        except NoVictoryException:
            try:
                self.lines["2"].checkLineVictory(symbol)
            except NoVictoryException:
                try:
                    self.lines["3"].checkLineVictory(symbol)
                except NoVictoryException:
                    raise NoVictoryException()
                else:
                    pass
            else:
                pass
        else:
            pass # Se uma linha sequer não retorna a exceção, é que venceu

    # ---------------------------------------

    def checkColumnVictory(self,symbol): # Checa vitória na vertical (Ex, linha 2, célula 1)
        try:
            self.lines["1"].checkOtherVictories(symbol,0) # Primeira coluna (células 0)
            self.lines["2"].checkOtherVictories(symbol,0)
            self.lines["3"].checkOtherVictories(symbol,0)
        except NoVictoryException:
            try:
                self.lines["1"].checkOtherVictories(symbol,1) # Segunda coluna (células 1)
                self.lines["2"].checkOtherVictories(symbol,1)
                self.lines["3"].checkOtherVictories(symbol,1)
            except NoVictoryException:
                try:
                    self.lines["1"].checkOtherVictories(symbol,2) # Terceira coluna (células 2)
                    self.lines["2"].checkOtherVictories(symbol,2)
                    self.lines["3"].checkOtherVictories(symbol,2)
                except NoVictoryException:
                    raise NoVictoryException()
                else:
                    pass
            else:
                pass
        else:
            pass # Se um conjunto de linhas (vulgo coluna) não retorna exceção, quer dizer que venceu

    # ---------------------------------------

    def checkDiagonalVictory(self,symbol):  # Checa vitória na diagonal (Ex, linha 1, célula 1)
        try:
            self.lines["1"].checkOtherVictories(symbol,0)
            self.lines["2"].checkOtherVictories(symbol,1)
            self.lines["3"].checkOtherVictories(symbol,2)
        except:
            raise NoVictoryException()
        else:
            pass # Todas tem que dar certo para indicar a vitória

    # ---------------------------------------

    def checkCounterDiagonalVictory(self,symbol):  # Checa vitória na diagonal invertida (Ex, linha 1, célula 3)
        try:
            self.lines["1"].checkOtherVictories(symbol,2)
            self.lines["2"].checkOtherVictories(symbol,1)
            self.lines["3"].checkOtherVictories(symbol,0)
        except:
            raise NoVictoryException()
        else:
            pass # Todas tem que dar certo para indicar a vitória

# ----------------------------------------------------------------------------------------------------------------------------------------------------

class game():
    # Atributos: mainTable e current_player
    def __init__(self,current_player = None):
        if current_player == None or current_player == X:
            self.current_player = X
        elif current_player == O:
            self.current_player = O
        self.mainTable = table()

    # ---------------------------------------

    def print(self): # Print usada para chamar o método que gera a tabela
        self.mainTable.print()

    # ---------------------------------------

    def endGamePrint(self,symbol): # Print usada para gerar a tabela após a vitória de um dos dois
        finalPrint = self.mainTable.endGamePrint()
        if symbol == O:
            loser = X
        else:
            loser = O
        for i in finalPrint: # Pega e printa cada caracter da string final separadamente
            if i == symbol:
                print(GREEN+i+END, end='') # Printa o símbolo vencedor em verde
            elif i == loser:
                print(RED+i+END, end='') # Printa o símbolo perdedor em vermelho
            else:
                print(i, end='') # Printa os demais normalmente

    # ---------------------------------------

    def change_player(self):
        # Inverte o jogador da rodada atual
        if self.current_player == X:
            self.current_player = O
        elif self.current_player == O:
            self.current_player = X

    # ---------------------------------------
    
    def round(self):
        # OBS: Informar valores errados faz com que o jogador atual perca o Round e a contagem do duration das células avance
        try:
            print("\n===================================================================================\n"
          "=================================== Tic Tac Toe ===================================\n"
          "===================================================================================")
            print(f"\n -Jogador atual: {self.current_player}")
            newLine = int(input("Informe uma linha:"))    # De 1 a 3
            newCell = int(input("Informe uma célula:"))-1 # De 1 a 3 (mas 0 a 2 no código)
            if FREE_PLAYER: # Se é pra informar o símbolo manualmente ou não
                newSymbol = input("Informe um símbolo")       # X ou O
            else:
                newSymbol = self.current_player
                self.change_player()
        except ValueError:
            print(RED+"Por favor, informe um valor válido!"+END)
        else:
            self.mainTable.alter(newLine,newCell,newSymbol)
            self.reset()
            if self.checkVictory(newSymbol):
                typewriterPrint(GREEN+f"{newSymbol} venceu!!!"+END) # Printando em verde
                self.endGamePrint(newSymbol) # Último Print (especial)
                exit()

    # ---------------------------------------

    def reset(self):
        if reset:
            self.mainTable.reset() # Checa se alguma célula chegou no limite

    # ---------------------------------------

    def checkVictory(self, symbol):
        # Precisa que todos retornem erro para indicar que não houve vitória
        # Basicamente, o jogo chama os métodos de checagem de vitória que a tabela tem
        try:
            self.mainTable.checkLineVictory(symbol)
        except NoVictoryException:
            try:
                self.mainTable.checkColumnVictory(symbol)
            except NoVictoryException:
                try:
                    self.mainTable.checkDiagonalVictory(symbol)
                except NoVictoryException:
                    try:
                        self.mainTable.checkCounterDiagonalVictory(symbol)
                    except NoVictoryException:
                        return False
                    else:
                        return True
                else:
                    return True
            else:
                return True
        else:
            return True

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Seção principal do código --------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------

def main(): # Função principal
    clear() # Limpa o terminal
    # ---------------------------------------
    gameMain = game()
    # ---------------------------------------
    global reset
    print("===================================================================================\n"
          "=================================== Tic Tac Toe ===================================\n"
          "===================================================================================")
    reset = input("\n\t-Reset ativado? (S/N)") # Flag que decide se vai haver reset das células com o passar das rodadas ou não
    # Loop para pegar o valor da flag
    while True:
        if reset.lower() in POSITIVE:
            reset = True
            break
        elif reset.lower() in NEGATIVE:
            reset = False
            break
        else:
            reset = input("\t"+YELLOW+"S ou N?"+END)
            continue
    print("\n",end="")
    # ---------------------------------------
    # Loop do game
    gameMain.print()
    while True:
        gameMain.round()
        gameMain.print()
    # ---------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(YELLOW+"Programa encerrado via terminal..."+END)

# ----------------------------------------------------------------------------------------------------------------------------------------------------
# Fim do código --------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------          