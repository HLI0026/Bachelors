## Bachelors

Toto repo obsahuje věci k bakalářské práci a do předmětu VVP

Samotná implementace groverova algoritmu se nachází v my_grover.py.

V tomto souboru se nachází funkce Grovers, která bere za argument podmínky sudoku a počet realizací obvodu.

Číslice označují jednotlivé bity. Podmínky jsou předány pomocí číslic jednotlivých bitů, mezi kterými by měl proběhnout XOR. 

Funkční pouze na 4 bitech, kde je zadaný počet podmínek roven 4. Případně na 2x větším obvodu, který je součástí examples.

# BP

TODO

# VVP

V examples najdeme využití groverova algoritmu na jednoduchých sudoku. Podmínky těchto pseudosudoku generujeme ve stejném souboru.

Více o groverově algoritmu se jde dočíst na:

https://qiskit.org/textbook/ch-algorithms/grover.html#3qubits
