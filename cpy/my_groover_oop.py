import numpy as np
from qiskit import Aer, assemble, transpile
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram 

class grovers_alg:

    def __init__(self, clauses_path:str, shots:int) -> None:
        self._shots = shots
        self._clauses_path = clauses_path
        self._clauses = self.FileRead()
        self._amount = self.QubitsCounts()
        self._init_gate = self.Init()
        self._oracle = self.Oracle()
        self._diffuser = self.Diffuser()
        self._counts = self.Grovers()


    def FileRead(self) -> list:
        """
        Reading file, transfering from string to list of lists, which contain single clauses
        """
        clauses = ""

        my_file = open(self._clauses_path, "rt")
        
        #reading file
        
        for line in my_file:
            
            clauses += line
        
        clauses = clauses.rsplit()

        #From string to list
        
        for idx, clause in enumerate(clauses):
            
            clauses[idx] = clause.split(",")
            
            clauses[idx][0] = int(clauses[idx][0])
            clauses[idx][1] = int(clauses[idx][1])

        my_file.close()

        return clauses


    def QubitsCounts(self) -> list:
        """
        Returns amount of qubits required for oracle and diffuser
        amount[0] contains diffuser quibts, amount[1] contains additional qubits for clause realisation, amount[2] number of all qubits needed
        """
        amount = [0, 0, 0]
        
        for cl1, cl2 in self._clauses:
            
            if amount[0]<cl1:
                
                amount[0] = cl1
            
            if amount[0]<cl2:
            
                amount[0] = cl2
        
        #due to 0 indexing of python we need to add 1 to diffuser qubits

        amount[0] +=1

        amount[1] = len(self._clauses)

        amount[2] = qubits_init = amount[1]+amount[0]+1

        return amount

    def Init(self):
        """
        Returns gate, which sets correct qubits into superposition and last qubits into |-> state
        """

        qc = QuantumCircuit(self._amount[2])

        for qubit in range(self._amount[0]):
            
            qc.h(qubit)
    
        qc.x(self._amount[2]-1)
        qc.h(self._amount[2]-1)
        
        init_gate = qc.to_gate()

        init_gate.name = "init"
        
        return init_gate

    def Oracle(self):
        
        """
        Makes oracle of grovers algorithm from clauses and respective amount of neccesary qubits
        Marks correct item(s)
        """


        qc = QuantumCircuit(self._amount[2])

        for idx, clause in enumerate(self._clauses):

            qc.cx(clause[0], idx + self._amount[1])

            qc.cx(clause[1], idx + self._amount[1])
        
        qc.mct(list(range(self._amount[0],self._amount[2]-1)), self._amount[2]-1)
        
        for idx, clause in enumerate(self._clauses):

            qc.cx(clause[0], idx + self._amount[1])

            qc.cx(clause[1], idx + self._amount[1])

        oracle_gate = qc.to_gate()

        oracle_gate.name = "oracle"
        
        return oracle_gate
    

    def Diffuser(self):

        """
        Diffuser amplifies probability of measuring marked items by oracle (or amplifies unmarked items - this depends on how many iterations of algorithm are done)
        """

        qc = QuantumCircuit(self._amount[0])

        for i in range(self._amount[0]-1):

            qc.h(i)
            qc.x(i)

        #qc.barrier(list(range(amount[0])))

        qc.z(self._amount[0]-1)
        qc.mct(list(range(self._amount[0]-1)), self._amount[0]-1)
        qc.z(self._amount[0]-1)

        #qc.barrier(list(range(amount[0])))

        for i in range(self._amount[0]-1):

            qc.x(i)
            qc.h(i)

        diffuser_gate = qc.to_gate()

        diffuser_gate.name = "diffuser"

        return diffuser_gate

    def Grovers(self):
        
        iterations = ( np.arcsin(1 / np.sqrt( self._amount[0] ) ) )
        iterations = iterations.ceil()
        #sometimes number of iterations can be near 0, in this case we increase it to 1 to make algorithm work

        if iterations == 0: iterations = 1
        
        init_qubits = list(range(self._amount[2]))
        
        oracle_qubits = list(range(self._amount[2]))
        
        diffuser_qubits = list(range(self._amount[0]))

        qc = QuantumCircuit(self._amount[2],self._amount[0])
        
        qc.append(self._init_gate,init_qubits)

        for i in range(iterations):
                
            qc.append(self._oracle,oracle_qubits)
            
            qc.append(self._diffuser, diffuser_qubits)
        
    
        qc.measure(diffuser_qubits,diffuser_qubits)

        aer_sim = Aer.get_backend('aer_simulator')
        
        trans_circ = transpile(qc, aer_sim)
        
        assembled = assemble(trans_circ,shots=self._shots)
        
        results = aer_sim.run(assembled).result()
        
        counts = results.get_counts()

        return counts

    def my_plot(self,f_name:str):
        
        plot_histogram(self._counts,filename = f_name)
