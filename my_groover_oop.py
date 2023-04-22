import numpy as np
from qiskit import Aer, assemble, transpile
from qiskit import QuantumCircuit,  ClassicalRegister, QuantumRegister
from qiskit.visualization import plot_histogram 
import math

class grovers_alg:

    def __init__(self, clauses_path:str, shots:int) -> None:
        self._shots = shots
        self._clauses_path = clauses_path
        self._clauses = self.FileRead()
        self.QubitsCounts()

    def CircuitSetup(self):

        self._init_gate = self.Init()
        self._oracle = self.Oracle()
        self._diffuser = self.Diffuser()    
    
    def Compute(self):
        self.CircuitSetup()
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


    def QubitsCounts(self):
        """
        Sets up amount of qubits required for oracle and diffuser
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

        amount[2] = amount[1]+amount[0]+1

        self._diffuser_qubits_count= amount[0]
        self._clause_qubits_count = amount[1]
        self._all_qubits_count = amount[2]

    def Init(self): #snazil jsem se najit objekt Gate v qiskit library, abych to hodil do type hintu, ale nenašel jsem to, proto to tu chybí 
        """
        Returns gate, which sets correct qubits into superposition and last qubits into |-> state
        """

        qc = QuantumCircuit(self._all_qubits_count)

        for qubit in range(self._diffuser_qubits_count):
            
            qc.h(qubit)
    
        qc.x(self._all_qubits_count-1)
        qc.h(self._all_qubits_count-1)

        self._init_gate_realization = qc
        
        init_gate = qc.to_gate()

        init_gate.name = "init"
        
        return init_gate

    def Oracle(self):
        
        """
        Makes oracle of grovers algorithm from clauses and respective amount of neccesary qubits
        Marks correct item(s)
        """


        qc = QuantumCircuit(self._all_qubits_count)

        for idx, clause in enumerate(self._clauses):

            qc.cx(clause[0], idx + self._clause_qubits_count)

            qc.cx(clause[1], idx + self._clause_qubits_count)
        
        qc.mct(list(range(self._diffuser_qubits_count, self._all_qubits_count-1)), self._all_qubits_count-1)
        
        for idx, clause in enumerate(self._clauses):

            qc.cx(clause[0], idx + self._clause_qubits_count)

            qc.cx(clause[1], idx + self._clause_qubits_count)

        self._oracle_gate_realization = qc    

        oracle_gate = qc.to_gate()

        oracle_gate.name = "oracle"
        
        return oracle_gate
    

    def Diffuser(self):
        """
        Diffuser amplifies probability of measuring marked items by oracle (or amplifies unmarked items - this depends on how many iterations of algorithm are done). Diffuser is built based on clauses.
        """

        qc = QuantumCircuit(self._diffuser_qubits_count)

        for i in range(self._diffuser_qubits_count-1):

            qc.h(i)
            qc.x(i)

        #qc.barrier(list(range(amount[0])))

        qc.z(self._diffuser_qubits_count-1)
        qc.mct(list(range(self._diffuser_qubits_count-1)), self._diffuser_qubits_count-1)
        qc.z(self._diffuser_qubits_count-1)

        #qc.barrier(list(range(amount[0])))

        for i in range(self._diffuser_qubits_count-1):

            qc.x(i)
            qc.h(i)

        self._diffuser_gate_realization = qc

        diffuser_gate = qc.to_gate()

        diffuser_gate.name = "diffuser"

        return diffuser_gate

    def Grovers(self) -> dict:
        """
        Runs grovers algorithm and returns counts of measured items
        """

        """
        Algorithm:
        1. Set correct qubits into superposition and last qubit into |-> state
        2. Run oracle for set up oracle part of grovers algorithm
        3. Run diffuser for set up diffuser part of grovers algorithm
        4. Measure diffuser qubits
        """


        iterations = int( np.arcsin(1 / np.sqrt( self._diffuser_qubits_count ) ) )
        #sometimes number of iterations can be near 0, in this case we increase it to 1 to make algorithm work

        if iterations == 0: iterations = 1
        
        init_qubits = list(range(self._all_qubits_count))
        
        oracle_qubits = list(range(self._all_qubits_count))
        
        diffuser_qubits = list(range(self._diffuser_qubits_count))

        qc = QuantumCircuit(self._all_qubits_count,self._diffuser_qubits_count)
        
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