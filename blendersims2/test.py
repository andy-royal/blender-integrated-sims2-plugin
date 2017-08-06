class myClass:
    myVar = "Hello world"
    
    @classmethod
    def dump(cls):
        print(cls.myVar)
        
myClass.dump()
