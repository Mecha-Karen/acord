def testfunc(hi,bye,*all):
  print(hi + "\n" + bye)
  allr = ""
  for i in all:
    if i != all[-1]:
      allr += i + " "
    else:
      allr += i
  
    
  print(allr)

args = ["hi","adios","all","all","mine"]
print(str(type(testfunc)))