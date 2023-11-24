def logged(function):
    def wrapper(*args,**kwargs):
        value = function(*args,**kwargs)
        with open('logfile.txt','a+') as f:

            fname= function.__name__
            print(f'{fname} 반환값은 {value}' )
            f.write(f'{fname} 반환값은 {value}' )

        return value

    return wrapper
@logged
async def add(x,y):
    return x+y

print(add(10,20))