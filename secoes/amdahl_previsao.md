• Amdahl é uma previsão sob hipóteses, não uma garantia. Com f quase 1, ela prevê speedup praticamente igual a p.
• O modelo não inclui o custo novo das versões paralelas (jump-ahead do gerador, criação de threads, redução, comunicação MPI).
• A máquina tem 6 núcleos físicos e 12 lógicos (SMT). Acima de 6 workers, o ganho real tende a ser menor que o previsto. Isso é hipótese a testar com os dados, não conclusão.

n=  10000000  f=0.999787  p= 1  S(p)=1.0000
n=  10000000  f=0.999787  p= 2  S(p)=1.9996
n=  10000000  f=0.999787  p= 4  S(p)=3.9974
n=  10000000  f=0.999787  p= 6  S(p)=5.9936
n=  10000000  f=0.999787  p= 8  S(p)=7.9881
n=  10000000  f=0.999787  p=12  S(p)=11.9719
n=  50000000  f=0.999952  p= 1  S(p)=1.0000
n=  50000000  f=0.999952  p= 2  S(p)=1.9999
n=  50000000  f=0.999952  p= 4  S(p)=3.9994
n=  50000000  f=0.999952  p= 6  S(p)=5.9986
n=  50000000  f=0.999952  p= 8  S(p)=7.9973
n=  50000000  f=0.999952  p=12  S(p)=11.9937
n= 100000000  f=0.999979  p= 1  S(p)=1.0000
n= 100000000  f=0.999979  p= 2  S(p)=2.0000
n= 100000000  f=0.999979  p= 4  S(p)=3.9997
n= 100000000  f=0.999979  p= 6  S(p)=5.9994
n= 100000000  f=0.999979  p= 8  S(p)=7.9988
n= 100000000  f=0.999979  p=12  S(p)=11.9972